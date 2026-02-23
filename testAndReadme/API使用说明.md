
# CyanAI API 使用说明

## 目录
1. [TTS (文本转语音) 接口](#tts-文本转语音-接口)
2. [RAG (检索增强生成) 接口](#rag-检索增强生成-接口)
   - [1. 文本向量化接口](#1-文本向量化接口)
   - [2. 数据插入接口](#2-数据插入接口)
   - [3. 全局 Top-K 搜索接口](#3-全局-top-k-搜索接口)
   - [4. 全局阈值搜索接口](#4-全局阈值搜索接口)
   - [5. 数据删除接口](#5-数据删除接口)
   - [6. 重排序 (Rerank) 接口](#6-重排序-rerank-接口)
   - [7. 清空单个表接口](#7-清空单个表接口)
   - [8. 清空所有表接口](#8-清空所有表接口)
3. [向量数据库 (LanceDB) 使用说明](#向量数据库-lancedb-使用说明)
4. [六大分区记忆架构说明](#六大分区记忆架构说明)
5. [实现原理](#实现原理)
6. [性能基准测试](#性能基准测试)

---

## TTS (文本转语音) 接口

### 功能说明
使用 Qwen3-TTS 模型，基于参考音频克隆声音，生成新的语音。

### API 端点
- **URL**: `/tts/generate`
- **方法**: `POST`
- **Content-Type**: `application/json`

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `reference_audio_path` | string | 是 | 参考音频的完整路径 |
| `text` | string | 是 | 需要合成的文本内容 |
| `ref_text` | string | 否 | 参考音频的文本内容（可选，提高克隆质量） |

### 请求示例
```bash
curl -X POST http://localhost:3723/tts/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"reference_audio_path\": \"E:\\AIlibs\\input.wav\", \"text\": \"你好，cyanAI！\"}"
```

### 响应示例
```json
{
  "status": "success",
  "message": "Audio generated successfully.",
  "generated_audio_path": "e:\\AIlibs\\audio\\20260223_015323.wav"
}
```

---

## RAG (检索增强生成) 接口

### 1. 文本向量化接口
将纯文本转换为 Embedding 向量。

#### API 端点
- **URL**: `/rag/embed`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `text` | string | 是 | 需要向量化的文本 |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/embed ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"人工智能是未来的技术\"}"
```

#### 响应示例
```json
{
  "status": "success",
  "vector_str": "[0.012, -0.034, 0.056, ...]"
}
```

---

### 2. 数据插入接口
将向量和关联数据存入指定的向量数据库表。

#### API 端点
- **URL**: `/rag/insert`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `table_name` | string | 是 | 目标表名，必须是 `event`、`theory`、`object`、`relationship`、`temp`、`chat` 之一 |
| `vector_str` | string | 是 | 字符串化的向量数组 |
| `data_str` | string | 是 | 字符串化的 JSON 数据 |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/insert ^
  -H "Content-Type: application/json" ^
  -d "{\"table_name\": \"event\", \"vector_str\": \"[0.012, -0.034, 0.056]\", \"data_str\": \"{\\\"title\\\": \\\"测试\\\", \\\"content\\\": \\\"这是正文\\\"}\"}"
```

#### 响应示例
```json
{
  "status": "success",
  "message": "Data inserted successfully."
}
```

---

### 3. 全局 Top-K 搜索接口
根据向量在指定的多个表中查找最相似的前 K 个结果，并进行全局合并排序。

#### API 端点
- **URL**: `/rag/search/topk`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `target_dbs` | list[string] | 是 | 目标表数组，可以包含一个或多个表（`event`、`theory`、`object`、`relationship`、`temp`、`chat`） |
| `vector_str` | string | 是 | 字符串化的查询向量 |
| `k` | integer | 是 | 返回结果的数量 |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/search/topk ^
  -H "Content-Type: application/json" ^
  -d "{\"target_dbs\": [\"event\", \"theory\"], \"vector_str\": \"[0.012, -0.034, 0.056]\", \"k\": 5}"
```

#### 响应示例
```json
{
  "status": "success",
  "results": [
    "{\"title\": \"测试1\", \"content\": \"这是正文1\"}",
    "{\"title\": \"测试2\", \"content\": \"这是正文2\"}"
  ]
}
```

---

### 4. 全局阈值搜索接口
根据向量和相似度阈值，在指定的多个表中查找所有大于该阈值的结果，并进行全局合并排序。

#### API 端点
- **URL**: `/rag/search/threshold`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `target_dbs` | list[string] | 是 | 目标表数组，可以包含一个或多个表（`event`、`theory`、`object`、`relationship`、`temp`、`chat`） |
| `vector_str` | string | 是 | 字符串化的查询向量 |
| `threshold` | float | 是 | 相似度阈值（0-1之间） |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/search/threshold ^
  -H "Content-Type: application/json" ^
  -d "{\"target_dbs\": [\"event\", \"theory\", \"object\"], \"vector_str\": \"[0.012, -0.034, 0.056]\", \"threshold\": 0.8}"
```

#### 响应示例
```json
{
  "status": "success",
  "results": [
    "{\"title\": \"高符合度数据\", \"content\": \"...\"}"
  ]
}
```

---

### 5. 数据删除接口
根据 data_str（存入时的 JSON 字符串），在指定的向量数据库表中删除完全匹配的记录。

#### API 端点
- **URL**: `/rag/delete`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `table_name` | string | 是 | 目标表名，必须是 `event`、`theory`、`object`、`relationship`、`temp`、`chat` 之一 |
| `data_str` | string | 是 | 存入时的 JSON 字符串（需要完全匹配） |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/delete ^
  -H "Content-Type: application/json" ^
  -d "{\"table_name\": \"event\", \"data_str\": \"{\\\"title\\\": \\\"测试\\\", \\\"content\\\": \\\"测试删除功能\\\"}\"}"
```

#### 响应示例
```json
{
  "status": "success",
  "message": "Deleted successfully."
}
```

---

### 6. 重排序 (Rerank) 接口
使用 Qwen3-Reranker 模型，计算查询与目标文本的相关性得分。得分越高（0-1之间）表示越相关。

#### API 端点
- **URL**: `/rag/rerank`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `query` | string | 是 | 基准查询文本 |
| `targets` | list[string] | 是 | 需要打分的目标文本数组 |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/rerank ^
  -H "Content-Type: application/json" ^
  -d "{\"query\": \"什么是 RAG？\", \"targets\": [\"RAG 是一种检索增强生成技术。\", \"今天天气真不错。\", \"大语言模型可以通过外部知识库提升准确性。\"]}"
```

#### 响应示例
```json
{
  "status": "success",
  "scores": [0.9998, 0.0001, 0.0474]
}
```

---

### 7. 清空单个表接口
清空指定分区表中的所有数据（保留表结构）。

#### API 端点
- **URL**: `/rag/clear/table`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `table_name` | string | 是 | 目标表名，必须是 `event`、`theory`、`object`、`relationship`、`temp`、`chat` 之一 |

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/clear/table ^
  -H "Content-Type: application/json" ^
  -d "{\"table_name\": \"temp\"}"
```

#### 响应示例
```json
{
  "status": "success",
  "message": "Table 'temp' cleared successfully."
}
```

---

### 8. 清空所有表接口
清空所有分区表中的数据（保留表结构）。

#### API 端点
- **URL**: `/rag/clear/all`
- **方法**: `POST`
- **Content-Type**: `application/json`

#### 请求参数
无

#### 请求示例
```bash
curl -X POST http://localhost:3723/rag/clear/all
```

#### 响应示例
```json
{
  "status": "success",
  "message": "All tables cleared successfully."
}
```

---

## 向量数据库 (LanceDB) 使用说明

### 数据库配置
- **存储目录**: `e:\AIlibs\lancedb_data`
- **向量维度**: 根据使用的 Embedding 模型自动确定

### 六大分区表结构
系统采用"六大分区记忆"架构，将数据存储在六个独立的表中：

| 表名 | 说明 | 用途 |
|------|------|------|
| `event` | 事件表 | 存储事件、经历、时间线等信息 |
| `theory` | 理论表 | 存储知识、理论、概念等信息 |
| `object` | 对象表 | 存储实体、物品、人物等信息 |
| `relationship` | 关系表 | 存储关系、连接、关联等信息 |
| `temp` | 临时表 | 存储临时数据、缓存等信息 |
| `chat` | 对话表 | 存储对话历史、聊天记录等信息 |

### 单表结构（每个表都相同）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `vector` | list[float32] | Embedding 向量 |
| `data` | string | 关联的 JSON 数据（字符串化） |

### 搜索方式
- **度量方式**: 余弦相似度 (Cosine Similarity)
- **相似度计算**: `similarity = 1 - distance`
- **全局检索**: 支持同时搜索多个表，并在内存中进行全局合并排序

---

## 六大分区记忆架构说明

### 设计理念
将知识库按照认知科学中的记忆分类原则，划分为六个独立的向量数据库表，实现更精细的知识组织和检索。

### 核心特点

#### 1. 写入/删除：一对一操作
- 每次插入或删除数据时，必须**明确指定目标表**
- 保证数据归属清晰，避免混淆

#### 2. 检索：多对多操作
- 支持同时检索一个或多个表
- 后端自动从多个表中拉取结果
- 在内存中进行**全局合并排序**
- 返回最优的全局召回结果

#### 3. 全局排序逻辑
- 从每个指定表中获取 Top-K 结果
- 将所有结果合并到一个列表中
- 按余弦距离升序排序（距离越小越相似）
- 截取最终的 Top-K 结果返回

### 使用建议

| 场景 | 推荐表 | 说明 |
|------|--------|------|
| 记录今天发生的事情 | `event` | 事件、时间线类信息 |
| 存储机器学习知识 | `theory` | 理论、概念、知识类 |
| 保存人物档案 | `object` | 实体、对象类信息 |
| 记录人际关系 | `relationship` | 关系、连接类信息 |
| 临时数据存储 | `temp` | 临时数据、缓存类 |
| 对话历史存储 | `chat` | 对话历史、聊天记录类 |
| 全面搜索相关信息 | `["event", "theory", "object", "relationship", "temp", "chat"]` | 跨表全局检索 |

---

## 实现原理

### TTS (文本转语音) 实现原理

1. **模型加载**: 启动时加载 `Qwen/Qwen3-TTS-12Hz-1.7B-Base` 模型
2. **声音克隆**: 使用 `generate_voice_clone` 方法
   - 输入参考音频提取声纹特征
   - 基于声纹特征和目标文本生成新语音
3. **音频输出**: 使用 soundfile 库保存为 WAV 格式

### RAG (检索增强生成) 实现原理

#### 1. Embedding 向量化
- 使用 `Qwen/Qwen3-Embedding-0.6B` 模型
- 将文本转换为高维向量表示
- 保留语义信息

#### 2. 六大分区记忆架构
- **设计思路**: 按照认知科学的记忆分类原则，将知识库划分为六个独立的向量数据库表
- **六个分区表**:
  - `event`: 事件、经历、时间线
  - `theory`: 知识、理论、概念
  - `object`: 实体、物品、人物
  - `relationship`: 关系、连接、关联
  - `temp`: 临时数据、缓存
  - `chat`: 对话历史、聊天记录
- **优势**: 实现更精细的知识组织，支持针对性检索和全局检索

#### 3. 向量存储
- 使用 LanceDB 作为向量数据库
- 每个分区表独立存储，互不干扰
- 支持高效的近似最近邻搜索 (ANN)
- 数据持久化存储

#### 4. 全局检索与合并排序
- **多表拉取**: 根据 `target_dbs` 参数，同时从多个指定表中检索结果
- **内存合并**: 将所有表的检索结果合并到一个列表中
- **全局排序**: 按余弦距离升序排序（距离越小越相似）
- **结果截断**: 截取最终的 Top-K 结果返回
- **优势**: 实现真正的"全局召回最优解"，避免单表检索的局限性

#### 5. 相似度搜索
- 基于余弦距离计算向量相似度
- Top-K 搜索: 返回最相似的 K 个结果（支持跨表全局检索）
- 阈值搜索: 过滤出相似度大于指定阈值的结果（支持跨表全局检索）

#### 6. 数据删除
- 基于完全匹配的 data_str 进行删除
- 必须指定目标表名进行删除
- 自动处理 SQL 注入风险（转义单引号）
- 使用 LanceDB 的条件删除语法

#### 7. 表清空功能
- `clear_table()`: 清空指定表的所有数据（保留表结构）
- `clear_all_tables()`: 清空所有表的所有数据（保留表结构）
- 使用 `delete(where="true")` 语法删除所有记录

#### 8. 重排序 (Rerank) 实现原理
- **模型**: 使用 `Qwen/Qwen3-Reranker-0.6B`（CausalLM 因果语言模型）
- **核心逻辑**:
  1. 构造特定的 Prompt 格式（包含 Query、Document 和判断指令）
  2. 使用模型的 chat_template 格式化对话
  3. 执行前向传播（不生成文本），获取最后一个 Token 的 logits
  4. 从词表中提取 "yes" 和 "no" 的 logit 值
  5. 对这两个值进行 Softmax 计算，得出 Yes 的绝对概率作为相关性得分
- **得分范围**: 0.0（完全不相关）到 1.0（完全相关）
- **性能优化**: 使用 bfloat16 精度 + Flash Attention 2 加速

### 项目架构
```
cyanai-python-server/
├── config.py              # 配置文件
├── run.py                 # 服务入口
├── app/
│   ├── __init__.py        # Flask 应用工厂
│   └── routes.py          # API 路由定义
├── services/
│   ├── tts_service.py     # TTS 服务
│   └── rag_service.py     # RAG 服务
├── audio/                 # 音频输出目录
└── lancedb_data/          # 向量数据库目录
```

---

## 性能基准测试

### 测试环境
- 测试日期: 2026-02-23
- 向量模型: Qwen/Qwen3-Embedding-0.6B
- 数据库: LanceDB
- 数据集规模: 200 条测试数据
- 测试文本长度: 约 100-150 字

### 测试结果

| 操作 | 平均耗时 | 说明 |
|------|---------|------|
| **单条文本向量化** | **48.39 ms** | 约 100 字中文文本 |
| **批量插入数据** | **120.46 ms/条** | 200 条总耗时 24.09 秒 |
| **Top-K 检索 (K=5)** | **22.79 ms** | 在 200 条数据中检索 |
| **阈值检索 (threshold=0.8)** | **70.66 ms** | 返回 100 条结果 |

### 详细测试数据

#### 1. 文本向量化
- 第 1 次: 98.93 ms (首次加载稍慢)
- 第 2-10 次: 29-55 ms (稳定)
- **平均: 48.39 ms**

#### 2. 批量插入
- 测试规模: 200 条记录
- 单条平均: 120.46 ms
- **总耗时: 24.09 秒**

#### 3. Top-K 向量检索
- 第 1 次: 116.96 ms (首次加载稍慢)
- 第 2-20 次: 16-20 ms (稳定)
- **平均: 22.79 ms**

#### 4. 阈值检索
- 阈值设置: 0.8
- 返回结果数: 100 条
- **平均: 70.66 ms**

### 性能特点

1. **首次调用**: 向量化和检索的首次调用会稍慢（预热），后续调用速度稳定
2. **检索效率**: Top-K 检索非常快，平均仅 22.79 ms，适合实时应用
3. **插入性能**: 单条插入约 120 ms，批量插入 200 条约 24 秒
4. **阈值检索**: 由于需要返回更多结果（100条），耗时较长，约 70 ms

### 测试脚本

完整的基准测试脚本位于: `test0223/benchmark_test.py`
