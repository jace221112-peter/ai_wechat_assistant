# 🤖 企业微信智能体客服系统（AI WeChat Assistant Bot）

一个基于 **LangChain + FastAPI + DeepSeek + bge-m3 向量检索** 的智能客服系统。  
支持知识库热加载、上下文记忆、多文件格式识别（txt、docx、pdf、WPS文档等），可接入 **企业微信 / 飞书 / n8n Webhook** 实现自动回复与知识问答。

---

## ✨ 功能亮点

✅ **知识库热更新**：文件夹内文档变动实时重建向量库  
✅ **上下文记忆**：支持多 session 独立记忆  
✅ **多格式支持**：自动解析 txt / pdf / docx / WPS 文件  
✅ **中文语义检索**：内置 bge-m3 嵌入模型  
✅ **本地可运行**：无需云服务器，完全离线即可使用  
✅ **可扩展接口**：兼容 Feishu、WeCom、n8n 等 webhook 自动化工具  

---

## 🧩 系统架构

```mermaid
graph TD
    A["WeCom / Feishu / n8n Webhook"] -->|HTTP POST| B["FastAPI 接口 /wechat"]
    B --> C["LangChain Logic Layer (chatbot.py)"]
    C --> D["DeepSeek API 调用"]
    C --> E["Knowledge Folder (knowledge/)"]
    E --> F["Chroma 向量数据库 (chroma_db/)"]
    F --> G["Embedding Model (bge-m3)"]
    C --> H["Session 记忆管理"]
    B --> I["返回 JSON 回复"]
⚙️ 本地运行步骤
1️⃣ 环境准备
bash
复制代码
git clone https://github.com/jace221112-peter/ai_wechat_assistant.git
cd ai_wechat_assistant
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
2️⃣ 配置环境变量
新建 .env 文件，内容如下：

ini
复制代码
DEEPSEEK_API_KEY=你的API密钥
ASSISTANT_ROLE=你的人设（例如：你是一名亲切的售后客服）
3️⃣ 启动服务
bash
复制代码
uvicorn app:app --reload
控制台输出示例：

nginx
复制代码
Uvicorn running on http://127.0.0.1:8000
打开浏览器访问接口文档：

arduino
复制代码
http://127.0.0.1:8000/docs
🌈 示例展示
模块	界面截图
Swagger 接口文档	<img src="assets/swagger_ui.png" width="600">
控制台运行	<img src="assets/console.png" width="600">
响应示例	<img src="assets/response.png" width="600">
PowerShell 启动	<img src="assets/powershell.png" width="600">

📁 图片请放入 assets/ 文件夹中，路径如：assets/swagger_ui.png

📂 项目结构
bash
复制代码
ai_wechat_assistant/
│
├── app.py                # FastAPI 主程序入口
├── chatbot.py            # LangChain 智能体逻辑
├── requirements.txt      # 项目依赖
├── .env.example          # 环境变量模板
├── start.ps1             # 启动脚本
│
├── knowledge/            # 知识库存放目录（支持 WPS/Docx/PDF/TXT）
├── chroma_db/            # 向量数据库（自动生成）
├── assets/               # 图片资源（Swagger截图等）
└── venv/                 # 虚拟环境（已忽略）
💬 项目说明
本项目核心由 LangChain 提供语义检索能力，
DeepSeek API 负责自然语言理解与生成。
通过 FastAPI 提供统一的 HTTP 接口，
可嵌入企业微信客服、飞书机器人、n8n 工作流，实现自动化智能回复。

🧱 依赖说明
主要依赖	说明
FastAPI	Web 框架
LangChain	智能体框架
ChromaDB	本地向量数据库
HuggingFace bge-m3	中文嵌入模型
Watchdog	文件监控（热加载）
dotenv	环境变量管理
Pydantic	数据模型定义

🚀 后续扩展计划
 接入 Feishu、WeCom 自动化客服

 增加多知识库管理后台

 支持文档批量导入与版本管理

 打包 Docker 容器部署

🪄 开发者信息
作者：@jace221112-peter
项目地址：https://github.com/jace221112-peter/ai_wechat_assistant

如果你喜欢这个项目，请为它点一颗 ⭐ Star！