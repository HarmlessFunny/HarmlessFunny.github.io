"""
笔记复习计划管理工具
基于艾宾浩斯遗忘曲线自动安排复习计划
"""

import os
import subprocess
import sys
import time
import configparser
from typing import Dict, List, Tuple

# 配置常量
DEFAULT_CONFIG = {
    'Paths': {'root_dir': './answers', 'export_dir': './answers'},
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
    export_dir = config.get('Paths', 'export_dir')
    if not os.path.isabs(root_dir):
        root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), root_dir)
    if not os.path.isabs(export_dir):
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), export_dir)
    
    return {
        'root_dir': root_dir,
        'export_dir': export_dir,
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

def write_notes(notes: List[Dict], export_dir: str, filename: str, title: str = "") -> None:
    """将笔记列表写入文件"""
    file_path = os.path.join(export_dir, f"{filename}")
    
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

def update_export_files(root_dir: str,export_dir: str, target_days: List[int], specialized: bool) -> None:
    """更新导出文件"""
    all_notes = get_all_notes(root_dir)
    current_time = time.time()
    filtered_notes = filter_notes(all_notes, current_time, target_days)
    
    write_notes(filtered_notes, export_dir, EXPORT_FILE)
    write_notes(all_notes, export_dir, ALL_EXPORT_FILE, "全部")
    
    if specialized:
        print("<< 已生成 export.md 和 allExport.md 文件\n")
        try:
            file_path = os.path.join(export_dir, EXPORT_FILE)
            subprocess.run(f'start /wait "" "{file_path}"', shell=True, check=True)
        except OSError as e:
            print(f">> 无法自动打开文件: {e}")

def write_operation(root_dir: str,export_dir: str, target_days: List[int], repeat: bool) -> None:
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
        update_export_files(root_dir, export_dir, target_days, False)
        if(not repeat):
            break

def git_push_operation(repo_path: str, remote: str, branch: str) -> bool:
    """执行Git提交和推送操作"""
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

def main() -> None:
    """主函数"""
    # 加载配置
    config = load_config()
    root_dir = config['root_dir']
    export_dir = config['export_dir']
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
    write_notes(filtered_notes, export_dir, EXPORT_FILE)
    
    clean_screen_operation(len(filtered_notes), git_enabled, True)
    
    while True:
        print(">> 请输入选项")
        operation = input("<< ").strip()
        
        if operation == "0":
            print(">> 已退出\n")
            break
        elif operation == "1":
            write_operation(root_dir, export_dir, target_days, False)
        elif operation == "1 -r":
            write_operation(root_dir, export_dir, target_days, True)
        elif operation == "2":
            update_export_files(root_dir, export_dir, target_days, True)
        elif operation == "git" and git_enabled:
            print(">> 尝试推送更改...")
            if git_push_operation(repo_path, git_remote, git_branch):
                print(">> 推送成功")
            else:
                print(">> 推送失败")
        elif operation == "cls":
            filtered_notes = filter_notes(get_all_notes(root_dir), current_time, target_days)
            clean_screen_operation(len(filtered_notes), git_enabled, False)
        else:
            print(">> 不是可用的选项\n")
        

if __name__ == "__main__":
    main()