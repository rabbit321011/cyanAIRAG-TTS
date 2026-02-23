
import requests
import json

BASE_URL = "http://localhost:3723"

print("=" * 60)
print("Testing new features")
print("=" * 60)

# Test 1: Ping
print("\n1. Testing service...")
resp = requests.get(f"{BASE_URL}/ping")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}")

# Test 2: Embed
print("\n2. Testing embed...")
resp = requests.post(f"{BASE_URL}/rag/embed", json={"text": "test"})
vector_str = resp.json()["vector_str"]
print("   OK")

# Test 3: Insert to temp
print("\n3. Testing insert to temp...")
test_data = json.dumps({"title": "Test"})
resp = requests.post(
    f"{BASE_URL}/rag/insert",
    json={
        "table_name": "temp",
        "vector_str": vector_str,
        "data_str": test_data
    }
)
print(f"   Response: {resp.json()}")

# Test 4: Search temp
print("\n4. Testing search temp...")
resp = requests.post(
    f"{BASE_URL}/rag/search/topk",
    json={"target_dbs": ["temp"], "vector_str": vector_str, "k": 5}
)
results = resp.json()["results"]
print(f"   Found {len(results)} results")

# Test 5: Clear temp
print("\n5. Testing clear temp...")
resp = requests.post(
    f"{BASE_URL}/rag/clear/table",
    json={"table_name": "temp"}
)
print(f"   Response: {resp.json()}")

# Test 6: Clear all
print("\n6. Testing clear all...")
resp = requests.post(f"{BASE_URL}/rag/clear/all")
print(f"   Response: {resp.json()}")

print("\n" + "=" * 60)
print("All tests done!")
print("=" * 60)
