
import requests
import json

BASE_URL = "http://localhost:3723"

print("=" * 60)
print("测试新增功能：temp 分区 + 清空数据库接口")
print("=" * 60)

# 测试 1: Ping 服务
print("\n--- 1. 检查服务状态 ---")
resp = requests.get(f"{BASE_URL}/ping")
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.json()}")

# 测试 2: 向量化文本
print("\n--- 2. 文本向量化 ---")
test_text = "这是测试temp分区的内容"
resp = requests.post(f"{BASE_URL}/rag/embed", json={"text": test_text})
vector_str = resp.json()["vector_str"]
print("✓ 文本向量化成功")

# 测试 3: 插入数据到 temp 分区
print("\n--- 3. 插入数据到 temp 分区 ---")
test_data = json.dumps({"title": "测试temp", "content": test_text})
resp = requests.post(
    f"{BASE_URL}/rag/insert",
    json={
        "table_name": "temp",
        "vector_str": vector_str,
        "data_str": test_data
    }
)
print(f"响应: {resp.json()}")

# 测试 4: 搜索 temp 分区
print("\n--- 4. 搜索 temp 分区 ---")
resp = requests.post(
    f"{BASE_URL}/rag/search/topk",
    json={
        "target_dbs": ["temp"],
        "vector_str": vector_str,
        "k": 5
    }
)
results = resp.json()["results"]
print(f"✓ 找到 {len(results)} 条结果")

# 测试 5: 清空 temp 分区
print("\n--- 5. 清空 temp 分区 ---")
resp = requests.post(
    f"{BASE_URL}/rag/clear/table",
    json={"table_name": "temp"}
)
print(f"响应: {resp.json()}")

# 测试 6: 验证 temp 分区已清空
print("\n--- 6. 验证 temp 分区已清空 ---")
resp = requests.post(
    f"{BASE_URL}/rag/search/topk",
    json={
        "target_dbs": ["temp"],
        "vector_str": vector_str,
        "k": 5
    }
)
results = resp.json()["results"]
print(f"✓ temp 分区有 {len(results)} 条结果 (应为 0)")

# 测试 7: 向其他分区插入测试数据
print("\n--- 7. 向 event 和 theory 分区插入测试数据 ---")
for table in ["event", "theory"]:
    test_data2 = json.dumps({"title": f"测试{table}", "content": test_text})
    resp = requests.post(
        f"{BASE_URL}/rag/insert",
        json={
            "table_name": table,
            "vector_str": vector_str,
            "data_str": test_data2
        }
    )
    print(f"✓ 已插入到 {table}")

# 测试 8: 清空所有表
print("\n--- 8. 清空所有表 ---")
resp = requests.post(f"{BASE_URL}/rag/clear/all")
print(f"响应: {resp.json()}")

# 测试 9: 验证所有表已清空
print("\n--- 9. 验证所有表已清空 ---")
all_empty = True
for table in ["event", "theory", "object", "relationship", "temp"]:
    resp = requests.post(
        f"{BASE_URL}/rag/search/topk",
        json={
            "target_dbs": [table],
            "vector_str": vector_str,
            "k": 5
        }
    )
    results = resp.json()["results"]
    if len(results) &gt; 0:
        print(f"✗ {table} 分区还有 {len(results)} 条结果")
        all_empty = False

if all_empty:
    print("✓ 所有分区已成功清空!")

print("\n" + "=" * 60)
print("所有测试完成!")
print("=" * 60)
