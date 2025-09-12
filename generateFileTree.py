#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用于递归扫描指定目录下所有文件和文件夹，生成文件树JSON
用法：python generateFileTree.py > filelist.json

过滤规则：
- 不扫描images文件夹
- 不扫描根目录下的文件（只扫描子文件夹中的文件）
- 不扫描.git目录
"""

import os
import json
import sys

def should_skip_directory(dir_name, base_path):
    """
    判断是否应该跳过某个目录
    
    Args:
        dir_name (str): 目录名称
        base_path (str): 基础路径
    
    Returns:
        bool: 是否跳过该目录
    """
    # 跳过images文件夹
    if dir_name.lower() == 'images':
        return True
    
    # 跳过.git目录
    if dir_name == '.git':
        return True
    
    # 跳过其他需要过滤的目录（可根据需要添加）
    return False

def should_include_file(file_path, root_dir):
    """
    判断是否应该包含某个文件
    
    Args:
        file_path (str): 文件路径
        root_dir (str): 根目录路径
    
    Returns:
        bool: 是否包含该文件
    """
    # 获取文件相对于根目录的路径
    rel_path = os.path.relpath(file_path, root_dir)
    
    # 如果文件直接在根目录下，跳过
    if os.path.dirname(rel_path) == '.':
        return False
    
    # 如果文件路径包含images，跳过
    if 'images' in rel_path.split(os.sep):
        return False
    
    return True

def walk_directory(dir_path, base='', root_dir=None):
    """
    递归遍历目录，生成文件列表（带过滤功能）
    
    Args:
        dir_path (str): 要遍历的目录路径
        base (str): 相对基础路径
        root_dir (str): 根目录路径（用于过滤判断）
    
    Returns:
        list: 包含文件信息的字典列表
    """
    if root_dir is None:
        root_dir = dir_path
    
    results = []
    
    try:
        items = os.listdir(dir_path)
    except PermissionError:
        print(f"警告: 无权限访问目录 {dir_path}", file=sys.stderr)
        return results
    except FileNotFoundError:
        print(f"错误: 目录不存在 {dir_path}", file=sys.stderr)
        return results
    
    for item in items:
        item_path = os.path.join(dir_path, item)
        rel_path = os.path.join(base, item).replace('\\', '/')
        
        try:
            if os.path.isdir(item_path):
                # 检查是否应该跳过这个目录
                if should_skip_directory(item, base):
                    continue
                
                # 如果是目录，递归遍历
                results.extend(walk_directory(item_path, rel_path, root_dir))
            else:
                # 检查是否应该包含这个文件
                if not should_include_file(item_path, root_dir):
                    continue
                
                # 如果是文件，添加到结果列表
                folder_path = base.replace('\\', '/')
                results.append({
                    "folder": folder_path,
                    "name": item
                })
        except PermissionError:
            print(f"警告: 无权限访问 {item_path}", file=sys.stderr)
        except OSError as e:
            print(f"警告: 访问 {item_path} 时出错: {e}", file=sys.stderr)
    
    return results

def main():
    """主函数"""
    # 获取命令行参数，如果没有指定则使用当前目录
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    # 检查目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误: 目录 '{root_dir}' 不存在", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isdir(root_dir):
        print(f"错误: '{root_dir}' 不是一个目录", file=sys.stderr)
        sys.exit(1)
    
    # 获取绝对路径
    root_dir = os.path.abspath(root_dir)
    
    # 遍历目录生成文件列表
    files = walk_directory(root_dir, '', root_dir)
    
    # 输出JSON格式的结果
    print(json.dumps(files, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
