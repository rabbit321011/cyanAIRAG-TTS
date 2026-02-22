
# CyanAI - RAG + TTS with 4-Partition Memory Architecture

一个基于 Qwen3 模型的 RAG（检索增强生成）+ TTS（文本转语音）系统，采用四大分区记忆架构。

## 功能特性

- ✅ **四大分区记忆架构**：event（事件）、theory（理论）、object（对象）、relationship（关系）
- ✅ **RAG 向量检索**：支持 Top-K 和阈值搜索
- ✅ **智能重排序**：使用 Qwen3-Reranker 进行相关性排序
- ✅ **声音克隆 TTS**：基于 Qwen3-TTS 的声音克隆功能
- ✅ **Flash Attention 2**：高效的注意力计算

---

## 环境要求

- Python 3.13+
- NVIDIA GPU（支持 CUDA 12.8）
- Windows 系统

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/rabbit321011/cyanAIRAG-TTS.git
cd cyanAIRAG-TTS
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv agent-env

# Windows 激活
.\agent-env\Scripts\activate
```

### 3. 安装 PyTorch with CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 4. 安装其他依赖

```bash
pip install -r requirements.txt
```

### 5. 安装 Flash Attention 2

需要下载 wheel 文件并安装：

```bash
# 下载 flash_attn-2.8.3+cu128torch2.10-cp313-cp313-win_amd64.whl
pip install flash_attn-2.8.3+cu128torch2.10-cp313-cp313-win_amd64.whl
```

### 6. 启动服务

```bash
python run.py
```

服务将在 `http://localhost:3723` 启动。

---

## 验证服务

检查服务是否正常运行：

```bash
curl http://localhost:3723/ping
```

响应：
```json
{
  "status": "ok",
  "message": "Python server is alive!"
}
```

---

## 📚 文档目录

请务必查看 `testAndReadme/` 目录下的详细文档：

| 文档 | 用途 |
|------|------|
| **THEAI.md** | 项目搭建和修改指南 - 详细环境配置、模型参数、实现原理 |
| **API使用说明.md** | 完整API文档 - 详细参数说明、请求示例、响应格式 |
| **API快速调用指南.md** | 快速上手 - 只需复制粘贴就能用的API调用示例 |

---

## 项目结构

```
cyanAIRAG-TTS/
├── app/                    # Flask 应用
├── services/               # 核心服务
│   ├── rag_service.py      # RAG 服务
│   └── tts_service.py      # TTS 服务
├── testAndReadme/          # 文档目录 ⭐
├── test0223/               # 测试脚本
├── config.py               # 配置文件
├── run.py                  # 启动入口
├── requirements.txt        # 依赖列表
└── README.md              # 本文档
```

---

## 模型说明

本项目使用以下 Qwen3 模型：

- **Embedding**：Qwen/Qwen3-Embedding-0.6B
- **Reranker**：Qwen/Qwen3-Reranker-0.6B
- **TTS**：Qwen/Qwen3-TTS-12Hz-1.7B-Base

模型会在首次运行时自动下载。

---

## 常见问题

### Q: 显存不足怎么办？

A: 请参考 `testAndReadme/THEAI.md` 中的显存管理章节。

### Q: 如何调用 API？

A: 查看 `testAndReadme/API快速调用指南.md` 或 `testAndReadme/API使用说明.md`。

### Q: 想要修改模型配置？

A: 请查看 `testAndReadme/THEAI.md` 中的详细说明。

---

## 许可证

本项目仅供学习和研究使用。

---

## 相关资源

- Qwen3 官方文档
- Flash Attention 2
- LanceDB 向量数据库

