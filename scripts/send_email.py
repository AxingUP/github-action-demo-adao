#!/usr/bin/env python3
"""
邮件发送模块
用于发送 AI 资讯报告邮件
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr, formatdate
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器类"""

    def __init__(self):
        """从环境变量加载配置"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.email_from = os.getenv('EMAIL_FROM', self.smtp_username)
        # 支持多个收件人，用逗号分隔，并去除前后空格
        email_to_str = os.getenv('EMAIL_TO', '')
        self.email_to = [email.strip() for email in email_to_str.split(',') if email.strip()]
        self.use_tls = os.getenv('USE_TLS', 'true').lower() == 'true'

        # 验证配置
        if not self.smtp_username:
            raise ValueError("缺少 SMTP_USERNAME 环境变量")
        if not self.smtp_password:
            raise ValueError("缺少 SMTP_PASSWORD 环境变量")
        if not self.email_to:
            raise ValueError("缺少 EMAIL_TO 环境变量（至少需要一个收件人邮箱）")

    def create_email(
        self,
        subject: str,
        html_content: str,
        plain_content: str = None,
        attachments: list = None
    ) -> MIMEMultipart:
        """
        创建邮件对象

        Args:
            subject: 邮件主题
            html_content: HTML 格式内容
            plain_content: 纯文本内容（可选）
            attachments: 附件路径列表（可选）

        Returns:
            MIMEMultipart 邮件对象
        """
        # 创建邮件对象
        msg = MIMEMultipart('alternative')

        # 设置邮件头
        msg['Subject'] = subject
        msg['From'] = formataddr(('AI 资讯机器人', self.email_from))
        msg['To'] = ', '.join(self.email_to)
        msg['Date'] = formatdate(localtime=True)

        # 添加纯文本内容
        if plain_content:
            text_part = MIMEText(plain_content, 'plain', 'utf-8')
            msg.attach(text_part)

        # 添加 HTML 内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        # 添加附件
        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    self._add_attachment(msg, filepath)
                else:
                    logger.warning(f"附件不存在: {filepath}")

        return msg

    def _add_attachment(self, msg: MIMEMultipart, filepath: str):
        """
        添加附件到邮件

        Args:
            msg: 邮件对象
            filepath: 文件路径
        """
        filename = os.path.basename(filepath)

        with open(filepath, 'rb') as f:
            part = MIMEApplication(f.read(), Name=filename)

        # 设置附件头
        part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(part)
        logger.info(f"已添加附件: {filename}")

    def send(self, msg: MIMEMultipart) -> bool:
        """
        发送邮件

        Args:
            msg: 邮件对象

        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info(f"正在连接 SMTP 服务器: {self.smtp_host}:{self.smtp_port}")

            # 创建 SMTP 连接
            if self.smtp_port == 465:
                # SSL 连接
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                # TLS 连接
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            # 登录
            logger.info(f"使用用户名登录: {self.smtp_username}")
            server.login(self.smtp_username, self.smtp_password)

            # 发送邮件
            logger.info(f"发送邮件到: {', '.join(self.email_to)}")
            server.send_message(msg)

            # 关闭连接
            server.quit()

            logger.info("邮件发送成功！")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP 认证失败: {e}")
            logger.error("请检查用户名和密码（或应用专用密码）")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"发送邮件时发生错误: {e}")
            return False


