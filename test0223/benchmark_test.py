
import requests
import json
import time
import random

BASE_URL = "http://localhost:3723"

# 生成150字左右的中文测试文本
def generate_test_text():
    subjects = ["人工智能", "机器学习", "深度学习", "自然语言处理", "计算机视觉"]
    verbs = ["可以用于", "能够帮助", "有助于", "广泛应用于", "在...方面取得了重大进展"]
    objects = ["图像识别", "语音合成", "智能推荐", "自动驾驶", "医疗诊断", "金融风控", "智能制造"]
    
    text = f"{random.choice(subjects)}{random.choice(verbs)}{random.choice(objects)}。"
    text += "这项技术通过大量数据训练，能够自动学习特征模式，"
    text += "在实际应用中展现出强大的能力和巨大的潜力。"
    text += "随着计算能力的提升和算法的优化，"
    text += "未来将在更多领域发挥重要作用，"
    text += "为人类社会带来深刻的变革和便利。"
    
    return text

print("=" * 70)
print("CyanAI 基准测试")
print("=" * 70)

# 测试1: 单条文本向量化时间
print("\n[测试1] 单条文本向量化时间")
print("-" * 70)
test_text = generate_test_text()
print(f"测试文本长度: {len(test_text)} 字")
print(f"文本内容: {test_text[:50]}...")

embed_times = []
for i in range(10):
    start = time.time()
    resp = requests.post(f"{BASE_URL}/rag/embed", json={"text": test_text})
    end = time.time()
    embed_time = (end - start) * 1000
    embed_times.append(embed_time)
    print(f"  第 {i+1} 次: {embed_time:.2f} ms")

avg_embed = sum(embed_times) / len(embed_times)
print(f"\n平均向量化时间: {avg_embed:.2f} ms")

# 获取一个向量用于后续测试
resp = requests.post(f"{BASE_URL}/rag/embed", json={"text": test_text})
vector_str = resp.json()["vector_str"]

# 测试2: 批量插入200条数据
print("\n[测试2] 批量插入 200 条数据")
print("-" * 70)

insert_times = []
for i in range(200):
    test_data = json.dumps({"title": f"测试数据 {i+1}", "content": generate_test_text()})
    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/rag/insert",
        json={
            "table_name": "temp",
            "vector_str": vector_str,
            "data_str": test_data
        }
    )
    end = time.time()
    insert_time = (end - start) * 1000
    insert_times.append(insert_time)
    if (i + 1) % 20 == 0:
        print(f"  已插入 {i+1} 条...")

avg_insert = sum(insert_times) / len(insert_times)
total_insert = sum(insert_times)
print(f"\n平均插入时间: {avg_insert:.2f} ms/条")
print(f"总插入时间: {total_insert:.2f} ms ({total_insert/1000:.2f} 秒)")

# 测试3: 向量检索时间（Top-K）
print("\n[测试3] 向量检索时间 (Top-K=5)")
print("-" * 70)

search_times = []
for i in range(20):
    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/rag/search/topk",
        json={
            "target_dbs": ["temp"],
            "vector_str": vector_str,
            "k": 5
        }
    )
    end = time.time()
    search_time = (end - start) * 1000
    search_times.append(search_time)
    results = resp.json()["results"]
    print(f"  第 {i+1} 次: {search_time:.2f} ms (返回 {len(results)} 条结果)")

avg_search = sum(search_times) / len(search_times)
print(f"\n平均检索时间: {avg_search:.2f} ms")

# 测试4: 向量检索时间（阈值搜索）
print("\n[测试4] 向量检索时间 (阈值=0.8)")
print("-" * 70)

threshold_times = []
for i in range(20):
    start = time.time()
    resp = requests.post(
        f"{BASE_URL}/rag/search/threshold",
        json={
            "target_dbs": ["temp"],
            "vector_str": vector_str,
            "threshold": 0.8
        }
    )
    end = time.time()
    threshold_time = (end - start) * 1000
    threshold_times.append(threshold_time)
    results = resp.json()["results"]
    print(f"  第 {i+1} 次: {threshold_time:.2f} ms (返回 {len(results)} 条结果)")

avg_threshold = sum(threshold_times) / len(threshold_times)
print(f"\n平均阈值检索时间: {avg_threshold:.2f} ms")

# 清理测试数据
print("\n[清理] 清空 temp 分区...")
resp = requests.post(f"{BASE_URL}/rag/clear/table", json={"table_name": "temp"})
print(f"  响应: {resp.json()}")

# 输出汇总
print("\n" + "=" * 70)
print("基准测试结果汇总")
print("=" * 70)
print(f"单条文本向量化 (150字):  {avg_embed:.2f} ms")
print(f"批量插入 (200条):         {avg_insert:.2f} ms/条")
print(f"向量检索 (Top-K=5):       {avg_search:.2f} ms")
print(f"向量检索 (阈值=0.8):       {avg_threshold:.2f} ms")
print("=" * 70)
