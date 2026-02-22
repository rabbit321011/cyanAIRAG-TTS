
import requests
import json

BASE_URL = "http://localhost:3723"

print("="*60)
print("验证非 RAG 接口")
print("="*60)

print("\n--- 测试 1: /ping 接口 ---")
resp = requests.get(f"{BASE_URL}/ping", timeout=10)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    print(f"✓ 成功! 响应: {resp.json()}")
else:
    print(f"✗ 失败")

print("\n--- 测试 2: /health 接口 ---")
resp = requests.get(f"{BASE_URL}/health", timeout=10)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    result = resp.json()
    print(f"✓ 成功!")
    print(f"  Python版本: {result.get('python_version')}")
    print(f"  GPU可用: {result.get('gpu_available')}")
    print(f"  GPU名称: {result.get('gpu_name')}")
else:
    print(f"✗ 失败")

print("\n--- 测试 3: TTS 接口 (仅验证参数格式) ---")
print("注意：需要真实的参考音频文件才能完整测试")
print("文档参数：reference_audio_path, text, ref_text(可选)")

# 测试参数验证（应该返回错误，但验证接口存在）
resp = requests.post(
    f"{BASE_URL}/tts/generate",
    json={"text": "测试文本"},  # 缺少必需参数
    timeout=30
)
print(f"状态码: {resp.status_code}")
if resp.status_code == 400:
    print(f"✓ 接口存在! 参数验证正常工作")
    print(f"  响应: {resp.json()}")
else:
    print(f"响应: {resp.text}")

print("\n" + "="*60)
print("验证完成!")
print("="*60)

