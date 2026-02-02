# Windows 打包用：供界面调用，入参由 GUI 传入。
from pathlib import Path
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
    result = chardet.detect(raw_data)
    return result['encoding']


def convert_file_encoding(input_file, output_file, target_encoding='utf-8'):
    """返回 (成功, 消息字符串)。"""
    source_encoding = detect_encoding(input_file)
    if source_encoding is None:
        return False, "无法检测文件的编码格式，转换终止。"
    if source_encoding.lower() == 'gb2312':
        source_encoding = 'gbk'
    try:
        with open(input_file, 'r', encoding=source_encoding, errors='replace') as infile, \
             open(output_file, 'w', encoding=target_encoding) as outfile:
            for line in infile:
                outfile.write(line)
        return True, f"检测到源编码：{source_encoding}\n已转换为 {target_encoding} 并保存至：\n{output_file}"
    except Exception as e:
        return False, f"读取或写入文件时发生错误：{e}"


def generate_output_filename(input_file, target_encoding='utf-8'):
    input_path = Path(input_file)
    new_filename = f"{input_path.stem}_{target_encoding}{input_path.suffix}"
    return str(input_path.parent / new_filename)


def run_convert(input_file, target_encoding='utf-8'):
    """供 GUI 调用：转换编码，返回 (成功, 消息)。"""
    output_file = generate_output_filename(input_file, target_encoding)
    return convert_file_encoding(input_file, output_file, target_encoding)
