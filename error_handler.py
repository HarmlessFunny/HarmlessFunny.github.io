"""错误处理模块

封装所有的消息框函数，提供统一的错误处理接口
"""

from tkinter.messagebox import askyesno, showinfo, showwarning, showerror


def show_error(title: str, message: str) -> None:
    """显示错误信息
    
    Args:
        title: 错误标题
        message: 错误消息
    """
    showerror(title, message)


def show_warning(title: str, message: str) -> None:
    """显示警告信息
    
    Args:
        title: 警告标题
        message: 警告消息
    """
    showwarning(title, message)


def show_info(title: str, message: str) -> None:
    """显示提示信息
    
    Args:
        title: 提示标题
        message: 提示消息
    """
    showinfo(title, message)


def ask_yes_no(title: str, message: str) -> bool:
    """显示确认对话框
    
    Args:
        title: 对话框标题
        message: 确认消息
        
    Returns:
        bool: 用户是否选择了"是"
    """
    return askyesno(title, message)


def handle_operation_result(success: bool, message: str, success_title: str = "成功", error_title: str = "失败") -> None:
    """处理操作结果
    
    Args:
        success: 操作是否成功
        message: 操作结果消息
        success_title: 成功时的标题
        error_title: 失败时的标题
    """
    if success:
        show_info(success_title, message)
    else:
        show_error(error_title, message)
