# services/tts_service.py
import os
import time
import subprocess
from datetime import datetime
import torch
import soundfile as sf

from config import QWEN_AUDIO_MODEL_PATH, AUDIO_OUTPUT_DIR, RERANK_SCRIPT_PATH, FULL_SCRIPT_PATH, VENV_PYTHON

from qwen_tts import Qwen3TTSModel

print("Initializing Qwen3-TTS model. This may take a moment...")
tts_model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto"
)
print("Qwen3-TTS Model loaded successfully.")

def generate_tts_from_reference(reference_audio_path: str, text_to_speak: str, ref_text: str = None):
    if not os.path.exists(reference_audio_path):
        return None, f"Reference audio not found at: {reference_audio_path}"

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{timestamp}.wav"
        output_path = os.path.join(AUDIO_OUTPUT_DIR, output_filename)
        
        os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

        print(f"Generating TTS from reference: {reference_audio_path}")
        wavs, sr = tts_model.generate_voice_clone(
            text=text_to_speak,
            language="chinese",
            speed=1.0,
            ref_audio=reference_audio_path,
            ref_text=ref_text if ref_text else "",
            x_vector_only_mode=True
        )
        
        sf.write(output_path, wavs[0], sr)

        absolute_output_path = os.path.abspath(output_path)
        print(f"Successfully generated audio file: {absolute_output_path}")
        return absolute_output_path, None

    except Exception as e:
        import traceback
        error_message = f"An error occurred during Qwen3-TTS generation: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return None, error_message

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
