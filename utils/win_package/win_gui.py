# 书工具 GUI：检查编码、转换编码、txt 转 epub，一个窗口三个标签页。
import os
import sys
import threading
import traceback

# 打包成 .app/.exe 时若启动崩溃，把错误写到桌面；无错误则不创建该文件
def _install_crash_log():
    if not getattr(sys, 'frozen', False):
        return
    log_path = os.path.join(os.path.expanduser('~'), 'Desktop', '书工具_启动错误.txt')
    class LazyTee:
        def __init__(self, path):
            self.path = path
            self._file = None
        def _ensure_file(self):
            if self._file is None:
                self._file = open(self.path, 'w', encoding='utf-8')
            return self._file
        def write(self, s):
            if s.strip():
                self._ensure_file().write(s)
                self._ensure_file().flush()
        def flush(self):
            if self._file is not None:
                self._file.flush()
    sys.stderr = LazyTee(log_path)
_log_ready = False
try:
    _install_crash_log()
    _log_ready = True
except Exception:
    pass

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# 打包后与 _win 同目录；开发时 win_gui 在 win_package 下
if __name__ == '__main__':
    _pkg = os.path.dirname(os.path.abspath(__file__))
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)

import 检查文件编码_win as mod_check
import 转换文件编码_win as mod_convert
import txtToEpub_win as mod_epub


def run_in_thread(fn, on_done):
    """在后台线程执行 fn()，完成后用 on_done(result) 在主线程更新 UI。"""
    def work():
        try:
            result = fn()
            root.after(0, lambda: on_done(('ok', result)))
        except Exception as e:
            root.after(0, lambda: on_done(('err', str(e))))

    threading.Thread(target=work, daemon=True).start()


def tab_check(parent):
    frame = ttk.Frame(parent, padding=10)
    ttk.Label(frame, text="选择要检测编码的文本文件：").pack(anchor='w')
    row1 = ttk.Frame(frame)
    row1.pack(fill='x', pady=(0, 6))
    ent_file = ttk.Entry(row1, width=60)
    ent_file.pack(side='left', fill='x', expand=True, padx=(0, 6))

    def browse():
        path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            ent_file.delete(0, tk.END)
            ent_file.insert(0, path)

    ttk.Button(row1, text="浏览…", command=browse).pack(side='left')
    result_text = scrolledtext.ScrolledText(frame, height=6, width=70, state='disabled', wrap='word')
    result_text.pack(fill='both', expand=True, pady=(0, 6))

    def run():
        path = ent_file.get().strip()
        if not path:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "请先选择或输入文件路径。")
            result_text.config(state='disabled')
            return
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "检测中…")
        result_text.config(state='disabled')

        def do():
            enc, conf = mod_check.run_check(path)
            if enc:
                conf_pct = (conf or 0) * 100
                return f"文件编码格式：{enc}\n检测置信度：{conf_pct:.2f}%"
            return "无法检测文件的编码格式。"

        def done(res):
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            if res[0] == 'err':
                result_text.insert(tk.END, f"错误：{res[1]}")
            else:
                result_text.insert(tk.END, res[1])
            result_text.config(state='disabled')

        run_in_thread(do, done)

    ttk.Button(frame, text="运行检测", command=run).pack(anchor='w')
    return frame


