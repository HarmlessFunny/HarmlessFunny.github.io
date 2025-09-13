"""
笔记复习计划管理工具
基于艾宾浩斯遗忘曲线自动安排复习计划
"""

import os
import subprocess
import sys
import time
import configparser
import shutil
from typing import Dict, List, Tuple

import markdown

# 配置常量
DEFAULT_CONFIG = {
    'Paths': {'root_dir': './answers'},
    'ReviewSchedule': {'target_days': '0,1,2,4,7,15,30,60,120,240'},
    'Git': {
        'enabled': 'no',
        'remote_name': 'origin',
        'branch': 'main'
    }
}

CONFIG_FILE = 'config.ini'
EXPORT_FILE = 'export.md'
ALL_EXPORT_FILE = 'allExport.md'


def load_config() -> Dict[str, List]:
    """加载配置文件，如果不存在则创建默认配置"""
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        # 创建默认配置文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as config_file:
            config.write(config_file)
        print(">> 已创建默认配置文件 config.ini")
    
    # 处理目标天数
    target_days_str = config.get('ReviewSchedule', 'target_days')
    target_days = [int(day.strip()) for day in target_days_str.split(',')]
    
    # 处理 Git
    git_enabled = config.get('Git', 'enabled') == 'yes'
    git_remote = config.get('Git', 'remote_name')
    git_branch = config.get('Git', 'branch')

    # 处理目录
    root_dir = config.get('Paths', 'root_dir')
    if not os.path.isabs(root_dir):
        root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), root_dir)
    
    return {
        'root_dir': root_dir,
        'target_days': target_days,
        'git_enabled': git_enabled,
        'git_remote': git_remote,
        'git_branch': git_branch
    }

def check_config(root_dir: str, target_days: List[int]) -> bool:
    """检查配置有效性"""
    if not os.path.exists(root_dir):
        os.makedirs(root_dir, exist_ok=True)
        print(f">> 已创建笔记根目录: {root_dir}")
    
    if not all(isinstance(day, int) and day >= 0 for day in target_days):
        print(">> 错误: target_days 应包含非负整数", file=sys.stderr)
        return False
    
    return True

def is_valid_filename(name: str) -> bool:
    """检查是否为合法的Windows文件名"""
    invalid_chars = '<>:"/\\|?*'
    return not any(char in invalid_chars for char in name)

def create_file(file_path: str, title: str) -> bool:
    """创建笔记文件"""
    if os.path.exists(file_path):
        print(f">> '{file_path}' 已存在，未执行任何操作")
        return False
    
    try:
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            print(f">> 已创建父目录: {os.path.basename(parent_dir)}")
        
        with open(file_path, 'w', encoding='utf-8') as file:
            filename = os.path.basename(file_path)
            file.write(f"## {title}\n")
        
        print(f">> 文件创建成功: {filename}")
        return True
    except OSError as error:
        print(f">> 创建失败: {error}", file=sys.stderr)
        return False

def split_at_first_space(text: str) -> Tuple[str, str]:
    """在第一个空格处分割字符串"""
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[1]

def days_difference(later_timestamp: int, earlier_timestamp: int) -> int:
    """计算两个时间戳之间的天数差"""
    day_later = later_timestamp // 86400
    day_earlier = earlier_timestamp // 86400
    return int(abs(day_later - day_earlier))

def get_all_notes(root_dir: str) -> List[Dict]:
    """获取所有笔记信息"""
    notes_info = []
    
    try:
        for entry in os.listdir(root_dir):
            sub_dir_path = os.path.join(root_dir, entry)
            if os.path.isdir(sub_dir_path):
                for note_file in os.listdir(sub_dir_path):
                    if note_file.endswith('.md'):
                        note_path = os.path.join(sub_dir_path, note_file)
                        note_info = {
                            'content': os.path.splitext(note_file)[0],
                            'subject': entry,
                            'last_modified': os.path.getmtime(note_path)
                        }
                        notes_info.append(note_info)
    except OSError as error:
        print(f">> 读取目录失败: {error}", file=sys.stderr)
    
    return notes_info

def filter_notes(notes: List[Dict], target_timestamp: int, target_days: List[int]) -> List[Dict]:
    """根据目标天数筛选笔记"""
    filtered_notes = [
        note for note in notes 
        if days_difference(target_timestamp, note['last_modified']) in target_days
    ]
    return filtered_notes

