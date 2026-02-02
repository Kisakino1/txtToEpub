# Windows 打包用：供界面调用，入参由 GUI 传入。
import chardet


def detect_file_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
    result = chardet.detect(raw_data)
    return result.get('encoding'), result.get('confidence')


def run_check(file_path):
    """供 GUI 调用：检测文件编码，返回 (encoding, confidence)，异常时抛出。"""
    return detect_file_encoding(file_path)