def create_html_email_content(markdown_file: str) -> tuple:
    """
    将 Markdown 文件转换为 HTML 邮件内容

    Args:
        markdown_file: Markdown 文件路径

    Returns:
        tuple: (html_content, plain_content)
    """
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单的 Markdown 到 HTML 转换
        html_lines = []
        in_code_block = False
        in_list = False

        for line in content.split('\n'):
            # 处理空行
            if not line.strip():
                html_lines.append('<br/>')
                continue

            # 代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    html_lines.append('<pre><code>')
                else:
                    html_lines.append('</code></pre>')
                continue

            if in_code_block:
                html_lines.append(f'{line}<br/>')
                continue

            # 标题
            if line.startswith('# '):
                html_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('#### '):
                html_lines.append(f'<h4>{line[5:]}</h4>')

            # 引用块（> 开头的内容）
            elif line.startswith('>'):
                text = line[1:].strip()
                if text.startswith('> '):
                    # 多行引用
                    text = text[1:].strip()
                html_lines.append(f'<blockquote>{text}</blockquote>')

            # 分隔线
            elif line.strip() == '---':
                html_lines.append('<hr/>')

            # 链接
            elif '[' in line and '](' in line:
                import re
                # 转换 Markdown 链接为 HTML
                pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                html_line = re.sub(pattern, r'<a href="\2" target="_blank">\1</a>', line)
                html_lines.append(f'<p>{html_line}</p>')

            # 列表
            elif line.strip().startswith('- '):
                text = line.strip()[2:]
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{text}</li>')

            # 加粗文本
            elif '**' in line and line.count('**') >= 2:
                import re
                # 简单的加粗转换
                html_line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
                html_lines.append(f'<p>{html_line}</p>')

            # 其他文本
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p>{line}</p>')

        if in_list:
            html_lines.append('</ul>')

        # 添加 CSS 样式
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Microsoft YaHei', sans-serif;
            line-height: 1.7;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 20px;
            font-size: 28px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 24px;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
            margin-bottom: 10px;
            font-size: 20px;
        }}
        h4 {{
            color: #666;
            margin-top: 20px;
            margin-bottom: 8px;
            font-size: 16px;
        }}
        p {{
            margin: 10px 0;
            line-height: 1.7;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
            color: #2980b9;
        }}
        strong {{
            color: #2c3e50;
            font-weight: 600;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 15px;
            color: #666;
            background-color: #f0f7fc;
            border-radius: 0 4px 4px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 25px 0;
        }}
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
        }}
        code {{
            font-family: 'Courier New', Consolas, 'Monaco', monospace;
        }}
        ul {{
            padding-left: 25px;
            margin: 10px 0;
        }}
        li {{
            margin: 8px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #95a5a6;
            font-size: 14px;
            text-align: center;
        }}
        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            h1 {{ font-size: 24px; }}
            h2 {{ font-size: 20px; }}
            h3 {{ font-size: 18px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {''.join(html_lines)}
        <div class="footer">
            <p>本邮件由 AI 资讯自动生成系统发送</p>
            <p>如需取消订阅，请联系系统管理员</p>
        </div>
    </div>
</body>
</html>
        """

        return html_content, content

    except Exception as e:
        logger.error(f"读取 Markdown 文件失败: {e}")
        return "", ""


def send_news_email(markdown_file: str) -> bool:
    """
    发送 AI 资讯邮件

    Args:
        markdown_file: Markdown 文件路径

    Returns:
        bool: 发送是否成功
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(markdown_file):
            logger.error(f"文件不存在: {markdown_file}")
            return False

        # 创建邮件发送器
        sender = EmailSender()

        # 生成邮件内容
        filename = os.path.basename(markdown_file)
        date_str = filename.replace('ai_news_', '').replace('.md', '')
        subject = f"AI 资讯日报 - {date_str}"

        logger.info(f"正在发送邮件: {subject}")

        # 创建 HTML 内容
        html_content, plain_content = create_html_email_content(markdown_file)

        if not html_content:
            logger.error("无法生成邮件内容")
            return False

        # 创建邮件
        msg = sender.create_email(
            subject=subject,
            html_content=html_content,
            plain_content=plain_content,
            attachments=[markdown_file]  # 附加原 Markdown 文件
        )

        # 发送邮件
        success = sender.send(msg)

        return success

    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        logger.error("请指定要发送的 Markdown 文件路径")
        sys.exit(1)

    markdown_file = sys.argv[1]

    if not os.path.exists(markdown_file):
        logger.error(f"文件不存在: {markdown_file}")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("开始发送邮件")
    logger.info("=" * 60)

    success = send_news_email(markdown_file)

    if success:
        logger.info("=" * 60)
        logger.info("邮件发送成功")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("邮件发送失败")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