def write_notes(notes: List[Dict], root_dir: str, filename: str, title: str = "") -> None:
    """将笔记列表写入文件"""
    file_path = os.path.join(root_dir, f"{filename}")
    
    with open(file_path, "w", encoding="utf-8") as file:
        if not title:
            human_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            file.write(f"## {human_time}\n")
        else:
            file.write(f"## {title}\n")
        
        last_subject = ""
        for note in notes:
            content, subject = note['content'], note['subject']
            if last_subject != subject:
                file.write(f"### [{subject}]({subject})\n")
                last_subject = subject
            file.write(f"- [{content}]({subject}/{content}.md)\n")

def update_export_files(root_dir: str, target_days: List[int], specialized: bool) -> None:
    """更新导出文件"""
    all_notes = get_all_notes(root_dir)
    current_time = time.time()
    filtered_notes = filter_notes(all_notes, current_time, target_days)
    
    write_notes(filtered_notes, root_dir, EXPORT_FILE)
    write_notes(all_notes, root_dir, ALL_EXPORT_FILE, "全部")
    
    if specialized:
        print("<< 已生成 export.md 和 allExport.md 文件\n")
        try:
            file_path = os.path.join(root_dir, EXPORT_FILE)
            subprocess.run(f'start /wait "" "{file_path}"', shell=True, check=True)
        except OSError as e:
            print(f">> 无法自动打开文件: {e}")

def write_operation(root_dir: str, target_days: List[int], repeat: bool) -> None:
    """处理写入操作"""
    is_first_input = True
    last_subject = ""  # 新增：记录最后使用的科目
    
    while True:
        if not is_first_input:
            # 根据是否有最后科目显示不同提示
            if last_subject:
                print(f">> 请输入笔记内容（默认科目: {last_subject}），输入格式：内容 或 科目 内容，按0取消")
            else:
                print(">> 请输入笔记，输入格式：科目(空格)内容，按0取消")
        else:
            print(">> 请输入笔记，输入格式：科目(空格)内容，按0取消")
            is_first_input = False
        
        user_input = input("<< ").strip()

        # 情况1：空输入
        if not user_input:
            print(">> 不可输入空字符串\n")
            continue
        
        # 情况2：取消操作
        if user_input == '0':
            print(">> 已取消输入笔记\n")
            break
        
        # 情况3：输入科目切换命令（例如 "> 数学"）
        if user_input.startswith('>'):
            new_subject = user_input[1:].strip()
            if is_valid_filename(new_subject):
                last_subject = new_subject
                print(f">> 已设置默认科目: {last_subject}\n")
                continue
            else:
                print(">> 错误: 科目包含非法字符(<>:\"/\\|?*)\n")
                continue
        
        # 情况4：只输入内容（使用最后科目）
        if ' ' not in user_input and last_subject:
            subject = last_subject
            content = user_input
            print(f">> 使用默认科目: {subject}")
        
        # 情况5：正常输入"科目 内容"
        else:
            subject, content = split_at_first_space(user_input)
            # 更新最后使用的科目
            last_subject = subject
        
        # 验证和文件创建
        if not is_valid_filename(subject) or not is_valid_filename(content):
            print(">> 错误: 科目或内容包含非法字符(<>:\"/\\|?*)\n")
            continue

        file_path = os.path.join(root_dir, subject, f"{content}.md")
        
        if create_file(file_path, content):
            # 在Windows上打开文件
            try:
               subprocess.run(f'start /wait "" "{file_path}"', shell=True, check=True)
            except OSError as e:
                print(f">> 无法自动打开文件: {e}")
        # 更新导出文件
        update_export_files(root_dir, target_days, False)
        if(not repeat):
            break

def git_push_operation(root_dir: str, repo_path: str, remote: str, branch: str) -> bool:
    """执行Git提交和推送操作"""
    
    convert_md_to_html(root_dir)
    try:
        # 添加所有更改
        subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
        
        # 提交更改
        commit_message = f"自动提交：{time.strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=repo_path, check=True)
        
        # 推送到远程仓库
        result = subprocess.run(['git', 'push', remote, branch], cwd=repo_path, capture_output=True, text=True)
        
        if "Everything up-to-date" in result.stdout:
            print(">> 无新更改可推送")
            return False
        print(f">> 成功推送到 {remote}/{branch}")
        return True
    except subprocess.CalledProcessError as e:
        print(f">> Git操作失败: {e.stderr}", file=sys.stderr)
        return False

