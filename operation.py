from typing import Dict, List
import time
from math import floor
from config import g_config
from utils import *

def create_file_operation(subject: str, content: str) -> tuple[bool, str]:
    """创建笔记文件"""
    # 验证输入
    if not subject or not content:
        return False, "科目和内容不能为空！"

    # 校验文件名非法
    if not is_valid_filename(subject) or not is_valid_filename(content):
        return False, "科目或内容包含非法字符(<>:\"/\\|?*)！"

    file_path = build_note_path(g_config['root_dir'], subject, content)
    if file_path.exists():
        return False, f"{file_path} 已存在，未执行任何操作"

    try:
        # 创建目录
        parent_dir = file_path.parent
        if parent_dir and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

        # 创建md文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"## {content}\n")

        # 更新data.json
        notes = get_note_list(g_config["data_file"])
        notes.append({
            "content": content,
            "subject": subject,
            "timestamp": floor(time.time())
        })
        update_note_list(g_config["data_file"], notes)

        # 使用封装的函数打开文件
        success, msg = open_file_with_editor(file_path, wait=True)
        if not success:
            return False, msg
        
        # 重新导出文件
        after_modify_operation(False)
        return True, "创建成功！"

    except OSError as error:
        return False, f"创建失败：{error}"


def write_notelist_operation(notes: List[Dict], file_path: Path, title: str = "") -> None:
    """将笔记列表写入文件"""
    with open(file_path, "w", encoding="utf-8") as file:
        if not title:
            file.write(f"## {format_time(None, '%Y-%m-%d')}\n")
        else:
            file.write(f"## {title}\n")

        last_subject = ""
        for note in notes:
            content, subject = note['content'], note['subject']
            if last_subject != subject:
                file.write(f"### [{subject}]({subject})\n")
                last_subject = subject
            file.write(f"- [{content}]({subject}/{content}.md)\n")

def modify_note_operation(subject: str, content: str) -> tuple[bool, str]:
    """修改笔记"""
    file_path = build_note_path(g_config['root_dir'], subject, content)

    # 检查文件是否存在
    if not file_path.exists():
        return False, "笔记文件不存在"

    try:
        # 记录原始修改时间
        original_mtime = file_path.stat().st_mtime

        # 使用封装的函数打开文件并等待编辑完成
        success, msg = open_file_with_editor(file_path, wait=True)
        if not success:
            return False, msg

        # 检查文件是否被修改
        new_mtime = file_path.stat().st_mtime
        if new_mtime == original_mtime:
            return False, "文件未修改，操作取消"

        # 更新JSON时间戳
        notes = get_note_list(g_config["data_file"])
        found = False
        for note in notes:
            if note.get('subject') == subject and note.get('content') == content:
                note['timestamp'] = floor(time.time())
                found = True
                break

        if not found:
            return True, "笔记修改成功，但未在data.json中找到对应条目！"

        # 保存更新后的笔记列表
        update_note_list(g_config["data_file"], notes)

        # 重新导出文件
        after_modify_operation(False)
        return True, "笔记修改成功，时间戳已更新！"

    except Exception as e:
        return False, f"修改失败：{str(e)}"

def delete_note_operation(subject: str, content: str) -> tuple[bool, str]:
    """删除笔记"""
    # 拼接笔记文件完整路径
    file_path = build_note_path(g_config['root_dir'], subject, content)

    # 检查笔记文件是否存在
    if not file_path.exists():
        return False, "笔记文件不存在！"

    try:
        # 删除笔记和空目录
        file_path.unlink()
        subject_dir = g_config['root_dir'] / subject
        if subject_dir.exists() and len(list(subject_dir.iterdir())) == 0:
            subject_dir.rmdir()

        # 更新data.json
        notes = get_note_list(g_config["data_file"])
        original_count = len(notes)
        
        updated_data = [
            note for note in notes
            if not (note['subject'] == subject and note['content'] == content)
        ]

        # 判断是否成功移除数据
        if len(updated_data) >= original_count:
            return True, "笔记文件已删除，但未在data.json中找到对应条目！"

        # 保存更新后的笔记列表
        update_note_list(g_config["data_file"], updated_data)

        # 执行修改后导出操作
        after_modify_operation(False)
        return True, "笔记删除成功！"

    except Exception as e:
        return False, f"删除笔记失败：{str(e)}"

def after_modify_operation(specialized_export: bool) -> None:
    """更新导出文件"""
    target_days=g_config['target_days']
    all_notes = get_note_list(g_config["data_file"])
    current_time = time.time()
    filtered_notes = filter_notes(all_notes, current_time, target_days)

    write_notelist_operation(filtered_notes, g_config["export_file"])
    write_notelist_operation(all_notes, g_config["all_export_file"], "全部")

    if specialized_export:
        open_file_with_editor(g_config["export_file"], wait=True)
