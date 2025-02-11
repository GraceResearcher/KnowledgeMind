from MCTS.Agent.Log_Agent import *
from MCTS.Agent.Trace_Agent import *

import os
import pandas as pd


def read_csv_files_from_directory(directory):
    """读取指定目录下所有 CSV 文件并存储到字典"""
    data_dict = {}
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return data_dict

    for file in os.listdir(directory):
        if file.endswith(".csv"):
            file_path = os.path.join(directory, file)
            try:
                data_dict[file] = pd.read_csv(file_path,encoding="gbk",encoding_errors="ignore")
            except Exception as e:
                print(f"读取文件 {file} 失败: {e}")
    return data_dict


def read_csv_files_from_subdirectories(directory):
    """读取目录下每个子文件夹中的所有 CSV 文件并存储到字典"""
    data_dict = {}
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return data_dict

    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            data_dict[folder] = {}
            for file in os.listdir(folder_path):
                if file.endswith(".csv"):
                    file_path = os.path.join(folder_path, file)
                    try:
                        data_dict[folder][file] = pd.read_csv(file_path,encoding="gbk",encoding_errors="ignore")
                    except Exception as e:
                        print(f"读取文件 {file} 失败: {e}")
    return data_dict





def get_result():
    # 指定目录
    anomaly_dir = "../output_anomaly"
    anomaly_log_dir = "../output_anomaly_log"
    anomaly_data = read_csv_files_from_directory(anomaly_dir)
    anomaly_log_data = read_csv_files_from_subdirectories(anomaly_log_dir)
    return anomaly_data,anomaly_log_data

# get_result()
