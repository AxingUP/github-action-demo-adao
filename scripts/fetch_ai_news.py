#!/usr/bin/env python3
"""
AI 资讯获取脚本
获取过去24小时内的 AI 相关资讯
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from deep_translator import GoogleTranslator
import os
import sys
import re

# 配置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
SOURCES_FILE = os.path.join(CONFIG_DIR, 'sources.json')
KEYWORDS_FILE = os.path.join(CONFIG_DIR, 'keywords.txt')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'ai_news')


def load_config():
    """加载配置文件"""
    with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
        sources_data = json.load(f)

    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    return sources_data, keywords


def get_time_range():
    """获取过去24小时的时间范围"""
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    return yesterday, now


def contains_keyword(text, keywords):
    """检查文本是否包含任意关键词"""
    if not text:
        return False

    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False


def fetch_rss_feed(source_url):
    """获取 RSS feed"""
    try:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed
    except requests.RequestException as e:
        print(f"[ERROR] 获取 RSS 失败 ({source_url}): {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 解析 RSS 失败 ({source_url}): {e}")
        return None


def is_within_24_hours(pub_date, yesterday, now):
    """检查发布时间是否在24小时内"""
    try:
        if not pub_date:
            return False

        pub_dt = date_parser.parse(pub_date)

        # 处理时区问题，转换为 UTC
        if pub_dt.tzinfo:
            pub_dt = pub_dt.utctimetuple()
            pub_dt = datetime(pub_dt.tm_year, pub_dt.tm_mon, pub_dt.tm_mday,
                             pub_dt.tm_hour, pub_dt.tm_min, pub_dt.tm_sec)

        return yesterday <= pub_dt <= now
    except Exception as e:
        print(f"[WARN] 解析日期失败: {pub_date}, 错误: {e}")
        return False


def translate_to_chinese(text):
    """将文本翻译成中文"""
    if not text or not text.strip():
        return text

    # 移除 HTML 标签
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = ' '.join(clean_text.split())

    if not clean_text or len(clean_text) < 2:
        return text

    # 限制翻译长度，避免超时
    if len(clean_text) > 1000:
        clean_text = clean_text[:1000] + '...'

    try:
        translator = GoogleTranslator(source='auto', target='zh-CN')
        translated = translator.translate(clean_text)
        return translated
    except Exception as e:
        print(f"[WARN] 翻译失败: {e}")
        return text  # 翻译失败则返回原文


def fetch_ai_news(sources_data, keywords, yesterday, now):
    """获取 AI 资讯"""
    all_news = []

    for source in sources_data['sources']:
        if not source.get('enabled', True):
            continue

        print(f"[INFO] 正在获取: {source['name']}")

        feed = fetch_rss_feed(source['url'])
        if not feed or not feed.entries:
            print(f"[WARN] 无法获取 {source['name']} 的内容或内容为空")
            continue

        for entry in feed.entries:
            pub_date = entry.get('published') or entry.get('updated')

            if not is_within_24_hours(pub_date, yesterday, now):
                continue

            title = entry.get('title', '')
            description = entry.get('description', '') or entry.get('summary', '')
            link = entry.get('link', '')

            # 检查标题和描述是否包含 AI 相关关键词
            if contains_keyword(title + ' ' + description, keywords):
                news_item = {
                    'source': source['name'],
                    'title': title,
                    'link': link,
                    'description': description,
                    'published': pub_date
                }
                all_news.append(news_item)

        print(f"[INFO] {source['name']} 获取完成，找到 {len([n for n in all_news if n['source'] == source['name']])} 条资讯")

    return all_news


def format_news_to_markdown(news_list, yesterday, now):
    """将资讯格式化为 Markdown，包含中文翻译"""
    date_str = now.strftime('%Y-%m-%d')
    markdown = f"""# AI 资讯日报 - {date_str}

> 本报告涵盖时间段: {yesterday.strftime('%Y-%m-%d %H:%M UTC')} 至 {now.strftime('%Y-%m-%d %H:%M UTC')}
>
> 生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 摘要

