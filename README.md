# github-action-demo-adao
自动化获取AI相关的咨询信息
● GitHub Actions AI 资讯获取工作流 - 开发步骤

第一步：确定数据源和获取方式

1. 研究 AI 资讯源                                                                                                                                                                   
   - 选择合适的 AI 资讯网站（如：OpenAI Blog、Google AI Blog、Hacker News AI、MIT Technology Review AI 栏目等）                                                                      
   - 确认网站是否有公开 API 或 RSS 订阅源                                                                                                                                            
   - 如果没有 API，评估网页抓取的可行性和法律合规性
2. 选择获取方案                                                                                                                                                                     
   - 方案 A：使用 RSS/API（推荐，更稳定）
  ---                                                                                                                                                                                 
第二步：创建项目目录结构

1. 创建 GitHub Actions 工作流目录                                                                                                                                                   
   .github/workflows/
2. 创建脚本目录（存放获取资讯的代码）                                                                                                                                               
   scripts/
3. 创建配置目录（存放配置文件）                                                                                                                                                     
   config/

  ---                                                                                                                                                                                 
第三步：设计并编写 GitHub Actions 工作流文件

1. 创建工作流文件：.github/workflows/fetch-ai-news.yml
2. 配置工作流基本参数                                                                                                                                                               
   - name: 工作流名称                                                                                                                                                                
   - on:
    - 定时触发：cron 表达式（每天 7:00 UTC 或北京时间）
    - 手动触发：workflow_dispatch（方便测试）                                                                                                                                       
      - jobs: 定义任务
3. 配置任务步骤                                                                                                                                                                     
   - 步骤1：检出代码                                                                                                                                                                 
   - 步骤2：设置运行环境（Node.js/Python/Go 等）                                                                                                                                     
   - 步骤3：安装依赖                                                                                                                                                                 
   - 步骤4：运行资讯获取脚本                                                                                                                                                         
   - 步骤5：处理结果（保存文件/发送通知）

  ---                                                                                                                                                                                 
第四步：编写资讯获取脚本

1. 选择编程语言                                                                                                                                                                     
   - Python
2. 实现核心功能                                                                                                                                                                     
   - 获取过去24小时的时间范围                                                                                                                                                        
   - 从配置的数据源获取资讯                                                                                                                                                          
   - 过滤时间范围内的内容                                                                                                                                                            
   - 按关键词筛选 AI 相关内容                                                                                                                                                        
   - 格式化输出（Markdown/JSON）
3. 添加错误处理                                                                                                                                                                     
   - 网络请求失败处理                                                                                                                                                                
   - 数据格式校验                                                                                                                                                                    
   - 日志记录

  ---                                                                                                                                                                                 
第五步：创建配置文件

1. 创建 config/sources.json                                                                                                                                                         
   - 列出所有资讯源（RSS URL、API 端点等）
2. 创建 config/keywords.txt                                                                                                                                                         
   - 定义 AI 相关关键词列表（AI、Artificial Intelligence、Machine Learning、LLM、GPT 等）
3. 创建环境变量配置说明                                                                                                                                                             
   - 需要在 GitHub Secrets 中配置的变量                                                                                                                                              
   - 可选：API 密钥、通知 Webhook URL 等

  ---                                                                                                                                                                                 
第六步：设计输出和通知机制

1. 输出方式选择                                                                                                                                                                     
   - 保存到仓库（创建每日日志文件）                                                                                                                                                  
   - 发布为 GitHub Release                                                                                                                                                           
   - 发送到通知渠道
2. 通知渠道选择                                                                                                                                                                      
   - 邮件通知
3. 实现通知脚本                                                                                                                                                                     
   - 整理筛选后的资讯                                                                                                                                                                
   - 格式化消息                                                                                                                                                                      
   - 发送通知

  ---                                                                                                                                                                                 
第七步：创建依赖文件

1. 根据选择的编程语言创建依赖文件                                                                                                                                                   
   - Python：requirements.txt                                                                                                                                                        
   - Node.js：package.json
2. 列出所需依赖包

  ---                                                                                                                                                                                 
第八步：本地测试和调试

1. 手动运行脚本                                                                                                                                                                     
   - 验证数据获取逻辑                                                                                                                                                                
   - 检查输出格式
2. 测试 GitHub Actions                                                                                                                                                              
   - 推送到测试分支                                                                                                                                                                  
   - 使用 workflow_dispatch 手动触发                                                                                                                                                 
   - 查看运行日志

  ---                                                                                                                                                                                 
第九步：文档更新

1. 更新 README.md                                                                                                                                                                   
   - 添加项目说明                                                                                                                                                                    
   - 使用指南                                                                                                                                                                        
   - 配置步骤                                                                                                                                                                        
   - GitHub Secrets 配置说明
2. 添加其他文档                                                                                                                                                                     
   - 贡献指南（可选）                                                                                                                                                                
   - 数据源说明（可选）

  ---                                                                                                                                                                                 
第十步：推送到 GitHub 并启用

1. 提交代码到仓库
2. 配置 GitHub Secrets                                                                                                                                                              
   - 如果需要，配置 API 密钥、Webhook URL 等
3. 启用 Actions                                                                                                                                                                     
   - 确认仓库启用了 GitHub Actions                                                                                                                                                   
   - 验证工作流配置
4. 监控首次运行                                                                                                                                                                     
   - 观察定时触发是否正常                                                                                                                                                            
   - 检查输出结果                                                                                                                                                                    
   - 根据需要调整

  --- 