import chardet


def detect_file_encoding(file_path):
    # 读取文件的前10000个字节用于检测编码
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)

    # 使用 chardet 检测文件编码
    result = chardet.detect(raw_data)

    # 获取编码格式和置信度
    encoding = result.get('encoding')
    confidence = result.get('confidence')

    return encoding, confidence


# 要检测的文件路径
# file_path = "D:\Documents\WeChat Files\wxid_q8r1q7xxjv8h22\FileStorage\File\\2024-09\天可汗.txt"
# file_path = "D:\Documents\WeChat Files\wxid_q8r1q7xxjv8h22\FileStorage\File\\2024-09\(NEW)天可汗.txt"
file_path = r"D:\RelaxTools\books\soushu2025.com@斗破苍穹魔改加料版[搜书吧].txt"

# 检测文件编码
try:
    encoding, confidence = detect_file_encoding(file_path)
    if encoding:
        print(f"文件编码格式：{encoding}")
        print(f"检测置信度：{confidence * 100:.2f}%")
    else:
        print("无法检测文件的编码格式。")
except FileNotFoundError:
    print(f"文件未找到: {file_path}")
except Exception as e:
    print(f"发生异常: {e}")
