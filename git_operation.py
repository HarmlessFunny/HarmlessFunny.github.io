from config import g_config
import subprocess
import time
from tkinter import Toplevel, ttk
import tkinter as tk
from utils import convert_md_to_html
from operation import after_modify_operation
from error_handler import show_warning, show_info, show_error

class GitManager:
    """Git 操作管理类"""
    def __init__(self):
        self.root_dir = g_config["root_dir"]
        self.git_remote = g_config["git_remote"]
        self.git_branch = g_config["git_branch"]
        self.git_enabled = g_config["git_enabled"]

    def show_push_dialog(self, root=None):
        """显示Git推送参数设置弹窗"""
        if not self.git_enabled:
            show_warning("Git未启用", "Git功能未在配置中启用！")
            return

        # 创建弹窗
        dialog = Toplevel()
        dialog.title("Git推送设置")
        dialog.geometry("450x370")
        dialog.transient()
        dialog.grab_set()

        # 绑定关闭事件，当窗口关闭时退出主循环
        if root:
            def on_window_close():
                dialog.destroy()
                root.quit()
            dialog.protocol("WM_DELETE_WINDOW", on_window_close)

        # Commit消息输入
        ttk.Label(dialog, text="提交消息：").pack(padx=10, pady=(15, 5), anchor=tk.W)
        commit_msg_var = tk.StringVar(value=f"自动提交：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        commit_msg_entry = ttk.Entry(dialog, textvariable=commit_msg_var, width=50)
        commit_msg_entry.pack(padx=10, pady=5, fill=tk.X)
        commit_msg_entry.focus()

        # 远程仓库输入
        ttk.Label(dialog, text="远程仓库：").pack(padx=10, pady=(10, 5), anchor=tk.W)
        remote_var = tk.StringVar(value=self.git_remote)
        remote_entry = ttk.Entry(dialog, textvariable=remote_var, width=50)
        remote_entry.pack(padx=10, pady=5, fill=tk.X)

        # 分支输入
        ttk.Label(dialog, text="分支：").pack(padx=10, pady=(10, 5), anchor=tk.W)
        branch_var = tk.StringVar(value=self.git_branch)
        branch_entry = ttk.Entry(dialog, textvariable=branch_var, width=50)
        branch_entry.pack(padx=10, pady=5, fill=tk.X)

        # 选项框
        options_frame = ttk.Frame(dialog)
        options_frame.pack(padx=10, pady=15, fill=tk.X)

        force_push_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="强制推送 (-f)", variable=force_push_var).pack(anchor=tk.W)

        add_all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="添加所有更改 (git add -A)", variable=add_all_var).pack(anchor=tk.W)

        convert_html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="转换Markdown到HTML", variable=convert_html_var).pack(anchor=tk.W)

        # 按钮区域
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(padx=10, pady=10)

        def do_push():
            commit_msg = commit_msg_var.get().strip()
            remote = remote_var.get().strip()
            branch = branch_var.get().strip()
            force_push = force_push_var.get()
            add_all = add_all_var.get()
            convert_html = convert_html_var.get()

            if not commit_msg:
                show_warning("输入错误", "提交消息不能为空！")
                return
            if not remote:
                show_warning("输入错误", "远程仓库不能为空！")
                return
            if not branch:
                show_warning("输入错误", "分支不能为空！")
                return

            dialog.destroy()
            if root:
                root.quit()
            self._execute_push(
                commit_msg=commit_msg,
                remote=remote,
                branch=branch,
                force_push=force_push,
                add_all=add_all,
                convert_html=convert_html
            )

        ttk.Button(btn_frame, text="推送", command=do_push).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=lambda: [dialog.destroy(), root.quit() if root else None]).pack(side=tk.LEFT, padx=5)

    def _execute_push(self, commit_msg: str, remote: str, branch: str, 
                      force_push: bool, add_all: bool, convert_html: bool) -> bool:
        """执行Git推送操作"""
        try:
            after_modify_operation(False)
            # 转换MD到HTML
            if convert_html:
                convert_md_to_html(self.root_dir)
            
            # Git add
            if add_all:
                subprocess.run(
                    ['git', 'add', '-A'], 
                    check=True, 
                    capture_output=True, 
                    cwd=self.root_dir,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Git commit
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                check=True,
                capture_output=True,
                cwd=self.root_dir,
                encoding='utf-8',
                errors='replace',
                text=True
            )
            
            # Git push
            push_cmd = ['git', 'push', remote, branch]
            if force_push:
                push_cmd.append('-f')
            
            subprocess.run(
                push_cmd,
                check=True,
                capture_output=True,
                cwd=self.root_dir,
                encoding='utf-8',
                errors='replace',
                text=True
            )
            
            show_info("成功", "Git推送成功！")
            return True
        
        except subprocess.CalledProcessError as e:
            show_error("Git失败", f"Git操作失败：{e.stderr}")
            return False
        except Exception as e:
            show_error("失败", f"Git推送失败：{e}")
            return False

    def has_unpushed_changes(self) -> bool:
        """检查是否有未推送的修改"""
        if not self.git_enabled:
            return False
        
        try:
            # 检查是否有未提交的修改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                cwd=self.root_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.stdout.strip():
                return True
            
            # 检查是否有未推送的提交
            result = subprocess.run(
                ['git', 'log', f'{self.git_remote}/{self.git_branch}..HEAD'],
                capture_output=True,
                cwd=self.root_dir,
                encoding='utf-8',
                errors='replace'
            )
            
            return bool(result.stdout.strip())
        
        except Exception:
            return False

if __name__ == "__main__":
    # 独立运行时的入口点
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建GitManager实例
    manager = GitManager()
    
    # 直接调用显示推送设置窗口的方法，并传递root参数
    manager.show_push_dialog(root=root)
    
    # 运行主循环
    root.mainloop()
