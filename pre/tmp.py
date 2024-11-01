import json
import os
import shutil
from shutil import Error, SameFileError

def copy_folders_based_on_jsonl(jsonl_file, json_key, category_key, base_source_dir, base_target_dir):
    """
    根据JSONL文件中的指定键值，将对应的文件夹从源目录复制到目标目录。
    文件夹会按照另一项（category_key）的值归类为不同的子目录。
    如果目标文件夹或文件已经存在，将跳过该文件夹或文件的复制。

    :param jsonl_file: 待处理的JSONL文件路径
    :param json_key: JSON对象中用于路径选择的键
    :param category_key: JSON对象中用于归类的键
    :param base_source_dir: 源文件夹的基础路径
    :param base_target_dir: 目标文件夹的基础路径
    """
    
    # 确保目标目录存在
    if not os.path.exists(base_target_dir):
        os.makedirs(base_target_dir)

    with open(jsonl_file, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                # 解析每一行的JSON对象
                data = json.loads(line.strip())
                if json_key in data and category_key in data:
                    folder_name = data[json_key]
                    category_name = data[category_key]
                    
                    source_folder = os.path.join(base_source_dir, folder_name)
                    # 根据 category_name 归类到不同的子目录
                    target_folder = os.path.join(base_target_dir, category_name, folder_name)
                    
                    if os.path.exists(source_folder):
                        if os.path.exists(target_folder):
                            print(f"目标文件夹已存在，跳过: {target_folder}")
                        else:
                            try:
                                os.makedirs(os.path.dirname(target_folder), exist_ok=True)
                                shutil.copytree(source_folder, target_folder)
                                print(f"复制文件夹: {source_folder} -> {target_folder}")
                            except PermissionError:
                                print(f"权限被拒绝: {source_folder}")
                            except FileNotFoundError:
                                print(f"文件或文件夹不存在: {source_folder}")
                            except SameFileError:
                                print(f"源和目标是同一个文件夹: {source_folder}")
                            except Error as e:
                                print(f"复制过程中发生错误: {e}")
                    else:
                        print(f"源文件夹不存在: {source_folder}")
                else:
                    print(f"JSON中未找到键: {json_key} 或 {category_key}")
            except json.JSONDecodeError:
                print(f"无法解析JSON: {line.strip()}")

# 使用范例
jsonl_file = '/data/wubenlong/work/project/Auto_RT/bench/finalbench.jsonl'  # JSONL文件路径
json_key = 'name'   # JSON中用于路径选择的键
category_key = 'type'  # JSON中用于归类的键
base_source_dir = '/data/wubenlong/work/vulhub'  # 源文件夹基础路径
base_target_dir = '/data/wubenlong/work/project/Auto_RT/bench'  # 目标文件夹基础路径

copy_folders_based_on_jsonl(jsonl_file, json_key, category_key, base_source_dir, base_target_dir)