import os
import subprocess
from tkinter import Toplevel, ttk
import tkinter as tk
from pathlib import Path
from error_handler import show_warning, show_error, show_info

# 尝试从config导入配置，如果失败则使用默认配置
try:
    from config import g_config
except ImportError:
    # 默认配置
    g_config = {
        "root_dir": Path(__file__).parent / "answers",
        "chem_eq_enabled": True
    }

class ChemEquationManager:
    """化学方程式转图片管理类"""
    def __init__(self):
        self.root_dir = g_config["root_dir"]
        self.chem_eq_enabled = g_config["chem_eq_enabled"]

    def create_equation_tex(self, root=None):
        """创建化学方程式TeX文件并转换为图片"""

        # 创建弹窗
        eq_window = Toplevel()
        eq_window.title("化学方程式转图片")
        eq_window.geometry("500x200")
        eq_window.transient()
        eq_window.grab_set()
        
        # 绑定关闭事件，当窗口关闭时退出主循环
        if root:
            def on_window_close():
                eq_window.destroy()
                root.quit()
            eq_window.protocol("WM_DELETE_WINDOW", on_window_close)

        # 文件名输入
        ttk.Label(eq_window, text="文件名（不带扩展名）：").pack(padx=10, pady=10)
        filename_var = tk.StringVar()
        filename_entry = ttk.Entry(eq_window, textvariable=filename_var, width=30)
        filename_entry.pack(padx=10, pady=5, fill=tk.X)
        filename_entry.focus()

        # 核心创建逻辑
        def create_tex():
            filename = filename_var.get().strip()
            if not filename:
                show_warning("输入错误", "文件名不能为空！")
                return

            # 构建路径
            assets_dir = self.root_dir / "化学" / "assets"
            tex_path = assets_dir / f"{filename}.tex"

            # 创建目录
            try:
                assets_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                show_error("创建失败", f"创建目录失败：{e}")
                eq_window.destroy()
                return

            # 创建TeX模板文件
            try:
                with open(tex_path, "w", encoding="utf-8") as f:
                    f.write("""\\documentclass[border=1pt]{standalone}
\\usepackage[UTF8]{ctex}
\\usepackage{extarrows}
\\begin{document}
    $
    
    $
\\end{document}""")
            except OSError as e:
                show_error("创建失败", f"创建文件失败：{e}")
                eq_window.destroy()
                return

            # 打开文件编辑
            try:
                subprocess.run(f'start /wait "" "{tex_path}"', shell=True, check=True)
            except Exception as e:
                show_error("编辑失败", f"打开文件失败：{e}")
                eq_window.destroy()
                return

            # 执行转换（texpng 命令）
            try:
                subprocess.run(
                    ['texpng', f'{filename}.tex'],
                    check=True,
                    capture_output=True,
                    cwd=assets_dir,
                    encoding='utf-8',
                    errors='replace'
                )
            except subprocess.CalledProcessError as e:
                show_error("转换失败", f"texpng转换失败：{e.stderr}")
                eq_window.destroy()
                return

            show_info("成功", f"转换成功！\n图片路径：{assets_dir / f'{filename}.png'}")
            eq_window.destroy()

        # 确认按钮
        ttk.Button(eq_window, text="创建并编辑", command=create_tex).pack(padx=10, pady=10)
        # 取消按钮
        ttk.Button(eq_window, text="取消", command=eq_window.destroy).pack(padx=10, pady=10)

if __name__ == "__main__":
    # 独立运行时的入口点
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建ChemEquationManager实例
    manager = ChemEquationManager()
    
    # 直接调用创建化学方程式的方法，并传递root参数
    manager.create_equation_tex(root=root)
    
    # 运行主循环
    root.mainloop()
