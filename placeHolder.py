import tkinter as tk

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="", placeholder_fg="grey", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_fg = placeholder_fg
        self.default_fg = self["fg"]

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        # 初始时显示 placeholder
        self._put_placeholder()

    def _put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_fg

    def _on_focus_in(self, event):
        if self.get() == self.placeholder and self["fg"] == self.placeholder_fg:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg

    def _on_focus_out(self, event):
        if not self.get():
            self._put_placeholder()

    def set_placeholder(self, new_placeholder):
        """更新placeholder文本"""
        # 如果当前显示的是旧的placeholder，先清空
        if self.get() == self.placeholder and self["fg"] == self.placeholder_fg:
            self.delete(0, tk.END)
        self.placeholder = new_placeholder
        # 如果当前为空，显示新的placeholder
        if not self.get():
            self._put_placeholder()

    def show_placeholder(self):
        """显示当前placeholder（用于外部清空后调用）"""
        if not self.get():
            self._put_placeholder()
