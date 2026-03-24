
import os
import sys

try:
    from pydub import AudioSegment
    print("使用 pydub 转换...")
    
    mp3_path = r"D:\test_aria\luyin\input.mp3"
    wav_path = r"D:\test_aria\luyin\input.wav"
    
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    print(f"转换成功! WAV文件保存到: {wav_path}")
    
except ImportError:
    print("pydub 未安装，尝试使用 librosa...")
    try:
        import librosa
        import soundfile as sf
        
        mp3_path = r"D:\test_aria\luyin\input.mp3"
        wav_path = r"D:\test_aria\luyin\input.wav"
        
        audio, sr = librosa.load(mp3_path, sr=None, mono=True)
        sf.write(wav_path, audio, sr)
        print(f"转换成功! WAV文件保存到: {wav_path}")
        
    except Exception as e:
        print(f"转换失败: {e}")
        print("\n请尝试手动转换MP3为WAV格式，或者安装 ffmpeg:")
        print("1. 下载 ffmpeg: https://ffmpeg.org/download.html")
        print("2. 或使用在线转换工具: https://cloudconvert.com/mp3-to-wav")
        sys.exit(1)

except Exception as e:
    print(f"转换失败: {e}")
    sys.exit(1)
