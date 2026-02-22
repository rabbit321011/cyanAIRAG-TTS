# server.py
import sys
from flask import Flask, jsonify, request
import subprocess
import os
import time
from datetime import datetime

app = Flask(__name__)

# 虚拟环境的 python 路径
VENV_PYTHON = r"E:\AIlibs\agent-env\Scripts\python.exe"

# 项目根目录
BASE_DIR = r"E:\AIlibs"
TEST_DIR = os.path.join(BASE_DIR, "testAndReadme")

# 测试脚本路径
TEST_SCRIPTS = {
    "full": os.path.join(TEST_DIR, "test_qwen3_a_scheme.py"),
    "rerank": os.path.join(TEST_DIR, "testRerank.py"),
}

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "ok",
        "message": "Python Agent Server is alive",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    import torch
    gpu_ok = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_ok else "No GPU"
    gpu_mem = torch.cuda.get_device_properties(0).total_memory // (1024**3) if gpu_ok else 0

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "agent-env",
        "gpu_available": gpu_ok,
        "gpu_name": gpu_name,
        "gpu_memory_gb": gpu_mem,
        "python_version": sys.version.split()[0],
        "working_dir": os.getcwd()
    }), 200


@app.route('/test', methods=['POST'])
def run_test():
    data = request.get_json() or {}
    script_key = data.get("script", "full")  # 默认跑 full 测试

    if script_key not in TEST_SCRIPTS:
        return jsonify({
            "status": "error",
            "message": f"无效的 script 参数。支持: {list(TEST_SCRIPTS.keys())}"
        }), 400

    script_path = TEST_SCRIPTS[script_key]

    if not os.path.exists(script_path):
        return jsonify({
            "status": "error",
            "message": f"脚本文件不存在: {script_path}"
        }), 404

    start_time = time.time()

    try:
        # 使用 subprocess 调用 python 脚本（在同一虚拟环境执行）
        result = subprocess.run(
            [VENV_PYTHON, script_path],
            capture_output=True,
            text=True,
            timeout=600,           # 最多等 10 分钟
            cwd=TEST_DIR           # 工作目录设为测试文件夹
        )

        duration = time.time() - start_time

        output = {
            "status": "success" if result.returncode == 0 else "failed",
            "script": script_key,
            "duration_seconds": round(duration, 2),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode,
            "generated_files": []  # 可以后续解析 stdout 提取生成的文件名
        }

        # 简单提取生成的文件（看输出中是否有 .wav）
        if "wav" in output["stdout"].lower():
            lines = output["stdout"].splitlines()
            for line in lines:
                if ".wav" in line and "生成" in line:
                    output["generated_files"].append(line.strip())

        return jsonify(output), 200

    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "timeout",
            "message": "测试执行超时（超过 600 秒）",
            "duration_seconds": 600
        }), 504

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    print("Starting Qwen3 Agent Server on http://localhost:3723")
    app.run(
        host='0.0.0.0',
        port=3723,
        debug=True
    )