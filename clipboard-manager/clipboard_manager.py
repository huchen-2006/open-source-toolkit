"""剪贴板历史管理器

功能：后台记录剪贴板文本历史，支持搜索、置顶、复制回剪贴板、删除与清空。
用法：python clipboard_manager.py
环境：Windows + Python 3.8 及以上，仅使用标准库（tkinter），无需安装第三方包。
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

DATA_FILE = os.path.join(os.path.expanduser("~"), ".clipboard_history.json")
MAX_ITEMS = 300
POLL_MS = 700
PREVIEW_LEN = 120


class ClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("剪贴板历史管理器")
        self.root.geometry("680x480")
        self.root.minsize(520, 360)

        self.items = self._load()
        self.last_text = ""
        self.recording = True
        self.view = []

        self._build_ui()
        self._refresh()

        # 启动时用当前剪贴板内容作为基准，避免把旧内容重复入库
        try:
            self.last_text = self.root.clipboard_get()
        except tk.TclError:
            self.last_text = ""

        self.root.after(POLL_MS, self._poll)

    # ---------- 界面 ----------
    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(top, text="搜索").pack(side="left")
        self.keyword = tk.StringVar()
        self.keyword.trace_add("write", lambda *_: self._refresh())
        tk.Entry(top, textvariable=self.keyword).pack(side="left", fill="x", expand=True, padx=6)
        self.status = tk.StringVar()
        tk.Label(top, textvariable=self.status, fg="#666666").pack(side="left")

        body = tk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=10)
        self.listbox = tk.Listbox(body, activestyle="dotbox", font=("Consolas", 10))
        scroll = tk.Scrollbar(body, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.listbox.bind("<Double-Button-1>", lambda _e: self._copy_selected())
        self.listbox.bind("<Return>", lambda _e: self._copy_selected())
        self.listbox.bind("<Delete>", lambda _e: self._delete_selected())

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)
        tk.Button(bottom, text="复制到剪贴板", width=14, command=self._copy_selected).pack(side="left")
        tk.Button(bottom, text="置顶 / 取消", width=10, command=self._pin_selected).pack(side="left", padx=6)
        tk.Button(bottom, text="删除", width=8, command=self._delete_selected).pack(side="left")
        tk.Button(bottom, text="清空历史", width=10, command=self._clear_all).pack(side="right")
        self.rec_txt = tk.StringVar(value="暂停记录")
        tk.Button(bottom, textvariable=self.rec_txt, width=10, command=self._toggle).pack(side="right", padx=6)

    # ---------- 数据 ----------
    def _load(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict) and "text" in d]
        except (OSError, ValueError):
            pass
        return []

    def _save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as fh:
                json.dump(self.items[:MAX_ITEMS], fh, ensure_ascii=False, indent=1)
        except OSError as exc:
            self.status.set("保存失败: %s" % exc)

    def _add(self, text):
        for idx, item in enumerate(self.items):
            if item["text"] == text:
                self.items.pop(idx)
                item["time"] = datetime.now().strftime("%m-%d %H:%M")
                self.items.insert(0, item)
                break
        else:
            self.items.insert(0, {
                "text": text,
                "time": datetime.now().strftime("%m-%d %H:%M"),
                "pinned": False,
            })
        del self.items[MAX_ITEMS:]
        self._save()
        self._refresh()

    # ---------- 交互 ----------
    def _poll(self):
        if self.recording:
            try:
                text = self.root.clipboard_get()
            except tk.TclError:
                text = ""
            if text and text != self.last_text and len(text) <= 100000:
                self.last_text = text
                self._add(text)
        self.root.after(POLL_MS, self._poll)

    def _refresh(self):
        keyword = self.keyword.get().strip().lower()
        self.view = []
        for item in self.items:
            if keyword and keyword not in item["text"].lower():
                continue
            self.view.append(item)
        self.view.sort(key=lambda x: not x.get("pinned", False))

        self.listbox.delete(0, tk.END)
        for item in self.view:
            line = item["text"].replace("\r", " ").replace("\n", " ").replace("\t", " ")
            if len(line) > PREVIEW_LEN:
                line = line[:PREVIEW_LEN] + " ..."
            flag = "[置顶] " if item.get("pinned") else ""
            self.listbox.insert(tk.END, "%s%s  |  %s" % (flag, item.get("time", ""), line))
        self.status.set("%d / %d 条" % (len(self.view), len(self.items)))

    def _selected_item(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.view[sel[0]]

    def _copy_selected(self):
        item = self._selected_item()
        if not item:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(item["text"])
        self.last_text = item["text"]
        self.status.set("已复制到剪贴板")

    def _pin_selected(self):
        item = self._selected_item()
        if not item:
            return
        item["pinned"] = not item.get("pinned", False)
        self._save()
        self._refresh()

    def _delete_selected(self):
        item = self._selected_item()
        if not item:
            return
        self.items = [i for i in self.items if i is not item]
        self._save()
        self._refresh()

    def _clear_all(self):
        if not self.items:
            return
        if not messagebox.askyesno("确认", "清空全部历史记录？置顶项也会被清除。"):
            return
        self.items = []
        self._save()
        self._refresh()

    def _toggle(self):
        self.recording = not self.recording
        self.rec_txt.set("继续记录" if not self.recording else "暂停记录")
        self.status.set("已暂停记录" if not self.recording else "记录中")


def main():
    root = tk.Tk()
    ClipboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
