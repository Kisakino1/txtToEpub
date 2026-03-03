import re
from ebooklib import epub

# 创建 EPUB 书籍对象
book = epub.EpubBook()

# 设置书籍元数据
book_title = '我的道侣都太诡异了（1-77）'  # 书名，用于设置元数据和生成文件名
book.set_title(book_title)
book.add_author('逆时针的圈[搜书吧]')
book.set_language('zh')

# 读取书籍内容
txtFile = r"D:\Downloads\soushu2025.com@《我的道侣都太诡异了》1-77章  作者：逆时针的圈[搜书吧].txt"
with open(txtFile, 'r', encoding='utf-8') as file:
    content = file.read()

# 使用正则表达式匹配卷标题和章节标题
# 卷标题：只匹配到“第X卷”本身，后面如果紧跟“第一章/第一节”等，不一起吞掉
volume_pattern = r'(第[\d一二三四五六七八九十百千万零]+卷(?:\s+(?!第[\d一二三四五六七八九十百千万零]+[章节])[^\n]*)?)'
# volume_pattern = r'★☆【卷[一二三四五六七八九十百千万零]+.*?】 ☆★'  # 另一种特殊格式的卷标题示例
chapter_pattern = r'(?m)^\s*(第[\d一二三四五六七八九十百千万零]+[章节][：:、\s]*[^\n]*)'  # 行首匹配"章/节"（允许前导空格），标题到行尾

# 尝试匹配卷标题，如果匹配不到则直接按章节划分
volumes = re.split(volume_pattern, content)
book_toc = []

# 规范化章节标题（为空或过长时给出安全标题）
def normalize_chapter_title(raw_title: str, index_one_based: int) -> str:
    title = (raw_title or '').strip()
    if not title:
        return f'第{index_one_based}章'
    # 标题过长可能是误判为正文，限制长度
    if len(title) > 50:
        return f'第{index_one_based}章'
    return title

# 处理引子内容
prologue_content = ""
if len(volumes) > 1:
    # 如果匹配到了卷，检查卷前是否有引子内容
    if volumes[0].strip():
        prologue_content = volumes[0].strip()
else:
    # 如果没有卷，按章节匹配，检查章节前是否有引子内容
    chapters = re.split(chapter_pattern, content)
    if chapters[0].strip():
        prologue_content = chapters[0].strip()

# 创建引子章节
if prologue_content:
    prologue = epub.EpubHtml(title='引子', file_name='prologue.xhtml', lang='zh')
    prologue.content = f'<h1>引子</h1><p>{prologue_content.replace("\n", "<br/>")}</p>'
    book.add_item(prologue)
    book_toc.append(prologue)

# 继续处理卷和章节
if len(volumes) > 1:
    # 如果匹配到了卷，按卷来组织
    for v in range(1, len(volumes), 2):
        if volumes[v] is None or volumes[v].strip() == "":
            continue

        volume_title = volumes[v].strip()
        volume_content = volumes[v + 1].strip() if v + 1 < len(volumes) and volumes[v + 1] is not None else ""

        # 打印卷名
        print(f'卷名: {volume_title}')

        # 使用正则表达式分割卷内的章节
        chapters = re.split(chapter_pattern, volume_content)
        volume_chapters = []

        # 创建卷的封面章节
        volume_intro = epub.EpubHtml(title=volume_title, file_name=f'volume_{v // 2 + 1}_intro.xhtml', lang='zh')
        volume_intro.content = f'<h1>{volume_title}</h1>'
        book.add_item(volume_intro)
        volume_chapters.append(volume_intro)

        # 遍历卷中的所有章节
        for i in range(1, len(chapters), 2):
            if chapters[i] is None or chapters[i].strip() == "":
                continue

            chapter_title = normalize_chapter_title(chapters[i], i // 2 + 1)
            chapter_content = chapters[i + 1].strip() if i + 1 < len(chapters) and chapters[i + 1] is not None else ""

            # 打印章名
            print(f'章名: {chapter_title}')

            # 创建章节对象
            chapter = epub.EpubHtml(title=chapter_title, file_name=f'volume_{v // 2 + 1}_chapter_{i // 2 + 1}.xhtml', lang='zh')
            chapter.content = f'<h1>{chapter_title}</h1><p>{chapter_content.replace("\n", "<br/>")}</p>'

            # 添加章节到卷中
            volume_chapters.append(chapter)
            book.add_item(chapter)

        # 将卷的章节作为目录项添加到书籍的 TOC
        book_toc.append((epub.Section(volume_title), tuple(volume_chapters)))

else:
    # 如果没有匹配到卷，直接处理章节
    chapters = re.split(chapter_pattern, content)
    for i in range(1, len(chapters), 2):
        if chapters[i] is None or chapters[i].strip() == "":
            continue

        chapter_title = normalize_chapter_title(chapters[i], i // 2 + 1)
        chapter_content = chapters[i + 1].strip() if i + 1 < len(chapters) and chapters[i + 1] is not None else ""

        # 打印章名
        print(f'章名: {chapter_title}')

        # 创建章节对象
        chapter = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{i // 2 + 1}.xhtml', lang='zh')
        chapter.content = f'<h1>{chapter_title}</h1><p>{chapter_content.replace("\n", "<br/>")}</p>'

        # 添加章节到书籍
        book.add_item(chapter)
        book_toc.append(chapter)

# 设置书籍目录和阅读顺序
book.toc = tuple(book_toc)
book.spine = ['nav']

# 遍历书籍的目录，只将具体的章节添加到 spine 中
for item in book_toc:
    if isinstance(item, tuple):
        _, chapters_in_volume = item

        book.spine.extend(chapters_in_volume)
    else:
        book.spine.append(item)

# 添加导航和样式
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

style = 'BODY { font-family: Times, serif; }'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

# 写入 EPUB 文件
epub.write_epub(f'{book_title}.epub', book)
