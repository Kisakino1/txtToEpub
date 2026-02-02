#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHM文件转TXT工具
将Microsoft CHM格式的帮助文档转换为纯文本文件
"""

import os
import sys
import re
from html.parser import HTMLParser
from io import StringIO


class HTMLTextExtractor(HTMLParser):
    """从HTML中提取纯文本的解析器"""
    
    def __init__(self):
        super().__init__()
        self.text = StringIO()
        self.skip_tags = {'script', 'style', 'head'}
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        # 添加段落、换行等标签的格式
        if tag == 'p':
            self.text.write('\n')
        elif tag == 'br':
            self.text.write('\n')
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.write('\n\n')
            
    def handle_endtag(self, tag):
        # 段落、标题结束后添加换行
        if tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.write('\n')
        elif tag == 'li':
            self.text.write('\n')
        self.current_tag = None
        
    def handle_data(self, data):
        # 跳过script和style标签中的内容
        if self.current_tag not in self.skip_tags:
            # 清理多余的空白字符，但保留必要的换行
            cleaned = re.sub(r'[ \t]+', ' ', data)
            self.text.write(cleaned)
            
    def get_text(self):
        text = self.text.getvalue()
        # 清理连续的空行，最多保留2个换行（一个空行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 清理每行首尾的空格
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines).strip()


def extract_text_from_html(html_content):
    """从HTML内容中提取纯文本"""
    parser = HTMLTextExtractor()
    try:
        parser.feed(html_content)
        return parser.get_text()
    except Exception as e:
        print(f"解析HTML时出错: {e}")
        return ""


def chm_to_txt_using_pychm(chm_file, output_txt):
    """使用pychm库转换CHM到TXT"""
    try:
        import chm.chm as chmlib
    except ImportError:
        print("错误: 未安装pychm库")
        print("请运行: pip install pychm")
        return False
    
    try:
        # 打开CHM文件
        chm_obj = chmlib.CHMFile()
        if not chm_obj.LoadCHM(chm_file):
            print(f"无法打开CHM文件: {chm_file}")
            return False
        
        print(f"正在处理: {chm_file}")
        all_text = []
        file_count = 0
        
        # 遍历CHM文件中的所有条目
        def extract_callback(chm, ui, context):
            nonlocal file_count
            # 只处理HTML文件
            if ui.path.lower().endswith(('.html', '.htm')):
                # 提取文件内容
                success, data = chm.RetrieveObject(ui)
                if success and data:
                    try:
                        # 尝试不同的编码
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'big5']:
                            try:
                                html_content = data.decode(encoding)
                                text = extract_text_from_html(html_content)
                                if text:
                                    all_text.append(f"\n{'='*60}\n")
                                    all_text.append(f"文件: {ui.path}\n")
                                    all_text.append(f"{'='*60}\n\n")
                                    all_text.append(text)
                                    all_text.append("\n\n")
                                    file_count += 1
                                    if file_count % 10 == 0:
                                        print(f"已处理 {file_count} 个文件...")
                                break
                            except UnicodeDecodeError:
                                continue
                    except Exception as e:
                        print(f"处理文件 {ui.path} 时出错: {e}")
            return chmlib.CHM_ENUMERATOR_CONTINUE
        
        # 枚举CHM文件中的所有内容
        chm_obj.Enumerate(chmlib.CHM_ENUMERATE_ALL, extract_callback, None)
        
        # 写入输出文件
        if all_text:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(''.join(all_text))
            print(f"\n转换完成！")
            print(f"共处理 {file_count} 个HTML文件")
            print(f"输出文件: {output_txt}")
            return True
        else:
            print("未能从CHM文件中提取到任何内容")
            return False
            
    except Exception as e:
        print(f"处理CHM文件时出错: {e}")
        return False


def chm_to_txt_using_extract_chmlib(chm_file, output_txt):
    """使用extract_chmLib方式转换（备选方案）"""
    import tempfile
    import shutil
    
    try:
        from CHMParser import CHMParser
    except ImportError:
        print("错误: 未安装CHMParser库")
        print("请尝试运行: pip install chm")
        return False
    
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"正在提取CHM文件...")
        parser = CHMParser()
        parser.LoadCHM(chm_file)
        
        # 提取所有文件到临时目录
        parser.ExtractFiles(temp_dir)
        
        all_text = []
        file_count = 0
        
        # 遍历提取的HTML文件
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith(('.html', '.htm')):
                    file_path = os.path.join(root, file)
                    try:
                        # 尝试不同的编码读取
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'big5']:
                            try:
                                with open(file_path, 'r', encoding=encoding) as f:
                                    html_content = f.read()
                                text = extract_text_from_html(html_content)
                                if text:
                                    all_text.append(f"\n{'='*60}\n")
                                    all_text.append(f"文件: {file}\n")
                                    all_text.append(f"{'='*60}\n\n")
                                    all_text.append(text)
                                    all_text.append("\n\n")
                                    file_count += 1
                                    if file_count % 10 == 0:
                                        print(f"已处理 {file_count} 个文件...")
                                break
                            except UnicodeDecodeError:
                                continue
                    except Exception as e:
                        print(f"处理文件 {file} 时出错: {e}")
        
        # 写入输出文件
        if all_text:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(''.join(all_text))
            print(f"\n转换完成！")
            print(f"共处理 {file_count} 个HTML文件")
            print(f"输出文件: {output_txt}")
            return True
        else:
            print("未能从CHM文件中提取到任何内容")
            return False
            
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主函数"""
    print("="*60)
    print("CHM转TXT工具")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print(f"  python {os.path.basename(__file__)} <chm文件路径> [输出txt文件路径]")
        print("\n示例:")
        print(f"  python {os.path.basename(__file__)} help.chm")
        print(f"  python {os.path.basename(__file__)} help.chm output.txt")
        print("\n依赖库安装:")
        print("  pip install pychm")
        print("  或者:")
        print("  pip install chm")
        sys.exit(1)
    
    chm_file = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(chm_file):
        print(f"错误: 文件不存在: {chm_file}")
        sys.exit(1)
    
    # 确定输出文件名
    if len(sys.argv) >= 3:
        output_txt = sys.argv[2]
    else:
        # 默认输出文件名：原文件名.txt
        base_name = os.path.splitext(os.path.basename(chm_file))[0]
        output_txt = base_name + '.txt'
    
    print(f"\n输入文件: {chm_file}")
    print(f"输出文件: {output_txt}\n")
    
    # 尝试使用pychm
    print("尝试使用pychm库...")
    success = chm_to_txt_using_pychm(chm_file, output_txt)
    
    if not success:
        print("\npychm方式失败，请确保已安装依赖库:")
        print("  pip install pychm")
        print("\n如果pychm安装失败，可以尝试:")
        print("  1. 在Windows上使用: pip install pychm")
        print("  2. 在Linux上: sudo apt-get install libchm-dev && pip install pychm")
        print("  3. 在macOS上: brew install chmlib && pip install pychm")
        sys.exit(1)


if __name__ == '__main__':
    main()

