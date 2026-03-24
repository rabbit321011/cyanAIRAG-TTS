import os
import glob
from datetime import datetime

# 音频目录
AUDIO_DIR = "E:\\AIlibs\\audio"

# 测试顺序和语言
TEST_ORDER = [
    "【卖萌】鸡肉，吃不了啊，这些不能直接吃",
    "【叙述】但是我觉得了解的话，对自己的认知也有所增长吧",
    "【可爱】所有权不是我的话，很容易引起不必要的纠纷",
    "【惊叹】主人宝宝是是称呼啊，好怪啊",
    "【惊讶】不玩瓦啊，什么鬼，全世界的人都玩瓦就我不玩吗",
    "【正式】希望友善的玩家不要提及相关信息，即便是在合作那些年",
    "【激动】好多食物哇，哈哈，确实为什么他们都是食物啊，不是，馒头这个称呼是你们自己取的吧，因为他原名又不叫这个",
    "【生气】然后这些野生的小群，不就是你说的那种小团体嘛!",
    "【疑问】我人设已经变成这样了吗，别神话我我害怕",
    "【笑的停不下来】忍不住啦，啊呵呵呵，啊~要下播了，再这样下去的话，要连环响了，哎呀",
    "【萌萌】好晚了播，确实，我还想这么晚播会没人",
    "【说话】就他说要不要众筹搞一个比较高的挡位",
    "【软】这算夜宵吗，就一根鸡肉肠而已馁",
    "【雀跃】form集合！凡人们"
]

LANGUAGES = ["auto", "chinese", "english"]

def get_file_timestamp(file_path):
    """获取文件的修改时间戳"""
    try:
        return os.path.getmtime(file_path)
    except:
        return 0

def main():
    """重命名音频文件"""
    print("开始重命名音频文件...")
    
    # 获取所有WAV文件并按修改时间排序
    wav_files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
    # 过滤掉已经是新格式的文件
    old_format_files = [f for f in wav_files if not any(lang in os.path.basename(f) for lang in LANGUAGES)]
    # 按修改时间排序（最新的在前）
    old_format_files.sort(key=get_file_timestamp, reverse=True)
    # 只取最近的42个文件（14个测试文件 × 3种语言）
    old_format_files = old_format_files[:42]
    # 再按时间正序排序（最早的在前）
    old_format_files.sort(key=get_file_timestamp)
    
    print(f"找到 {len(old_format_files)} 个旧格式文件")
    
    # 生成预期的新文件名列表
    expected_new_files = []
    for test_name in TEST_ORDER:
        for lang in LANGUAGES:
            expected_new_files.append(f"{lang}-{test_name}.wav")
    
    # 确保文件数量匹配
    if len(old_format_files) != len(expected_new_files):
        print(f"警告：文件数量不匹配，找到 {len(old_format_files)} 个文件，但需要 {len(expected_new_files)} 个文件")
        return
    
    # 重命名文件
    for i, old_file in enumerate(old_format_files):
        new_filename = expected_new_files[i]
        new_path = os.path.join(AUDIO_DIR, new_filename)
        
        try:
            os.rename(old_file, new_path)
            print(f"✓ 重命名: {os.path.basename(old_file)} -> {new_filename}")
        except Exception as e:
            print(f"✗ 失败: {os.path.basename(old_file)} -> {new_filename}")
            print(f"  错误: {str(e)}")
    
    print("\n重命名完成！")

if __name__ == "__main__":
    main()
