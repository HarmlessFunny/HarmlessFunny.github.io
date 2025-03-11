import os

def traverse_directory(path):
    with open('.\\temp.txt','w',encoding="utf-8") as f:
        f.truncate()
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if root == ".\\answers\\assets":
                continue
            full_path = os.path.join(root, file)
            file_list.append(full_path)
            print(root[-2:],file[:-3])
            with open('.\\temp.txt','a',encoding="utf-8") as f:
                lines = [root[-2:],file[:-3],"\n"]
                f.writelines(lines)
    return file_list

if __name__ == "__main__":
    files = traverse_directory(".\\answers")