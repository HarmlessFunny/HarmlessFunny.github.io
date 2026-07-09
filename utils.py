import json
import shutil
import markdown
import os
from pathlib import Path
from typing import Dict, List
from subprocess import run
import time
from error_handler import show_warning, show_error

def check_config(root_dir: Path, target_days: List[int]) -> bool:
    """检查配置有效性"""
    if not root_dir.exists():
        root_dir.mkdir(parents=True, exist_ok=True)

    if not all(isinstance(day, int) and day >= 0 for day in target_days):
        return False

    return True

def convert_md_to_html(root_dir: Path) -> None:
    """将MD文件转换为HTML文件并保持目录结构"""
    html_root = root_dir / "html"

    # 清空或创建HTML目录
    if html_root.exists():
        shutil.rmtree(html_root)
    html_root.mkdir(parents=True, exist_ok=True)

    # 复制目录结构
    for root, dirs, files in os.walk(root_dir):
        # 转换为Path对象
        root_path = Path(root)
        # 跳过HTML目录本身
        if "html" in str(root_path):
            continue

        # 创建对应的HTML目录
        relative_path = root_path.relative_to(root_dir)
        html_dir_path = html_root / relative_path
        html_dir_path.mkdir(parents=True, exist_ok=True)

        # 转换MD文件为HTML
        for file in files:
            if file.endswith('.png'):
                md_png_file_path = root_path / file
                html_png_file_path = html_dir_path / file
                shutil.copy(md_png_file_path, html_png_file_path)
            if file.endswith('.md'):
                md_file_path = root_path / file
                html_file_path = html_dir_path / file.replace('.md', '.html')

                # 尝试不同编码读取文件
                encodings = ['utf-8', 'gbk', 'latin1', 'iso-8859-1']
                md_content = None

                for encoding in encodings:
                    try:
                        with open(md_file_path, 'r', encoding=encoding) as md_file:
                            md_content = md_file.read()
                        break  # 成功读取则跳出循环
                    except UnicodeDecodeError:
                        continue  # 尝试下一个编码
                    except Exception as e:
                        show_warning("读取失败", f"无法读取文件 {md_file_path}：{e}")
                        md_content = None
                        break

                # 如果所有编码都失败，使用替代内容
                if md_content is None:
                    md_content = f"无法读取文件：{md_file_path}"

                # 转换为HTML
                html_content = markdown.markdown(md_content, extensions=[
                        'markdown.extensions.tables',
                        'markdown.extensions.attr_list'
                ])
                with open(html_file_path, 'w', encoding='utf-8') as html_file:
                    if(file=="export.md"):
                        html_content = html_content.replace(".md\">",".html\">")
                    else:
                        html_content = html_content+f"<a href=\"javascript:history.back(-1)\">返回</a>"
                    html_file.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Path(file).stem}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; }}
        a {{ color: #0366d6; text-decoration: none; font-size: 20px;}}
        img {{ margin:0; padding: 0; transform: translateY(-15px); text-align: center;}}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; }}
        code {{ background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f6f8fa; padding: 10px; border-radius: 3px; overflow: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
        table,th,td {{text-align: left; border: #333 1px solid; padding: 5px;}}
        table {{border-collapse: collapse;}}
    </style>
</head>
<body>
{html_content}
</body>
</html>""")
    
def days_difference(later_timestamp: int, earlier_timestamp: int) -> int:
    """计算两个时间戳之间的天数差"""
    day_later = later_timestamp // 86400
    day_earlier = earlier_timestamp // 86400
    return int(day_later - day_earlier)

def is_valid_filename(name: str) -> bool:
    """检查是否为合法的Windows文件名"""
    invalid_chars = '<>:"/\\|?*'
    return not any(char in invalid_chars for char in name)


def filter_notes(notes: List[Dict], target_timestamp: int, target_days: List[int]) -> List[Dict]:
    """根据目标天数筛选笔记"""
    filtered_notes = [
        note for note in notes
        if days_difference(target_timestamp, note['timestamp']) in target_days
    ]
    return filtered_notes


# ==================== 统一数据访问函数 ====================

def load_data_json(data_file: Path) -> Dict:
    """加载data.json文件，如果不存在则返回默认结构"""
    if not data_file.exists():
        return {"note_list": [], "last_subject": ""}
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        show_error("读取失败", f"读取data.json失败：{e}")
        return {"note_list": [], "last_subject": ""}


def save_data_json(data_file: Path, data: Dict) -> bool:
    """保存数据到data.json文件"""
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        show_error("保存失败", f"保存data.json失败：{e}")
        return False


def get_note_list(data_file: Path) -> List[Dict]:
    """获取笔记列表"""
    data = load_data_json(data_file)
    notes = data.get('note_list', [])
    notes.sort(key=lambda x: x["subject"])
    return notes


def update_note_list(data_file: Path, notes: List[Dict]) -> bool:
    """更新笔记列表"""
    data = load_data_json(data_file)
    data['note_list'] = notes
    return save_data_json(data_file, data)


def get_last_subject(data_file: Path) -> str:
    """获取上次使用的科目"""
    data = load_data_json(data_file)
    return data.get('last_subject', "")


def set_last_subject(data_file: Path, subject: str) -> bool:
    """设置上次使用的科目"""
    data = load_data_json(data_file)
    data['last_subject'] = subject
    return save_data_json(data_file, data)


# ==================== 文件路径工具函数 ====================

def build_note_path(root_dir: Path, subject: str, content: str) -> Path:
    """构建笔记文件路径"""
    return root_dir / subject / f"{content}.md"


# ==================== 时间格式化函数 ====================

def format_time(timestamp: float = None, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """格式化时间
    
    Args:
        timestamp: 时间戳，默认为当前时间
        format_str: 格式化模板字符串，默认为 '%Y-%m-%d %H:%M:%S'
        
    Returns:
        格式化后的时间字符串
    """
    if timestamp is None:
        timestamp = time.time()
    return time.strftime(format_str, time.localtime(timestamp))


# ==================== 外部命令执行函数 ====================

def open_file_with_editor(file_path: Path, wait: bool = True) -> tuple[bool, str]:
    """使用系统默认编辑器打开文件
    
    Args:
        file_path: 要打开的文件路径
        wait: 是否等待编辑完成
        
    Returns:
        (success, message): 是否成功及提示信息
    """
    try:
        if wait:
            run(f'start /wait "" "{file_path}"', shell=True, check=True, capture_output=True)
        else:
            run(f'start "" "{file_path}"', shell=True, check=True, capture_output=True)
        return True, ""
    except Exception as e:
        return False, f"打开文件失败：{e}"
