import os
import sys
import time

root_dir = ".\\answers"
target_days = [0,1,2,4,7,15,30,60,120,240]
tsnow = time.time()

def createFile(path, title):
    if os.path.exists(path):
        print(f">>'{path}' 已存在，未执行任何操作")
        return False
    try:
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            print(f">>已创建父目录: {parent_dir}")
        with open(path, 'w', encoding='utf-8') as f:
            filename = os.path.basename(path)
            f.write("## "+title+"\n")
        print(f">>文件创建成功: {path}")
        return True
    except OSError as e:
        print(f">>创建失败: {e}", file=sys.stderr)
        return False

def splitAtFirstSpace(s):
    parts = s.split(maxsplit=1)
    if len(parts) == 1:
        return s, s
    return parts[0], parts[1]

def DaysDifference(tsLate, tsEarly):
    dayLate = tsLate // 86400
    dayEarly = tsEarly // 86400
    return int(abs(dayLate - dayEarly))

def getNotes():
    """
    遍历根目录下的每个子文件夹，获取所有.md文件的信息
    :param root_dir: 根目录路径
    :return: 包含文件信息的字典列表
    """
    files_info = []
    for entry in os.listdir(root_dir):
        sub_dir_path = os.path.join(root_dir, entry)
        if os.path.isdir(sub_dir_path):
            for file in os.listdir(sub_dir_path):
                if file.endswith('.md'):
                    file_path = os.path.join(sub_dir_path, file)
                    file_info = {
                        'content': os.path.splitext(file)[0],
                        'subject': entry,
                        'last_modified': os.path.getmtime(file_path)
                    }
                    files_info.append(file_info)
    return files_info

def filterNotes(tsTarget, isFilter = True):
    notes = getNotes()
    filteredNotes = [note for note in notes if not isFilter or DaysDifference(tsTarget, note['last_modified']) in target_days]
    return filteredNotes

def writeNotes(notes,filename):
    with open(root_dir+"\\"+filename+".md", "w", encoding="utf-8") as file:
        human_time = time.strftime('%Y年%m月%d日', time.localtime(tsnow))
        file.write(f"## {human_time}\n")
        lastSubject=""
        for note in notes:
            content, subject = note['content'], note['subject']
            if not lastSubject == subject:
                file.write(f"### [{subject}]({subject})\n")
                lastSubject=subject
            file.write(f"- [{content}]({subject}/{content}.md)\n")

isFirstNoteInput = False
isFirstDateInput = False
print(">>1：写入\n>>2：查询指定日期背诵内容\n>>3：打开存储文件\n>>0：退出\n")
while True:
    tsNow = time.time()
    filteredNotes = filterNotes(tsNow)
    writeNotes(filteredNotes,"export2")
    operation = input("<<")
    if operation == "0":
        print("已退出\n")
        break
    elif operation == "1":
        if not isFirstNoteInput:
            print(">>请输入，输入格式：科目(空格)内容，科目中不能包含空格和换行符")
        else:
            print(">>请输入")
        line = input("<<")
        if line.strip() == "":
            print(">>不可输入空字符串\n")
            continue
        elif len(line) == 1 and line.isdigit():
            print(">>不可输入数字\n")
            continue
        subject, content = splitAtFirstSpace(line)
        path = root_dir+"\\"+subject+"\\"+content+".md"
        createFile(path, content)
        os.system(path)
        print("<<已完成\n")
    else:
        print(">>不是可用的数字\n")
        