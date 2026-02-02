# CHM转TXT工具使用说明

## 功能介绍
将Microsoft CHM格式的帮助文档转换为纯文本TXT文件。

## 安装依赖

### 方法1：使用pychm（推荐）

**Windows:**
```bash
pip install pychm
```

**macOS:**
```bash
brew install chmlib
pip install pychm
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libchm-dev python3-dev
pip install pychm
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install chmlib-devel python3-devel
pip install pychm
```

## 使用方法

### 基本用法
```bash
python chmToTxt.py <chm文件路径>
```
这会在当前目录生成一个同名的.txt文件。

### 指定输出文件名
```bash
python chmToTxt.py input.chm output.txt
```

## 使用示例

```bash
# 转换help.chm为help.txt
python chmToTxt.py help.chm

# 转换并指定输出文件名
python chmToTxt.py manual.chm 使用手册.txt

# 使用绝对路径
python chmToTxt.py /path/to/file.chm /path/to/output.txt
```

## 功能特点

1. **自动编码检测**：支持UTF-8、GBK、GB2312、BIG5等多种编码
2. **HTML解析**：自动提取HTML中的文本内容，过滤标签
3. **格式化输出**：保留段落结构，自动处理换行
4. **批量处理**：自动处理CHM文件中的所有HTML页面
5. **进度显示**：每处理10个文件显示一次进度

## 输出格式

转换后的TXT文件格式如下：
```
============================================================
文件: index.html
============================================================

[页面内容...]


============================================================
文件: chapter1.html
============================================================

[页面内容...]
```

## 常见问题

### Q: 提示"未安装pychm库"怎么办？
A: 按照上面的"安装依赖"部分安装pychm库。

### Q: macOS上安装pychm失败？
A: 可能需要先安装chmlib：
```bash
brew install chmlib
export CFLAGS="-I$(brew --prefix chmlib)/include"
export LDFLAGS="-L$(brew --prefix chmlib)/lib"
pip install pychm
```

### Q: 转换后的文本乱码？
A: 程序会自动尝试多种编码。如果仍然乱码，可能是CHM文件本身的编码比较特殊。

### Q: 可以批量转换多个CHM文件吗？
A: 目前版本需要逐个转换。如果需要批量转换，可以使用shell脚本：
```bash
for file in *.chm; do
    python chmToTxt.py "$file"
done
```

## 注意事项

1. 转换大型CHM文件可能需要较长时间
2. 输出的TXT文件可能比较大，建议确保有足够的磁盘空间
3. 程序只提取文本内容，图片等媒体文件不会被转换
4. CHM文件中的JavaScript代码会被过滤

## 技术说明

- 使用`pychm`库读取CHM文件
- 使用`HTMLParser`解析HTML内容
- 支持多种中文编码自动检测
- 过滤script、style等非内容标签

