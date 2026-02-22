# config.py
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Qwen-Audio 模型路径 ---
# !!! 请务必确认此路径是正确的 !!!
QWEN_AUDIO_MODEL_PATH = "E:\\AIlibs\\qwen\\Qwen-Audio-Chat"

# 音频输出目录
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "audio")

# (可选) 旧测试脚本的路径
RERANK_SCRIPT_PATH = os.path.join(BASE_DIR, "testAndReadme", "testRerank.py")
FULL_SCRIPT_PATH = os.path.join(BASE_DIR, "testAndReadme", "test_qwen3_a_scheme.py")

# 虚拟环境的 python 路径
VENV_PYTHON = r"E:\AIlibs\agent-env\Scripts\python.exe"

# --- 新增: RAG 配置 ---
# Embedding 模型路径
EMBEDDING_MODEL_PATH = "Qwen/Qwen3-Embedding-0.6B"

# LanceDB 数据库存储目录
LANCEDB_DIR = os.path.join(BASE_DIR, "lancedb_data")
# 定义四个核心记忆分区的表名
ALLOWED_TABLES = ["event", "theory", "object", "relationship"]

# --- 新增: Rerank 重排序模型配置 ---
RERANK_MODEL_PATH = "Qwen/Qwen3-Reranker-0.6B"
