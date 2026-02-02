# Mac 打包用：供界面调用，入参由 GUI 传入。
import os
import re
from ebooklib import epub


def run_txt_to_epub(book_title, author, txt_file, output_dir=None):
    """
    供 GUI 调用：生成 epub。返回 (生成的 epub 路径, None) 成功；(None, 错误信息) 失败。
    output_dir 为空时保存到 txt 所在目录。
    """
    if not book_title:
        book_title = '我的书'
    if not author:
        author = '作者'
    if not txt_file or not os.path.isfile(txt_file):
        return None, "请选择有效的 txt 文件路径。"
    save_dir = output_dir if output_dir else os.path.dirname(os.path.abspath(txt_file))

    book = epub.EpubBook()
    book.set_title(book_title)
    book.add_author(author)
    book.set_language('zh')

    try:
        with open(txt_file, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        return None, f"读取 txt 失败：{e}"

    volume_pattern = r'(第[\d一二三四五六七八九十百千万零]+卷\s+[^。\n]*)'
    chapter_pattern = r'(?m)^\s*(第[\d一二三四五六七八九十百千万零]+[章节][：:、\s]*[^\n]*)'
    volumes = re.split(volume_pattern, content)
    book_toc = []

    def normalize_chapter_title(raw_title: str, index_one_based: int) -> str:
        title = (raw_title or '').strip()
        if not title:
            return f'第{index_one_based}章'
        if len(title) > 50:
            return f'第{index_one_based}章'
        return title

    prologue_content = ""
    if len(volumes) > 1:
        if volumes[0].strip():
            prologue_content = volumes[0].strip()
    else:
        chapters = re.split(chapter_pattern, content)
        if chapters[0].strip():
            prologue_content = chapters[0].strip()

    if prologue_content:
        prologue = epub.EpubHtml(title='引子', file_name='prologue.xhtml', lang='zh')
        prologue.content = f'<h1>引子</h1><p>{prologue_content.replace(chr(10), "<br/>")}</p>'
        book.add_item(prologue)
        book_toc.append(prologue)

    if len(volumes) > 1:
        for v in range(1, len(volumes), 2):
            if volumes[v] is None or volumes[v].strip() == "":
                continue
            volume_title = volumes[v].strip()
            volume_content = volumes[v + 1].strip() if v + 1 < len(volumes) and volumes[v + 1] is not None else ""
            print(f'卷名: {volume_title}')
            chapters = re.split(chapter_pattern, volume_content)
            volume_chapters = []
            volume_intro = epub.EpubHtml(title=volume_title, file_name=f'volume_{v // 2 + 1}_intro.xhtml', lang='zh')
            volume_intro.content = f'<h1>{volume_title}</h1>'
            book.add_item(volume_intro)
            volume_chapters.append(volume_intro)
            for i in range(1, len(chapters), 2):
                if chapters[i] is None or chapters[i].strip() == "":
                    continue
                chapter_title = normalize_chapter_title(chapters[i], i // 2 + 1)
                chapter_content = chapters[i + 1].strip() if i + 1 < len(chapters) and chapters[i + 1] is not None else ""
                print(f'章名: {chapter_title}')
                chapter = epub.EpubHtml(title=chapter_title, file_name=f'volume_{v // 2 + 1}_chapter_{i // 2 + 1}.xhtml', lang='zh')
                chapter.content = f'<h1>{chapter_title}</h1><p>{chapter_content.replace(chr(10), "<br/>")}</p>'
                volume_chapters.append(chapter)
                book.add_item(chapter)
            book_toc.append((epub.Section(volume_title), tuple(volume_chapters)))
    else:
        chapters = re.split(chapter_pattern, content)
        for i in range(1, len(chapters), 2):
            if chapters[i] is None or chapters[i].strip() == "":
                continue
            chapter_title = normalize_chapter_title(chapters[i], i // 2 + 1)
            chapter_content = chapters[i + 1].strip() if i + 1 < len(chapters) and chapters[i + 1] is not None else ""
            print(f'章名: {chapter_title}')
            chapter = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{i // 2 + 1}.xhtml', lang='zh')
            chapter.content = f'<h1>{chapter_title}</h1><p>{chapter_content.replace(chr(10), "<br/>")}</p>'
            book.add_item(chapter)
            book_toc.append(chapter)

    book.toc = tuple(book_toc)
    book.spine = ['nav']
    for item in book_toc:
        if isinstance(item, tuple):
            _, chapters_in_volume = item
            book.spine.extend(chapters_in_volume)
        else:
            book.spine.append(item)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    style = 'BODY { font-family: Times, serif; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    out_path = os.path.join(save_dir, f'{book_title}.epub')
    try:
        epub.write_epub(out_path, book)
        return out_path, None
    except Exception as e:
        return None, f"写入 epub 失败：{e}"
