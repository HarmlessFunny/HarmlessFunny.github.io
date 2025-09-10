def splitAtFirstSpace(s):
    parts = s.split(maxsplit=1)
    if len(parts) == 1:
        return s, s
    return parts[0], parts[1]

isFirstNoteInput = False
isFirstDateInput = False
print(">>1：写入\n>>2：查询指定日期背诵内容\n>>3：打开存储文件\n>>0：退出\n\n")
while True:
    operation = input("<<")
    if operation == "0":
        print("已退出\n\n")
        break
    elif operation == "1":
        if not isFirstNoteInput:
            print(">>请输入，输入格式：科目(空格)内容，科目和内容当中均不能包含空格和换行符")
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
        