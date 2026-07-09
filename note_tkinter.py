"""
笔记复习计划管理工具（Tkinter版）
基于艾宾浩斯遗忘曲线自动安排复习计划
"""

import os
import time
import tkinter as tk
from tkinter import ttk
from typing import Any
from placeHolder import PlaceholderEntry
from utils import *
from config import g_config
from git_operation import GitManager
from chem_equation import ChemEquationManager
from operation import *
from error_handler import show_error, show_warning, show_info, ask_yes_no, handle_operation_result



class NoteManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("艾宾浩斯笔记复习管理工具")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 检查配置有效性
        self.config_valid = check_config(g_config['root_dir'], g_config['target_days'])
        if not self.config_valid:
            show_error("配置错误", f"目标天数配置无效，请检查 config.ini")
            self.root.quit()
            return

        # 确保data.json存在（使用新的工具函数）
        if not g_config["data_file"].exists():
            save_data_json(g_config["data_file"], {"note_list": [], "last_subject": ""})
                
        # 初始化独立功能模块
        self.git_manager = GitManager()
        self.chem_eq_manager = ChemEquationManager()

        # 初始化last_subject和当前筛选科目
        self.last_subject = get_last_subject(g_config["data_file"])
        self.current_filter_subject = "全部"
        
        # 创建界面
        self.create_ui()
        # 初始化笔记列表
        self.refresh_note_list()
        # 初始化状态信息
        self.update_status_bar()


    def create_ui(self):
        """创建界面布局"""
        # 整体布局：顶部操作栏 + 左侧笔记列表 + 右侧功能区 + 底部状态栏
        # 1. 顶部操作栏
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        # 功能按钮组
        self.btn_modify_note = ttk.Button(self.top_frame, text="修改笔记", command=self.modify_note_handler)
        self.btn_modify_note.pack(side=tk.LEFT, padx=5)

        self.btn_delete_note = ttk.Button(self.top_frame, text="删除笔记", command=self.delete_note_handler)
        self.btn_delete_note.pack(side=tk.LEFT, padx=5)

        if g_config['chem_eq_enabled']:
            self.btn_chem_eq = ttk.Button(self.top_frame, text="化学方程式转图片", command=self.chem_eq_manager.create_equation_tex)
            self.btn_chem_eq.pack(side=tk.LEFT, padx=5)

        self.btn_re_export = ttk.Button(self.top_frame, text="重新导出文件", command=self.re_export_handler)
        self.btn_re_export.pack(side=tk.LEFT, padx=5)

        if g_config['git_enabled']:
            self.btn_git_push = ttk.Button(self.top_frame, text="推送到Git", command=self.git_manager.show_push_dialog)
            self.btn_git_push.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = ttk.Button(self.top_frame, text="刷新列表", command=self.refresh_note_list)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        # 2. 主内容区（左右分栏）
        self.main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧：笔记列表
        self.left_frame = ttk.Frame(self.main_frame, width=400)
        self.main_frame.add(self.left_frame, weight=1)

        # 筛选区域
        self.filter_frame = ttk.Frame(self.left_frame)
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.filter_frame, text="筛选科目：").pack(side=tk.LEFT, padx=5)
        self.filter_subject_var = tk.StringVar(value="全部")
        self.filter_combobox = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_subject_var,
            state="readonly",
            width=20
        )
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", 
            lambda event: (
                setattr(self, 'current_filter_subject', self.filter_subject_var.get()),
                self.refresh_note_list(),
                self.update_status_bar()
            )
        )

        # 笔记列表Treeview
        self.note_tree = ttk.Treeview(
            self.left_frame,
            columns=("subject", "content", "timestamp"),
            show="headings",
            selectmode="extended"
        )
        
        # 绑定点击事件，点击空白区域取消选择
        self.note_tree.bind("<Button-1>", 
            lambda event: (
                (item := self.note_tree.identify_row(event.y)),
                self.note_tree.selection_remove(self.note_tree.selection()) if not item else None
            )
        )
        self.note_tree.heading("subject", text="科目")
        self.note_tree.heading("content", text="笔记内容")
        self.note_tree.heading("timestamp", text="创建/更新时间")
        self.note_tree.column("subject", width=90)
        self.note_tree.column("content", width=170)
        self.note_tree.column("timestamp", width=110)

        # 列表滚动条
        self.tree_scroll = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.note_tree.yview)
        self.note_tree.configure(yscrollcommand=self.tree_scroll.set)

        # 创建右键菜单
        self.create_context_menu()

        self.note_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # 右侧：功能面板（默认显示新建笔记面板）
        self.right_frame = ttk.Frame(self.main_frame, width=600)
        self.main_frame.add(self.right_frame, weight=2)

        # 功能面板容器（用于切换不同功能面板）
        self.panel_container = ttk.Frame(self.right_frame)
        self.panel_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 绑定点击事件，点击空白处取消输入框聚焦
        self.panel_container.bind("<Button-1>", 
            lambda event: (
                (widget := self.panel_container.winfo_containing(event.x_root, event.y_root)),
                self.panel_container.focus_set() if widget == self.panel_container else None
            )
        )

        # 显示新建笔记面板
        self.show_new_note_panel()

        # 3. 底部状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

    def create_context_menu(self):
        """创建右键菜单"""
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        
        # 绑定右键菜单到笔记列表
        self.note_tree.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 清空现有菜单
        self.context_menu.delete(0, tk.END)
        
        # 检查是否有选中的笔记
        selected_items = self.note_tree.selection()
        
        if not selected_items:
            # 未选中时的菜单
            self.context_menu.add_command(label="新建笔记", command=lambda:(
                # 显示新建笔记面板
                self.show_new_note_panel(),
                # 聚焦到内容输入框
                self.content_placeholder_entry.focus()
            ))
            if g_config['git_enabled']:
                self.context_menu.add_command(label="推送到Git", command=self.git_manager.show_push_dialog)
        else:
            # 选中时的菜单
            self.context_menu.add_command(label="修改笔记", command=self.modify_note_handler)
            self.context_menu.add_command(label="删除笔记", command=self.delete_note_handler)
        
        # 显示菜单
        self.context_menu.post(event.x_root, event.y_root)

    def show_new_note_panel(self):
        """显示新建笔记面板"""
        # 清空容器
        for widget in self.panel_container.winfo_children():
            widget.destroy()

        # 面板标题
        title_label = ttk.Label(self.panel_container, text="新建笔记", font=("SimHei", 16))
        title_label.pack(anchor=tk.W, pady=10)

        # 科目输入区
        subject_frame = ttk.Frame(self.panel_container)
        subject_frame.pack(fill=tk.X, pady=5)

        ttk.Label(subject_frame, text="科目：").pack(side=tk.LEFT, padx=5)
        self.subject_var = tk.StringVar()
        placeholder = self.last_subject if self.last_subject else "科目"
        self.subject_placeholder_entry = PlaceholderEntry(subject_frame, textvariable=self.subject_var, width=30, placeholder=placeholder)
        self.subject_placeholder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 内容输入区
        content_frame = ttk.Frame(self.panel_container)
        content_frame.pack(fill=tk.X, pady=5)

        ttk.Label(content_frame, text="内容：").pack(side=tk.LEFT, padx=5)
        self.content_placeholder_entry = PlaceholderEntry(content_frame, width=50)
        self.content_placeholder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)



        # 操作按钮
        btn_frame = ttk.Frame(self.panel_container)
        btn_frame.pack(pady=10)

        self.btn_create = ttk.Button(btn_frame, text="创建笔记", command=self.create_note_handler)
        self.btn_create.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = ttk.Button(btn_frame, text="清空输入", command=self.clear_note_input)
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

        # 提示信息
        tip_label = ttk.Label(
            self.panel_container,
            text=f"提示：科目/内容不能包含非法字符(<>:\"/\\|?*)",
            foreground="gray"
        )
        tip_label.pack(anchor=tk.W, pady=5)

    def create_note_handler(self):
        """创建笔记处理函数"""
        subject = self.subject_var.get().strip()
        content = self.content_placeholder_entry.get().strip()

        success, msg = create_file_operation(subject, content)

        if success:
            # 更新last_subject
            if subject:
                self.last_subject = subject
                # 更新placeholder
                self.subject_placeholder_entry.set_placeholder(subject)
                # 保存到data.json（使用新的工具函数）
                if not set_last_subject(g_config["data_file"], subject):
                    show_error("保存失败", "更新last_subject失败")
            
            self.refresh_note_list()
            self.update_status_bar()
            show_info("成功", msg)
        else:
            show_error("失败", msg)

        # 清空所有输入
        self.clear_note_input()

    def clear_note_input(self):
        """清空笔记输入框"""
        self.content_placeholder_entry.delete(0, tk.END)
        self.subject_var.set("")
        # 显示科目输入框的placeholder
        self.subject_placeholder_entry.show_placeholder()
        self.content_placeholder_entry.focus()

    def modify_note_handler(self):
        """修改笔记处理函数"""
        # 选中校验
        selected_items = self.note_tree.selection()
        if not selected_items:
            show_warning("选择错误", "请先选中要修改的笔记！")
            return

        # 获取选中数据
        item = selected_items[0]
        values = self.note_tree.item(item, "values")
        subject = values[0]
        content = values[1]

        if not ask_yes_no("确认修改", f"是否要修改笔记：{subject}/{content}？"):
            return

        success, msg = modify_note_operation(subject, content)

        if success:
            self.refresh_note_list()
            self.update_status_bar()
            show_info("成功", msg)
        else:
            if "未修改" not in msg:
                show_error("失败", msg)
            else:
                show_info("提示", msg)

    def delete_note_handler(self):
        """删除笔记处理函数"""
        # 获取选中的笔记
        selected_items = self.note_tree.selection()
        if not selected_items:
            show_warning("选择错误", "请先选中要删除的笔记！")
            return

        # 只处理第一个选中项
        item = selected_items[0]
        values = self.note_tree.item(item, "values")
        subject = values[0]
        content = values[1]

        # 二次确认
        if not ask_yes_no("确认删除", f"确定要删除笔记：{subject}/{content}？此操作不可恢复！"):
            return

        success, msg = delete_note_operation(subject, content)

        # 根据结果显示提示并刷新界面
        if success:
            # 刷新界面列表和状态栏
            self.refresh_note_list()
            self.update_status_bar()
            show_info("成功", msg)
        else:
            if "未找到" in msg or "未在" in msg:
                show_warning("警告", msg)
            else:
                show_error("删除失败", msg)

    def re_export_handler(self):
        """重新导出文件处理函数"""
        try:
            after_modify_operation(True)
            show_info("成功", f"已重新生成{g_config["export_file"]}和{g_config["all_export_file"]}文件！")
        except Exception as e:
            show_error("导出失败", f"重新导出文件失败：{e}")

    def refresh_note_list(self):
        """刷新笔记列表"""
        # 清空现有内容
        for item in self.note_tree.get_children():
            self.note_tree.delete(item)

        # 获取所有笔记
        self.all_notes = get_note_list(g_config["data_file"])
        
        # 更新筛选科目下拉菜单
        subjects = sorted(list(set([note['subject'] for note in self.all_notes])))
        subjects = ["全部"] + subjects
        self.filter_combobox['values'] = subjects
        
        # 根据筛选条件过滤笔记
        filtered_notes = self._filter_notes_by_subject(self.all_notes)
        
        # 插入到列表中
        for note in filtered_notes:
            # 使用新的时间格式化函数
            time_str = format_time(note['timestamp'], '%Y-%m-%d %H:%M')
            self.note_tree.insert("", tk.END, values=(note['subject'], note['content'], time_str))

    def _filter_notes_by_subject(self, notes):
        """根据当前筛选科目过滤笔记"""
        if self.current_filter_subject != "全部":
            return [note for note in notes if note['subject'] == self.current_filter_subject]
        return notes
    
    def update_status_bar(self):
        """更新状态栏信息"""
        # 使用缓存的笔记列表，避免重复读取
        notes = getattr(self, 'all_notes', get_note_list(g_config["data_file"]))
        note_count = len(notes)
        
        # 获取当日复习笔记数
        current_time = time.time()
        today_notes = filter_notes(notes, current_time, g_config['target_days'])
        today_count = len(today_notes)
        
        # 获取筛选后的笔记数（复用过滤函数）
        filtered_notes = self._filter_notes_by_subject(notes)
        if self.current_filter_subject != "全部":
            filter_info = f" | 筛选科目：{self.current_filter_subject} ({len(filtered_notes)}条)"
        else:
            filter_info = ""

        # 使用新的时间格式化函数
        self.status_var.set(
            f"当前时间：{format_time()} | 总笔记数：{note_count} | 今日需复习：{today_count}{filter_info} | 笔记根目录：{g_config['root_dir']}"
        )

    def on_closing(self):
        """窗口关闭事件处理"""
        # 检查是否有未推送的修改
        if self.git_manager.has_unpushed_changes():
            if ask_yes_no("未推送的修改", "检测到有未推送到Git的修改，是否现在推送？"):
                # 用户选择推送
                success = self.git_manager.show_push_dialog()
                if not success:
                    # 推送失败，阻止关闭
                    return
            else:
                # 用户选择不推送
                self.root.destroy()
        
        # 没有未推送的修改或已成功推送，允许关闭
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = NoteManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    print("当前工作目录：", os.getcwd())
    main()
