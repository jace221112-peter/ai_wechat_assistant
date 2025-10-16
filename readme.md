\# 🤖 企业微信智能体客服系统（AI WeChat Assistant Bot）



> 基于 \*\*LangChain + DeepSeek + FastAPI\*\* 构建的智能客服系统，  

> 支持 \*\*知识库热加载、会话记忆、多格式文档识别（含 WPS）、本地部署运行\*\*，  

> 让 AI 成为企业的知识中枢与客户沟通桥梁。



---



\## 🌟 项目简介



在企业客服体系中，大量重复性问答浪费了人工时间，也导致客户等待体验下降。  

本项目将 \*\*LangChain\*\* 的语义检索与 \*\*DeepSeek API\*\* 的生成能力结合，通过 \*\*FastAPI\*\* 提供标准接口，打造一个\*\*可持续学习、自我进化\*\*的智能客服大脑。



📌 项目核心特性：

\- 💬 自动回复企业微信客户：通过 Webhook 接口与工作流对接

\- 🧠 知识增强问答（RAG）：LangChain + ChromaDB + bge-m3 中文嵌入模型

\- 📂 支持多格式文档：自动识别 `.txt / .pdf / .docx / .pptx / .xlsx / .wps`

\- 🔁 实时热加载机制：监控知识库文件夹变更，自动重建向量数据库

\- 🧩 多轮会话记忆：每个 session 独立记忆上下文

\- 🎭 可定制 AI 人设：通过 `.env` 设置客服语气与角色

\- ⚙️ 本地即可运行：轻量部署，无需云服务器



---



\## 🧩 系统架构



```mermaid

graph TD

&nbsp;   A\[企业微信 / 飞书 / n8n Webhook] -->|HTTP POST| B\[FastAPI 接口 /wechat]

&nbsp;   B --> C\[LangChain 智能体 DeepSeekBot]

&nbsp;   C --> D\[Chroma 向量数据库]

&nbsp;   C --> E\[知识库文件夹 (knowledge/)]

&nbsp;   C --> F\[bge-m3 中文向量模型]

&nbsp;   F -->|语义检索| C

&nbsp;   C --> G\[DeepSeek Chat API]

&nbsp;   G -->|生成回复| H\[返回企业微信 / 飞书 / 客户端]

🏗️ 项目结构

bash

复制代码

ai\_wechat\_bot/

│

├── knowledge/             # 知识库目录，支持多格式文件（txt, pdf, docx, pptx, xlsx, wps）

├── chroma\_db/             # 向量数据库持久化目录

├── venv/                  # 虚拟环境（可选）

│

├── app.py                 # FastAPI 启动入口（提供 /wechat 接口）

├── chatbot.py             # LangChain + DeepSeek 智能体核心逻辑

├── requirements.txt       # 依赖文件

├── .env                   # 环境变量配置（DeepSeek API Key + 人设）

├── knowledge.txt          # 示例知识文件

└── start.ps1              # Windows 一键启动脚本

⚙️ 技术栈

模块	技术

Web框架	FastAPI

LLM调用	DeepSeek Chat API

知识检索	LangChain + ChromaDB

向量模型	HuggingFace Embeddings (bge-m3)

文件监控	Watchdog 实时热加载

文档解析	unstructured / PyPDF / docx2txt / python-docx

环境管理	python-dotenv



🚀 快速上手

1️⃣ 安装依赖

bash

复制代码

pip install -r requirements.txt

2️⃣ 配置环境变量

在项目根目录创建 .env 文件：



bash

复制代码

DEEPSEEK\_API\_KEY=你的API密钥

ASSISTANT\_ROLE=你是一名温柔且专业的企业售后客服

3️⃣ 运行服务

bash

复制代码

uvicorn app:app --reload

启动后访问：

👉 http://127.0.0.1:8000/docs



🧠 知识库使用说明

知识库目录位于：



bash

复制代码

/knowledge

支持放入以下类型文件：



复制代码

.txt / .pdf / .docx / .pptx / .xlsx / .wps

系统会自动解析并更新向量数据库，无需重启程序。

📁 当文件发生增删改操作时，watchdog 会自动触发知识库重建。



🧩 接口文档

POST /wechat

用于接收消息并返回智能回复。



请求示例：

json

复制代码

{

&nbsp; "text": "请问浙传最近会开展什么活动？",

&nbsp; "session\_id": "user123"

}

返回示例：

json

复制代码

{

&nbsp; "reply": "您好！根据资料显示，近期在钱塘新区有一场创业主题活动..."

}

GET /health

检查服务运行状态。



json

复制代码

{"status": "ok"}

💻 运行演示

访问 http://127.0.0.1:8000/docs 查看 Swagger API 文档👇



接口测试页	控制台日志	回复结果



将这些截图放在项目根目录下的 /assets 文件夹中（GitHub 会自动展示）。



🧭 应用场景

场景	说明

🤝 企业客服	对接企业微信 / 飞书机器人，实现7x24小时客服

📚 内部知识问答	公司文档、培训资料自动检索问答

🧾 营销助手	结合活动资料，自动回复优惠、活动问答

🧠 教育答疑	学校内部智能答疑系统



🔮 未来规划

☁️ 云端部署（支持 Docker、公网 Webhook）



🧩 集成工作流（n8n / 飞书自动化 / 企业微信API）



🧠 多模型支持（DeepSeek / Qwen / Yi / GPT）



🖥️ Web 管理端与知识库可视化



📊 智能FAQ生成与分类检索



🪐 开发者寄语

“LangChain 是大脑，Chroma 是记忆，DeepSeek 是灵魂。”

未来的客服不再是人工替代，而是企业知识的流动与沉淀。

希望这个项目能帮你开启企业智能化服务的第一步。



📌 作者信息

👤 开发者：PeterPan

💡 技术方向：AI 应用开发 / 自动化工作流 / LangChain 实践

📫 联系方式：在 Issues 区留言讨论即可



⭐ 支持项目

如果你喜欢这个项目，请为它点一颗 ⭐Star！

未来我将持续更新云端版与可视化控制台版本 🚀

