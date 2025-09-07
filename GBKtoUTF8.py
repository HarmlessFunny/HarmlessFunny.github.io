import argparse
import sys
import os

def convert_gbk_to_utf8(file_path):
    """
    将指定的文件从GBK编码转换为UTF-8编码（覆盖原文件）
    """
    try:
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            print(f"错误：文件 '{file_path}' 不存在。")
            return False
            
        # 以二进制模式读取文件内容
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # 尝试用GBK解码内容
        try:
            content = raw_data.decode('gbk')
        except UnicodeDecodeError as e:
            print(f"解码错误：文件 '{file_path}' 可能不是GBK编码。错误详情：{e}")
            return False
        
        # 以UTF-8编码写回原文件（覆盖）
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"成功将文件 '{file_path}' 从GBK转换为UTF-8编码。")
        return True
        
    except Exception as e:
        print(f"转换文件 '{file_path}' 时发生未知错误：{e}")
        return False

def main():
    """主函数，解析命令行参数并执行转换"""
    parser = argparse.ArgumentParser(description='将文件的编码从GBK转换为UTF-8')
    parser.add_argument('file_path', type=str, help='要转换编码的文件路径')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行转换
    success = convert_gbk_to_utf8(args.file_path)
    
    # 根据转换结果设置退出码（0表示成功，非0表示失败）
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    print("hello world")
    main()