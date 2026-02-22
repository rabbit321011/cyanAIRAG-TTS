import requests
import json

BASE_URL = "http://127.0.0.1:3723"

print("=== 测试删除接口 ===")

# 1. 生成 embedding
print("\n1. 生成 Embedding...")
embed_response = requests.post(
    f"{BASE_URL}/rag/embed",
    json={"text": "测试删除功能"}
)
vector_str = embed_response.json()["vector_str"]
print("✓ Embedding 生成成功")

# 2. 插入数据
print("\n2. 插入数据...")
data_str = json.dumps({"title": "测试", "content": "测试删除功能"})
insert_response = requests.post(
    f"{BASE_URL}/rag/insert",
    json={"vector_str": vector_str, "data_str": data_str}
)
print(f"✓ 插入结果: {insert_response.json()}")

# 3. 搜索验证数据存在
print("\n3. 搜索验证数据存在...")
search_response = requests.post(
    f"{BASE_URL}/rag/search/topk",
    json={"vector_str": vector_str, "k": 5}
)
results = search_response.json()["results"]
print(f"✓ 搜索结果数量: {len(results)}")
print(f"  结果: {results}")

# 4. 删除数据
print("\n4. 删除数据...")
delete_response = requests.post(
    f"{BASE_URL}/rag/delete",
    json={"data_str": data_str}
)
print(f"✓ 删除结果: {delete_response.json()}")

# 5. 再次搜索验证数据已删除
print("\n5. 再次搜索验证数据已删除...")
search_response2 = requests.post(
    f"{BASE_URL}/rag/search/topk",
    json={"vector_str": vector_str, "k": 5}
)
results2 = search_response2.json()["results"]
print(f"✓ 搜索结果数量: {len(results2)}")
print(f"  结果: {results2}")

print("\n=== 删除接口测试完成！===")