def tab_convert(parent):
    frame = ttk.Frame(parent, padding=10)
    ttk.Label(frame, text="输入文件（要转换编码的 txt）：").pack(anchor='w')
    row1 = ttk.Frame(frame)
    row1.pack(fill='x', pady=(0, 6))
    ent_in = ttk.Entry(row1, width=60)
    ent_in.pack(side='left', fill='x', expand=True, padx=(0, 6))

    def browse():
        path = filedialog.askopenfilename(
            title="选择要转换的文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            ent_in.delete(0, tk.END)
            ent_in.insert(0, path)

    ttk.Button(row1, text="浏览…", command=browse).pack(side='left')
    ttk.Label(frame, text="目标编码（默认 utf-8）：").pack(anchor='w')
    ent_enc = ttk.Entry(frame, width=20)
    ent_enc.insert(0, "utf-8")
    ent_enc.pack(anchor='w', pady=(0, 6))
    result_text = scrolledtext.ScrolledText(frame, height=6, width=70, state='disabled', wrap='word')
    result_text.pack(fill='both', expand=True, pady=(0, 6))

    def run():
        path = ent_in.get().strip()
        enc = (ent_enc.get() or "utf-8").strip() or "utf-8"
        if not path:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "请先选择或输入文件路径。")
            result_text.config(state='disabled')
            return
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "转换中…")
        result_text.config(state='disabled')

        def do():
            return mod_convert.run_convert(path, enc)

        def done(res):
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            if res[0] == 'err':
                result_text.insert(tk.END, f"错误：{res[1]}")
            else:
                ok, msg = res[1]
                result_text.insert(tk.END, msg)
            result_text.config(state='disabled')

        run_in_thread(do, done)

    ttk.Button(frame, text="运行转换", command=run).pack(anchor='w')
    return frame


def tab_epub(parent):
    frame = ttk.Frame(parent, padding=10)
    ttk.Label(frame, text="书名：").pack(anchor='w')
    ent_title = ttk.Entry(frame, width=50)
    ent_title.pack(fill='x', pady=(0, 6))
    ttk.Label(frame, text="作者：").pack(anchor='w')
    ent_author = ttk.Entry(frame, width=50)
    ent_author.pack(fill='x', pady=(0, 6))
    ttk.Label(frame, text="txt 文件路径：").pack(anchor='w')
    row_txt = ttk.Frame(frame)
    row_txt.pack(fill='x', pady=(0, 6))
    ent_txt = ttk.Entry(row_txt, width=50)
    ent_txt.pack(side='left', fill='x', expand=True, padx=(0, 6))

    def browse():
        path = filedialog.askopenfilename(
            title="选择 txt 小说文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            ent_txt.delete(0, tk.END)
            ent_txt.insert(0, path)

    ttk.Button(row_txt, text="浏览…", command=browse).pack(side='left')
    result_text = scrolledtext.ScrolledText(frame, height=6, width=70, state='disabled', wrap='word')
    result_text.pack(fill='both', expand=True, pady=(0, 6))

    def run():
        title = ent_title.get().strip() or "我的书"
        author = ent_author.get().strip() or "作者"
        txt_path = ent_txt.get().strip()
        if not txt_path:
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "请先选择或输入 txt 文件路径。")
            result_text.config(state='disabled')
            return
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "生成 epub 中，请稍候…")
        result_text.config(state='disabled')

        def do():
            return mod_epub.run_txt_to_epub(title, author, txt_path)

        def done(res):
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            if res[0] == 'err':
                result_text.insert(tk.END, f"错误：{res[1]}")
            else:
                out_path, err = res[1]
                if err:
                    result_text.insert(tk.END, err)
                else:
                    result_text.insert(tk.END, f"已生成：\n{out_path}")
            result_text.config(state='disabled')

        run_in_thread(do, done)

    ttk.Button(frame, text="生成 epub", command=run).pack(anchor='w')
    return frame


def main():
    global root
    root = tk.Tk()
    root.title("书工具：检查编码 / 转换编码 / txt 转 epub")
    root.minsize(520, 380)
    nb = ttk.Notebook(root)
    nb.pack(fill='both', expand=True, padx=8, pady=8)
    nb.add(tab_check(nb), text="检查文件编码")
    nb.add(tab_convert(nb), text="转换文件编码")
    nb.add(tab_epub(nb), text="txt 转 epub")
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        if _log_ready and getattr(sys, 'frozen', False):
            log_path = os.path.join(os.path.expanduser('~'), 'Desktop', '书工具_启动错误.txt')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(traceback.format_exc())
        raise
