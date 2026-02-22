以下是更新后的完整 Markdown 文档，已经整合了我们今天的所有进展，包括：

- 如何进入/退出虚拟环境（详细步骤 + 常见问题）
- TTS 支持的语言列表（完整 + 推荐用法）
- 所有组件的最新使用方式（尤其是 TTS 的克隆接口、ref_text 重要性、x_vector_only_mode 等）
- 显存管理、常见坑点、后续扩展建议

你可以直接复制保存为 `Qwen3-Agent-本地环境搭建记录.md`，放在 E:\AIlibs\ 目录下，方便以后开发时随时查阅。

# Qwen3 Agent 本地环境搭建记录（RTX 5070 Ti Laptop 12GB VRAM）

**日期**：2026年2月22日  
**操作系统**：Windows  
**GPU**：NVIDIA GeForce RTX 5070 Ti Laptop GPU（12GB GDDR7）  
**CUDA**：12.8  
**Python**：3.13.7（虚拟环境 agent-env）  
**目标**：搭建 Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B + Qwen3-TTS-1.7B-Base + LanceDB 的本地环境，用于个人 Agent 开发（支持声音克隆 TTS）。

## 1. 最终环境状态（2026-02-22 成功验证）

- **PyTorch**：2.10.0+cu128（CUDA 可用）
- **Flash Attention**：2.8.3（wheel 安装成功，支持加速 & 省显存）
- **核心组件**：
  - Embedding：Qwen/Qwen3-Embedding-0.6B（sentence-transformers 加载）
  - Reranker：Qwen/Qwen3-Reranker-0.6B（transformers CausalLM + yes/no logits 概率打分）
  - TTS：Qwen/Qwen3-TTS-12Hz-1.7B-Base（qwen-tts 包，generate_voice_clone 接口，支持声音克隆）
  - 向量数据库：LanceDB 0.29.2
- **显存占用估算**（动态加载，按需 del + empty_cache）：
  - Embedding 0.6B：~1.5GB
  - Reranker 0.6B：~1.8GB
  - TTS 1.7B Base（克隆生成峰值）：~7–9GB
  - 总峰值控制在 10–11GB 内（12GB 显卡可承受）

## 2. 如何进入/退出虚拟环境（重要！）

虚拟环境路径：`E:\AIlibs\agent-env`

### 进入（激活）虚拟环境
1. 打开 PowerShell
2. 切换目录：
   ```powershell
   E:
   cd \AIlibs
   ```

3. 激活：
   ```powershell
   .\agent-env\Scripts\Activate.ps1
   ```
   - 成功后提示符会变成 `(agent-env) PS E:\AIlibs>`

### 退出虚拟环境
```powershell
deactivate
```

### 验证当前是否在虚拟环境中
```powershell
python -c "import sys; print(sys.executable)"
```
- 正确输出示例：`E:\AIlibs\agent-env\Scripts\python.exe`
- 如果输出全局路径（如 `C:\Python313\python.exe`），说明没激活成功 → 重新运行 Activate.ps1

### 常见问题
- 激活后提示符没变：可能是 PowerShell 执行策略限制，尝试以管理员身份运行 PowerShell。
- 每次新开窗口都要重新激活：正常行为。可以写个 bat 快捷方式（见文末）。

## 3. 安装步骤（完整复现命令）

### 3.1 创建虚拟环境（已完成）
```powershell
python -m venv agent-env
```

### 3.2 安装 PyTorch CUDA 12.8
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 3.3 安装 Flash Attention 2
- 下载 wheel 文件：`flash_attn-2.8.3+cu128torch2.10-cp313-cp313-win_amd64.whl`
```powershell
pip install E:\AIlibs\flash_attn-2.8.3+cu128torch2.10-cp313-cp313-win_amd64.whl
```

### 3.4 安装核心依赖
```powershell
pip install "transformers>=4.51.0" "sentence-transformers>=3.0.0" accelerate
pip install lancedb
pip install -U qwen-tts soundfile
```

### 3.5 安装 SoX（TTS 音频后处理必须）
- 下载地址：https://sourceforge.net/projects/sox/files/sox/
- 安装到：`C:\Program Files (x86)\sox-14-4-2`
- 添加到系统 PATH：
  
  - 右键“此电脑” → 属性 → 高级系统设置 → 环境变量 → 系统变量 Path → 编辑 → 新增 `C:\Program Files (x86)\sox-14-4-2`
- 验证：
  ```powershell
  sox --version
  ```

## 4. 组件使用方式总结（含 TTS 语言列表）

