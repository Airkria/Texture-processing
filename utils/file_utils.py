# -*- coding: utf-8 -*-
"""文件操作工具模块"""

import os


def get_matched_files(dir1: str, dir2: str, extensions: set) -> list:
    """
    获取两个目录中匹配的文件对

    Args:
        dir1: 第一个目录
        dir2: 第二个目录
        extensions: 文件扩展名集合

    Returns:
        list: 匹配的文件对列表 [(file1, file2), ...]
    """
    files1 = get_files_by_extension(dir1, extensions)
    files2 = get_files_by_extension(dir2, extensions)

    # 按文件名（不含扩展名）匹配
    names1 = {os.path.splitext(os.path.basename(f))[0]: f for f in files1}
    names2 = {os.path.splitext(os.path.basename(f))[0]: f for f in files2}

    matched = []
    for name in names1:
        if name in names2:
            matched.append((names1[name], names2[name]))

    return matched


def get_files_by_extension(directory: str, extensions: set) -> list:
    """
    获取目录中指定扩展名的文件

    Args:
        directory: 目录路径
        extensions: 扩展名集合（如 {'.png', '.jpg'}）

    Returns:
        list: 文件路径列表
    """
    files = []
    if not os.path.isdir(directory):
        return files

    for f in os.listdir(directory):
        ext = os.path.splitext(f)[1].lower()
        if ext in extensions:
            files.append(os.path.join(directory, f))

    return sorted(files)


def ensure_output_dir(output_dir: str) -> bool:
    """
    确保输出目录存在

    Args:
        output_dir: 输出目录路径

    Returns:
        bool: 是否成功
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception:
        return False
