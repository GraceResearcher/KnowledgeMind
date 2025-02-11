import pandas as pd
import re
import os
import glob

def Log_Process_Agent(path):
    # 假设日志数据已加载到 log_data DataFrame
    log_data = pd.read_csv(path)

    # 检查 message 是否包含错误或异常关键词
    def contains_error_or_exception(value):
        # 错误或异常关键字列表
        error_keywords = ['error', 'exception', 'nullpointerexception', 'failed', 'failure', 'critical', 'warning']
        value = str(value)
        value = value.lower()  # 转为小写，方便匹配
        return any(keyword in value for keyword in error_keywords)

    # 过滤包含错误或异常信息的日志
    log_data.dropna(axis=1, how='any')
    log_data['is_error_exception'] = log_data['value'].apply(contains_error_or_exception)
    # 输出包含异常的日志条目
    error_logs = log_data[log_data['is_error_exception']]
    count_by_combination = error_logs.groupby(['cmdb_id', 'log_name', 'value']).size().reset_index(name='count')


    return count_by_combination



# 遍历所有故障案例中的 log 开头的 CSV 文件并进行处理
def process_logs(fault_data_root, output_anomaly_log_root):
    # 遍历 output_data 目录下所有故障案例
    for folder_name in os.listdir(fault_data_root):
        folder_path = os.path.join(fault_data_root, folder_name)

        # 如果是文件夹，则处理
        if os.path.isdir(folder_path):
            print(f"处理故障案例: {folder_name}")

            # 创建故障案例名字的子文件夹，用于存储处理后的日志
            case_output_folder = os.path.join(output_anomaly_log_root, folder_name)
            if not os.path.exists(case_output_folder):
                os.makedirs(case_output_folder)

            # 查找文件夹下所有以 log 开头的 CSV 文件
            log_files = glob.glob(os.path.join(folder_path, 'log*.csv'))

            # 如果找到了两个 log 文件
            if len(log_files) == 2:
                for i, log_file in enumerate(log_files):
                    # 将 log 文件路径传递给 Log_Process_Agent 进行处理
                    processed_log_data = Log_Process_Agent(log_file)

                    # 生成存储路径，两个 log 文件分别存储
                    output_file = os.path.join(case_output_folder, f"{folder_name}_log_{i+1}.csv")

                    # 存储处理后的日志数据
                    processed_log_data.to_csv(output_file, index=False)
                    print(f"日志数据已存储为: {output_file}")
            else:
                print(f"警告: {folder_name} 中并未找到两个 log 文件")





# 主函数
def Log_analysis():
    # 假设故障数据目录为 'output_data'，异常输出目录为 'output_anomaly_log'
    fault_data_root = '../output_data'
    output_anomaly_log_root = '../output_anomaly_log'

    # 确保输出目录存在
    if not os.path.exists(output_anomaly_log_root):
        os.makedirs(output_anomaly_log_root)

    # 开始处理日志数据
    process_logs(fault_data_root, output_anomaly_log_root)

# _call()