共找到 **{len(news_list)}** 条 AI 相关资讯

---

## 资讯详情

"""

    # 按来源分组
    from collections import defaultdict
    news_by_source = defaultdict(list)
    for news in news_list:
        news_by_source[news['source']].append(news)

    # 按来源输出
    for source, items in news_by_source.items():
        markdown += f"\n### {source}\n\n"
        for i, news in enumerate(items, 1):
            # 翻译标题
            title_cn = translate_to_chinese(news['title'])

            markdown += f"#### {i}. {news['title']}\n\n"
            if title_cn and title_cn != news['title']:
                markdown += f"**标题（中文）**: {title_cn}\n\n"

            markdown += f"- **链接**: {news['link']}\n"
            if news['published']:
                markdown += f"- **发布时间**: {news['published']}\n"
            markdown += f"\n"

            # 清理 HTML 标签并翻译摘要
            clean_desc = re.sub(r'<[^>]+>', '', news['description'])
            clean_desc = ' '.join(clean_desc.split())  # 去除多余空格
            if clean_desc and len(clean_desc) > 50:
                desc_en = clean_desc[:500] + ('...' if len(clean_desc) > 500 else '')
                markdown += f"**摘要（英文）**: {desc_en}\n\n"

                # 翻译摘要
                desc_cn = translate_to_chinese(clean_desc[:500])
                if desc_cn and desc_cn != clean_desc[:500]:
                    markdown += f"**摘要（中文）**: {desc_cn}\n\n"

            markdown += "---\n\n"

    markdown += f"""
## 说明

本报告由 GitHub Actions 自动生成，通过抓取多个 AI 相关资讯源并筛选过去 24 小时内包含 AI 相关关键词的内容生成。

**数据源**:
- OpenAI Blog
- Google AI Blog
- MIT Technology Review
- Hacker News AI
- The Verge AI

**关键词数量**: {len(news_list)}

---
*Powered by github-action-demo-adao*
"""

    return markdown


def save_output(markdown_content, date_str):
    """保存输出文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = f"ai_news_{date_str}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"[INFO] 资讯报告已保存到: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("AI 资讯获取脚本启动")
    print("=" * 60)

    # 加载配置
    print("\n[INFO] 加载配置文件...")
    try:
        sources_data, keywords = load_config()
        print(f"[INFO] 加载了 {len(sources_data['sources'])} 个资讯源")
        print(f"[INFO] 加载了 {len(keywords)} 个关键词")
    except FileNotFoundError as e:
        print(f"[ERROR] 配置文件未找到: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败: {e}")
        sys.exit(1)

    # 获取时间范围
    yesterday, now = get_time_range()
    print(f"\n[INFO] 查询时间范围: {yesterday} 至 {now}")

    # 获取资讯
    print("\n[INFO] 开始获取资讯...")
    news_list = fetch_ai_news(sources_data, keywords, yesterday, now)

    # 格式化输出
    print(f"\n[INFO] 共找到 {len(news_list)} 条 AI 相关资讯")
    if not news_list:
        print("[WARN] 未找到符合条件的内容")
        markdown_content = format_news_to_markdown(news_list, yesterday, now)
    else:
        markdown_content = format_news_to_markdown(news_list, yesterday, now)

    # 保存文件
    date_str = now.strftime('%Y-%m-%d')
    output_file = save_output(markdown_content, date_str)

    print("\n" + "=" * 60)
    print("AI 资讯获取脚本执行完成")
    print("=" * 60)

    # 发送邮件通知
    if os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'):
        print("\n[INFO] 正在发送邮件通知...")
        try:
            from send_email import send_news_email
            if send_news_email(output_file):
                print("[INFO] 邮件发送成功")
            else:
                print("[WARN] 邮件发送失败")
        except Exception as e:
            print(f"[ERROR] 邮件发送出错: {e}")

    return output_file


if __name__ == '__main__':
    main()
