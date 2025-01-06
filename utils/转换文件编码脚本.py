import os
from pathlib import Path
import argparse
import chardet

def detect_encoding(file_path):
    """
    检测文件的编码格式
    :param file_path: 文件路径
    :return: 检测到的编码格式
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)  # 读取文件的前10000个字节进行检测
    result = chardet.detect(raw_data)
    return result['encoding']


def convert_file_encoding(input_file, output_file, target_encoding='utf-8'):
    """
    将文件的编码格式转换为指定的编码格式
    :param input_file: 输入文件路径（需要转换编码的文件）
    :param output_file: 输出文件路径（转换后保存的文件）
    :param target_encoding: 目标编码格式（默认是 utf-8）
    """
    # 检测文件的当前编码格式
    source_encoding = detect_encoding(input_file)
    print(f"检测到的文件编码格式：{source_encoding}")

    if source_encoding is None:
        print("无法检测文件的编码格式，转换终止。")
        return

    # 将 gb2312 改为 gbk，增加兼容性
    if source_encoding.lower() == 'gb2312':
        source_encoding = 'gbk'

    # 逐行读取文件内容并将其解码为 Unicode
    try:
        with open(input_file, 'r', encoding=source_encoding, errors='replace') as infile, \
             open(output_file, 'w', encoding=target_encoding) as outfile:
            for line in infile:
                outfile.write(line)
        print(f"文件编码已成功转换为 {target_encoding} 并保存至 {output_file}")
    except Exception as e:
        print(f"读取或写入文件时发生错误：{e}")



def generate_output_filename(input_file, target_encoding='utf-8'):
    """
    根据输入文件路径生成默认的输出文件路径
    :param input_file: 输入文件路径
    :param target_encoding: 目标编码格式（用于文件名标识）
    :return: 自动生成的输出文件路径
    """
    # 使用 Path 对象处理文件路径
    input_path = Path(input_file)

    # 获取文件的父目录路径、文件名（去掉扩展名）和扩展名
    parent_dir = input_path.parent
    stem = input_path.stem  # 文件名（不包含扩展名）
    suffix = input_path.suffix  # 文件的扩展名

    # 生成输出文件名（在文件名中加入目标编码格式）
    new_filename = f"{stem}_{target_encoding}{suffix}"
    output_file = parent_dir / new_filename

    return str(output_file)


input_file = r"D:\RelaxTools\books\soushu2025.com@火星引力《网游之修罗传说》未删减[搜书吧].txt"
output_file = generate_output_filename(input_file)
convert_file_encoding(input_file, output_file)