def clean_screen_operation(notes_number: int, git_enabled: bool, is_first_input: bool) -> None:
    """初始输出"""
    human_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    if not is_first_input:
        os.system("cls")
    print(f">> {human_time}，共有{notes_number}条笔记")
    print(">> 1：新建笔记（-r重复输入）")
    print(">> 2：生成导出文件")
    if git_enabled:
        print(">> git：推送到 Github")
    print(">> cls：清屏")
    print(">> 0：退出")

    print()

def convert_md_to_html(root_dir: str) -> None:
    """将MD文件转换为HTML文件并保持目录结构"""
    html_root = os.path.join(root_dir, "html")
    
    # 清空或创建HTML目录
    if os.path.exists(html_root):
        shutil.rmtree(html_root)
    os.makedirs(html_root, exist_ok=True)
    
    # 复制目录结构
    for root, dirs, files in os.walk(root_dir):
        # 跳过HTML目录本身
        if "html" in root:
            continue
            
        # 创建对应的HTML目录
        relative_path = os.path.relpath(root, root_dir)
        html_dir_path = os.path.join(html_root, relative_path)
        os.makedirs(html_dir_path, exist_ok=True)
        
        # 转换MD文件为HTML
        for file in files:
            if file.endswith('.md'):
                md_file_path = os.path.join(root, file)
                html_file_path = os.path.join(html_dir_path, file.replace('.md', '.html'))
                
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
                        print(f">> 无法读取文件 {md_file_path}: {e}")
                        md_content = None
                        break
                
                # 如果所有编码都失败，使用替代内容
                if md_content is None:
                    md_content = f"# 文件读取错误\n\n无法正确读取原始文件内容"
                    print(f">> 警告: 无法读取文件 {md_file_path}，使用替代内容")
                
                # 转换Markdown为HTML
                try:
                    html_content = markdown.markdown(md_content)
                except Exception as e:
                    html_content = f"<h1>Markdown转换错误</h1><p>{str(e)}</p>"
                    print(f">> 警告: 转换文件 {md_file_path} 时出错: {e}")
                
                # 写入HTML文件
                try:
                    with open(html_file_path, 'w', encoding='utf-8') as html_file:
                        if(file=="export.md"):
                            html_content = html_content.replace(".md\">",".html\">")
                        else:
                            html_content = html_content+f"<a href=\"{os.path.join("..", "export.html")}\">返回</a>"
                        html_file.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.splitext(file)[0]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        ul, ol {{ padding-left: 20px; }}
        code {{ background-color: #f6f8fa; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f6f8fa; padding: 10px; border-radius: 3px; overflow: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>""")
                except Exception as e:
                    print(f">> 无法写入HTML文件 {html_file_path}: {e}")
    
    print(f">> 已将所有MD文件转换为HTML文件，存放在: {html_root}")

def main() -> None:
    """主函数"""
    # 加载配置
    config = load_config()
    root_dir = config['root_dir']
    target_days = config['target_days']
    git_enabled = config['git_enabled']
    git_remote = config['git_remote']
    git_branch = config['git_branch']
    

    # Git 初始化
    if git_enabled:
        repo_path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(os.path.join(repo_path, '.git')):
            print(">> 初始化Git仓库...")
            subprocess.run(['git', 'init'], cwd=repo_path, check=True)
    
    # 检查配置
    if not check_config(root_dir, target_days):
        print(">> 配置错误，程序终止", file=sys.stderr)
        sys.exit(1)
    
    # 初始导出
    current_time = time.time()
    filtered_notes = filter_notes(get_all_notes(root_dir), current_time, target_days)
    write_notes(filtered_notes, root_dir, EXPORT_FILE)
    
    clean_screen_operation(len(filtered_notes), git_enabled, True)
    
    while True:
        print(">> 请输入选项")
        operation = input("<< ").strip()
        
        if operation == "0":
            print(">> 已退出\n")
            break
        elif operation == "1":
            write_operation(root_dir, target_days, False)
        elif operation == "1 -r":
            write_operation(root_dir, target_days, True)
        elif operation == "2":
            update_export_files(root_dir, target_days, True)
        elif operation == "git" and git_enabled:
            print(">> 尝试推送更改...")
            if git_push_operation(root_dir, repo_path, git_remote, git_branch):
                print(">> 推送成功\n")
            else:
                print(">> 推送失败\n")
        elif operation == "cls":
            filtered_notes = filter_notes(get_all_notes(root_dir), current_time, target_days)
            clean_screen_operation(len(filtered_notes), git_enabled, False)
        else:
            print(">> 不是可用的选项\n")
        

if __name__ == "__main__":
    main()
    # convert_md_to_html("./answers")