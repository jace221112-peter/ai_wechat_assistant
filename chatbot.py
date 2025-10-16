# chatbot.py
import os
import threading
import time
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ---------- 全局配置 ----------
KNOWLEDGE_DIR = "knowledge"
PERSIST_DIR = "chroma_db"
TOP_K = 3                    # 检索返回文档数
MAX_TURNS = 10               # 会话记忆最多保留轮次

# 会话记忆：session_id -> List[{role, content}]
SESSION_MEMORIES: Dict[str, List[Dict[str, str]]] = {}


def ensure_dirs():
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
        print(f"📁 未找到 {KNOWLEDGE_DIR}，已自动创建。")
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR, exist_ok=True)


# ---------- 文档加载 ----------
def load_docs(folder_path=KNOWLEDGE_DIR) -> List[Document]:
    ensure_dirs()
    docs: List[Document] = []
    for name in os.listdir(folder_path):
        path = os.path.join(folder_path, name)
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".txt":
                loader = TextLoader(path, encoding="utf-8")
            elif ext == ".pdf":
                loader = PyPDFLoader(path)
            elif ext == ".docx":
                loader = Docx2txtLoader(path)
            else:
                print(f"⚠️ 暂不支持的文件类型：{name}，已跳过。")
                continue
            loaded = loader.load()
            docs.extend(loaded)
        except Exception as e:
            print(f"❌ 加载 {name} 失败：{e}")
    print(f"📚 文档加载完成，共 {len(docs)} 条。")
    return docs


def split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"🧩 文档切分完成，共 {len(chunks)} 个片段。")
    return chunks


# ---------- DeepSeek 客户端 ----------
def make_deepseek_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 DEEPSEEK_API_KEY，请在 .env 中配置。")
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"  # 兼容 OpenAI 格式
    )
    return client


# ---------- 向量库 ----------
def make_embeddings():
    # 中文检索更稳的 bge-m3（CPU 可运行）
    return HuggingFaceEmbeddings(model_name="BAAI/bge-m3")


def build_or_update_vectorstore(embeddings) -> Chroma:
    docs = load_docs(KNOWLEDGE_DIR)
    if not docs:
        # 即使没有文档，也初始化一个空的向量库，避免报错
        return Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

    chunks = split_docs(docs)
    # 若已存在则在其上增量更新；首次则新建
    if os.listdir(PERSIST_DIR):
        vs = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
        vs.add_documents(chunks)
        vs.persist()
        print("🔁 向量库增量更新完成。")
        return vs
    else:
        vs = Chroma.from_documents(chunks, embeddings, persist_directory=PERSIST_DIR)
        vs.persist()
        print("✅ 向量库创建完成。")
        return vs


# ---------- 文件夹热加载监控 ----------
class _KnowledgeHandler(FileSystemEventHandler):
    def __init__(self, bot_ref):
        super().__init__()
        self.bot_ref = bot_ref
        self._lock = threading.Lock()
        self._last = 0

    def on_any_event(self, event):
        # 防抖：1秒内的连续事件只触发一次
        now = time.time()
        with self._lock:
            if now - self._last < 1.0:
                return
            self._last = now
        print("🔎 检测到知识库变更，正在重建向量库...")
        self.bot_ref.rebuild_vectorstore()


class DeepSeekBot:
    def __init__(self):
        ensure_dirs()
        self.client = make_deepseek_client()
        self.embeddings = make_embeddings()
        self.vectorstore = build_or_update_vectorstore(self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K})
        # 人设（系统提示）
        self.role = os.getenv(
            "ASSISTANT_ROLE",
            "你是一名资深售后客服，语气亲切、礼貌、简洁，优先依据公司提供的知识库回答。"
        )

        # 启动文件监控
        self._observer = Observer()
        handler = _KnowledgeHandler(self)
        self._observer.schedule(handler, KNOWLEDGE_DIR, recursive=True)
        self._observer.daemon = True
        self._observer.start()
        print("👀 已开启知识库热加载监控。")

    def rebuild_vectorstore(self):
        self.vectorstore = build_or_update_vectorstore(self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": TOP_K})
        print("📦 向量库已重建。")

    def _get_memory(self, session_id: str) -> List[Dict[str, str]]:
        mem = SESSION_MEMORIES.setdefault(session_id, [])
        # 限制记忆轮数
        if len(mem) > MAX_TURNS * 2:
            SESSION_MEMORIES[session_id] = mem[-MAX_TURNS * 2:]
        return SESSION_MEMORIES[session_id]

    def ask(self, query: str, session_id: str = "default") -> str:
        try:
            # 1) 语义检索
            docs = self.retriever.get_relevant_documents(query)
            context = "\n\n".join([d.page_content for d in docs]) if docs else "（知识库暂无相关内容）"

            # 2) 组装 Prompt（含知识+人设+历史对话）
            system_msg = (
                f"{self.role}\n"
                f"你必须基于【已知资料】优先作答，无法确认时请明确说明。\n"
                f"【已知资料】:\n{context}"
            )

            messages = [{"role": "system", "content": system_msg}]
            # 加入会话记忆
            history = self._get_memory(session_id)
            messages.extend(history)
            # 当前用户消息
            messages.append({"role": "user", "content": query})

            # 3) 调用 DeepSeek
            resp = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            answer = resp.choices[0].message.content

            # 4) 更新记忆
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": answer})

            return answer

        except Exception as e:
            print("❌ 生成回答出错：", e)
            return "抱歉，我暂时无法回答这个问题。请稍后再试。"


# 对外方法
def create_bot() -> DeepSeekBot:
    bot = DeepSeekBot()
    print("✅ DeepSeek 机器人初始化完成。")
    return bot