### 4.1 Embedding (Qwen3-Embedding-0.6B)
```python
from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer(
    "Qwen/Qwen3-Embedding-0.6B",
    model_kwargs={"torch_dtype": torch.bfloat16, "attn_implementation": "flash_attention_2", "device_map": "auto"},
    trust_remote_code=True
)
embeddings = embed_model.encode(texts, normalize_embeddings=True)
```

### 4.2 Reranker (Qwen3-Reranker-0.6B)
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

rerank_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B", padding_side="left", trust_remote_code=True)
rerank_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B", torch_dtype=torch.bfloat16, attn_implementation="flash_attention_2", device_map="auto", trust_remote_code=True).eval()

yes_id = rerank_tokenizer.convert_tokens_to_ids("yes")
no_id = rerank_tokenizer.convert_tokens_to_ids("no")

def get_rerank_score(query, doc):
    prompt = f"""<|im_start|>system
Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end>
<|im_start|>user
<Instruct>: Given a web search query, retrieve relevant passages that answer the query
<Query>: {query}
<Document>: {doc}<|im_end>
<|im_start|>assistant
<think>

</think>

"""
    inputs = rerank_tokenizer(prompt, return_tensors="pt", max_length=8192, truncation=True).to(device)
    outputs = rerank_model(**inputs)
    logits = outputs.logits[:, -1, :]
    probs = torch.softmax(logits[:, [no_id, yes_id]], dim=-1)
    return probs[0, 1].item()  # yes 概率作为相关性分数
```

### 4.3 TTS (Qwen3-TTS-12Hz-1.7B-Base) – 支持声音克隆

**支持的语言**（必须用英文全称或 'auto'，不要用 'zh'）：
- 'auto'（自动检测，最推荐）
- 'chinese'
- 'english'
- 'french'
- 'german'
- 'italian'
- 'japanese'
- 'korean'
- 'portuguese'
- 'russian'
- 'spanish'

**使用方式**（必须提供参考音频和参考文本）：
```python
from qwen_tts import Qwen3TTSModel
import soundfile as sf

tts_model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto"
)

ref_audio = r"E:\AIlibs\input.wav"          # 你的参考音频路径（3–10s 清晰语音）
ref_text = "你好，这是我的参考语音样本。"   # 必须准确匹配音频里说的话！

wavs, sr = tts_model.generate_voice_clone(
    text="你好！这是测试文本。",
    language="chinese",                     # 或 "auto"
    speed=1.0,
    ref_audio=ref_audio,
    ref_text=ref_text,
    # 可选：x_vector_only_mode=True         # 只用声纹特征，不强制文本匹配（克隆更稳定）
)

sf.write("output_cloned.wav", wavs[0], sr)
```

**注意**：
- ref_text 不准会导致音色失真、杂音、怪腔。
- speed 范围建议 0.8–1.2，过快/慢会不自然。
- 生成后记得 `del tts_model; torch.cuda.empty_cache()`

### 4.4 LanceDB 示例（向量存储）
```python
import lancedb

db = lancedb.connect("~/lancedb/my_agent")
table = db.create_table("docs", data=[{"vector": emb.tolist(), "text": text} for emb, text in zip(embeddings, texts)])
results = table.search(query_emb).limit(5).to_pandas()
```

## 5. 常见问题 & 注意事项

- **显存管理**：用完模型后必须 `del model; torch.cuda.empty_cache()`
- **TTS 语言**：只支持上面列表的英文全称或 'auto'，'zh' 会报错
- **SoX**：必须安装并加 PATH，否则 TTS 生成失败
- **symlinks warning**：Windows 可忽略，或设置环境变量 `HF_HUB_DISABLE_SYMLINKS_WARNING=1`
- **torch_dtype deprecated**：可改用 `dtype=torch.bfloat16`
- **声音克隆质量**：ref_text 越准确越好；参考音频越清晰（无背景噪音）越好
- **后续扩展建议**：
  1. 加小 LLM（Qwen3-4B/8B-Instruct）生成回复文本
  2. 完整 RAG 流程：Embedding 检索 → Reranker 重排 → LLM 生成 → TTS 语音输出
  3. 语音交互：麦克风输入 → 语音识别 → Agent 处理 → TTS 回复（你的声音）
  4. 打包成 exe 或 Gradio Web UI

## 6. 参考资源

- Qwen3-Embedding：https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Qwen3-Reranker：https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- Qwen3-TTS Base：https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base
- qwen-tts GitHub：https://github.com/QwenLM/Qwen-TTS
- Flash Attention wheel：https://huggingface.co/Wildminder/AI-windows-whl

**文档最后更新**：2026-02-22  
祝开发顺利！如需扩展 RAG/LLM/交互部分，随时补充。

