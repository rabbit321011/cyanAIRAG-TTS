import requests
import json

BASE_URL = "http://localhost:3723"

def test_embed(text):
    print(f"\n--- 测试 /rag/embed ---")
    print(f"输入文本: {text}")
    response = requests.post(
        f"{BASE_URL}/rag/embed",
        json={"text": text}
    )
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result.get("vector_str")

def test_insert(vector_str, data_str):
    print(f"\n--- 测试 /rag/insert ---")
    print(f"数据: {data_str}")
    response = requests.post(
        f"{BASE_URL}/rag/insert",
        json={"vector_str": vector_str, "data_str": data_str}
    )
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

def test_search_topk(vector_str, k):
    print(f"\n--- 测试 /rag/search/topk (k={k}) ---")
    response = requests.post(
        f"{BASE_URL}/rag/search/topk",
        json={"vector_str": vector_str, "k": k}
    )
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

def test_search_threshold(vector_str, threshold):
    print(f"\n--- 测试 /rag/search/threshold (threshold={threshold}) ---")
    response = requests.post(
        f"{BASE_URL}/rag/search/threshold",
        json={"vector_str": vector_str, "threshold": threshold}
    )
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("="*50)
    print("开始测试 RAG API")
    print("="*50)
    
    # 1. 测试 embedding 并获取向量
    vector1 = test_embed("人工智能是未来的技术")
    vector2 = test_embed("机器学习在不断发展")
    vector3 = test_embed("今天天气很好")
    
    # 2. 插入数据
    if vector1:
        test_insert(vector1, json.dumps({"title": "AI介绍", "content": "人工智能是未来的技术"}))
    if vector2:
        test_insert(vector2, json.dumps({"title": "机器学习", "content": "机器学习在不断发展"}))
    if vector3:
        test_insert(vector3, json.dumps({"title": "天气", "content": "今天天气很好"}))
    
    # 3. 测试搜索
    if vector1:
        test_search_topk(vector1, 3)
        test_search_threshold(vector1, 0.5)
    
    print("\n" + "="*50)
    print("所有测试完成！")
    print("="*50)
