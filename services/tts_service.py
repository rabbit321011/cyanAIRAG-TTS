# services/tts_service.py
import os
import sys
import time
import subprocess
from datetime import datetime
import torch
import soundfile as sf

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import QWEN_AUDIO_MODEL_PATH, AUDIO_OUTPUT_DIR, RERANK_SCRIPT_PATH, FULL_SCRIPT_PATH, VENV_PYTHON

from qwen_tts import Qwen3TTSModel
import torch

# === 正确加载 0.6B Custom Voice（关键修复） ===
model_path = r"E:\AIlibs\Qwen3-TTS-0.6B-CustomVoice-base"  # 你之前合并好的目录

model = Qwen3TTSModel.from_pretrained(
    model_path,
    torch_dtype=torch.float32,      # ← 必须float32！float16会导致nan/inf和CUDA assert
    device_map="cuda:0",
    trust_remote_code=True,
)

print("✅ 模型加载成功")
print(f"支持speakers: {model.get_supported_speakers()}")
print("当前设备: cuda:0")

def generate_tts_from_custom_voice(text_to_speak: str, instruct: str = "", language: str = "Chinese", temperature: float = 0.65, top_p: float = 0.92):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{timestamp}.wav"
        output_path = os.path.join(AUDIO_OUTPUT_DIR, output_filename)
        
        os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

        print(f"Generating TTS with Custom Voice")
        print(f"Text: {text_to_speak}")
        print(f"Instruct: {instruct}")
        print(f"Language: {language}")
        print(f"Temperature: {temperature}")
        print(f"Top_p: {top_p}")
        
        # 关键修复：speaker必须是 "yoeawa"
        wavs, sr = model.generate_custom_voice(
            text=text_to_speak,
            language=language,
            speaker="yoeawa",           # ← 必须改成这个！不是"default"
            instruct=instruct,
            temperature=temperature,       # 使用传入的参数
            top_p=top_p,                # 使用传入的参数
            repetition_penalty=1.15,    # 防止重复/爆炸
            max_new_tokens=1200,
            do_sample=True
        )
        
        sf.write(output_path, wavs[0], sr)

        absolute_output_path = os.path.abspath(output_path)
        print(f"Successfully generated audio file: {absolute_output_path}")
        return absolute_output_path, None
    except Exception as e:
        print(f"Error generating TTS: {e}")
        import traceback
        traceback.print_exc()
        return None, str(e)

def run_test_script(script_name: str):
    script_map = {'full': FULL_SCRIPT_PATH, 'rerank': RERANK_SCRIPT_PATH}
    script_path = script_map.get(script_name)
    
    if not script_path or not os.path.exists(script_path):
        return {"status": "error", "message": f"Script '{script_name}' not found."}

    start_time = time.time()
    try:
        process = subprocess.run(
            [VENV_PYTHON, script_path], capture_output=True, text=True,
            encoding='utf-8', timeout=300
        )
        duration = time.time() - start_time
        return {
            "status": "success" if process.returncode == 0 else "failed",
            "script": script_name,
            "duration_seconds": round(duration, 2),
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "message": "Script execution timed out after 300 seconds."}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}