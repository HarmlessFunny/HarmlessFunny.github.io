# config.py
import configparser
import os
from pathlib import Path

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.ini"

# 默认配置
DEFAULT_CONFIG = {
    'Paths': {
        'root_dir': './answers',
        'data_file': 'data.json',
        'export_file': 'export.md',
        'all_export_file': 'allExport.md'
    },
    'ReviewSchedule': {'target_days': '0,1,2,4,7,15,30,60,120,240'},
    'Git': {
        'git_enabled': 'no',
        'git_remote': 'origin',
        'git_branch': 'main'
    },
    'ChemEq': {
        'chem_eq_enabled': 'no'
    }
}

# 全局配置变量（整个项目共用）
g_config = {}

def create_default_config():
    """创建默认配置文件"""
    conf = configparser.ConfigParser()
    
    # 添加各个section
    for section, values in DEFAULT_CONFIG.items():
        conf[section] = values
    
    # 写入文件
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        conf.write(f)

def load_config():
    """加载配置文件，全局只需调用一次"""
    global g_config
    
    # 如果配置文件不存在，创建默认配置
    if not CONFIG_FILE.exists():
        create_default_config()
    
    conf = configparser.ConfigParser()
    conf.read(CONFIG_FILE, encoding="utf-8")
    target_days_str = conf.get('ReviewSchedule', 'target_days')
    root_dir = Path(__file__).parent / conf.get("Paths", "root_dir")

    g_config = {
        "root_dir": root_dir,
        "data_file": root_dir / conf.get('Paths', 'data_file'),
        "export_file": root_dir / conf.get('Paths', 'export_file'),
        "all_export_file": root_dir / conf.get('Paths', 'all_export_file'),
        "target_days": [int(day.strip()) for day in target_days_str.split(',')],
        "git_enabled": conf.getboolean("Git", "git_enabled"),
        "git_remote": conf.get("Git", "git_remote"),
        "git_branch": conf.get("Git", "git_branch"),
        "chem_eq_enabled": conf.getboolean("ChemEq", "chem_eq_enabled"),
    }

# 程序启动时自动加载一次
load_config()
