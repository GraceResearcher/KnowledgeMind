import os
import pandas as pd
import numpy as np
import glob
import json


# 使用三sigma法进行异常检测
def detect_anomalies(data, column_name, mean, std):
    anomalies = data[abs(data[column_name] - mean) > 3*abs(mean)]
    return anomalies


# 读取正常数据并根据cmdb_id和kpi_name生成三sigma均值和标准差
def generate_normal_statistics(normal_data_root, json_file):
    cmdb_kpi_statistics = {}

    # 遍历正常数据目录下的所有CSV文件
    for file in glob.glob(os.path.join(normal_data_root, '*.csv')):
        normal_data = pd.read_csv(file)

        # 按 cmdb_id 和 kpi_name 拆分数据
        for (cmdb_id, kpi_name), cmdb_kpi_data in normal_data.groupby(['cmdb_id', 'kpi_name']):
            mean = cmdb_kpi_data['value'].mean()
            std = cmdb_kpi_data['value'].std()

            # 使用字符串格式化来生成唯一的键
            key = f"{cmdb_id}_{kpi_name}"

            # 存储每个 cmdb_id 和 kpi_name 组合的三sigma统计
            cmdb_kpi_statistics[key] = {'mean': mean, 'std': std}

    # 将统计信息存储到JSON文件中
    with open(json_file, 'w') as f:
        json.dump(cmdb_kpi_statistics, f, indent=4)
    print(f"三sigma统计信息已存储到 {json_file}")


# 读取JSON文件并获取cmdb_id和kpi_name的阈值
def load_normal_statistics_from_json(json_file):
    with open(json_file, 'r') as f:
        cmdb_kpi_statistics = json.load(f)
    return cmdb_kpi_statistics

def extract_service(cmdb_id):
    parts = cmdb_id.split('.')
    return parts[1] if len(parts) > 1 else cmdb_id

# 读取故障数据并进行异常检测
def analyze_fault_data(fault_data_root, output_anomaly_root,output_server):
    # 用于记录异常的cmdb_id和kpi_name组合
    anomalous_combinations = []

    # 遍历所有故障文件夹
    for folder_name in os.listdir(fault_data_root):
        folder_path = os.path.join(fault_data_root, folder_name)
        anomaly_combinations = []
        filtered_dfs = []
        # 如果是文件夹则处理
        if os.path.isdir(folder_path):
            print(f"处理故障案例: {folder_name}")
            for file in glob.glob(os.path.join(folder_path, '*.csv')):
                try:
                    #adservice.ts:8088', 'java_lang_GarbageCollector_LastGcInfo_endTime.MarkSweepCompact'
                    #adservice.ts:8088,java_lang_GarbageCollector_LastGcInfo_memoryUsageAfterGc_max.Metaspace.Copy
                    fault_data = pd.read_csv(file)


                    # 确保时间戳字段是 datetime 格式
                    if 'service' in fault_data.columns and 'count' in fault_data.columns:
                        # 如果包含service和count字段，拆分service为cmdb_id和kpi_name
                        fault_data[['cmdb_id', 'kpi_name']] = fault_data['service'].str.split('-', expand=True)
                        #rr,sr,mrt,count

                        pattern = r'node-\d+\..+'
                        if 'cmdb_id' in fault_data.columns:  # 确保 cmdb_id 存在
                            fault_data_filtered = fault_data[
                                fault_data['cmdb_id'].str.contains(pattern, regex=True, na=False)]
                            if not fault_data_filtered.empty:
                                fault_data_filtered[['server', 'pod']] = fault_data_filtered['cmdb_id'].str.split('.',n=1,expand=True)
                                filtered_dfs.append(fault_data_filtered[['server', 'pod']])




                        fault_data['cmdb_id'] = fault_data['cmdb_id'].apply(extract_service)

                        for k in ["rr","sr","mrt","count"]:
                            fault_data['value'] = fault_data[k]
                            # 找到最早的时间戳
                            earliest_timestamp = fault_data['timestamp'].min()
                            # print(f"最早时间戳: {earliest_timestamp}")


                            # 获取最早时间戳后的600秒的数据作为训练集
                            time_limit = earliest_timestamp + 480
                            train_data = fault_data[
                                (fault_data['timestamp'] >= earliest_timestamp) & (
                                            fault_data['timestamp'] < time_limit)]
                            test_data = fault_data[fault_data['timestamp'] > time_limit]
                            # 按 cmdb_id 和 kpi_name 拆分训练数据，并计算三sigma统计
                            for (cmdb_id, kpi_name), cmdb_kpi_data in train_data.groupby(['cmdb_id', 'kpi_name']):
                                # print(f"处理 cmdb_id: {cmdb_id}, kpi_name: {kpi_name} 的数据")


                                # 计算三sigma的均值和标准差
                                mean = cmdb_kpi_data['value'].mean()
                                std = cmdb_kpi_data['value'].std()
                                test_kpi_data = test_data[
                                    (test_data['cmdb_id'] == cmdb_id) & (test_data['kpi_name'] == kpi_name)]
                                # 对后续数据进行异常检测

                                anomalies_fault = detect_anomalies(test_kpi_data, 'value', mean, std)
                                if not anomalies_fault.empty:
                                    print(f"故障数据中 cmdb_id: {cmdb_id}, kpi_name: {kpi_name}_{k} 存在异常数据点")
                                    anomaly_combinations.append((cmdb_id, kpi_name))

                    else:

                        pattern = r'node-\d+\..+'

                        if 'cmdb_id' in fault_data.columns:  # 确保 cmdb_id 存在
                            fault_data_filtered = fault_data[
                                fault_data['cmdb_id'].str.contains(pattern, regex=True, na=False)]
                            if not fault_data_filtered.empty:
                                fault_data_filtered[['server', 'pod']] = fault_data_filtered['cmdb_id'].str.split('.', n=1, expand=True)
                                filtered_dfs.append(fault_data_filtered[['server', 'pod']])







                        # 找到最早的时间戳
                        earliest_timestamp = fault_data['timestamp'].min()
                        # print(f"最早时间戳: {earliest_timestamp}")
                        fault_data['cmdb_id'] = fault_data['cmdb_id'].apply(extract_service)
                        # 获取最早时间戳后的600秒的数据作为训练集
                        time_limit = earliest_timestamp + 480
                        train_data = fault_data[
                            (fault_data['timestamp'] >= earliest_timestamp) & (fault_data['timestamp'] < time_limit)]
                        test_data = fault_data[fault_data['timestamp'] > time_limit]
                        # 按 cmdb_id 和 kpi_name 拆分训练数据，并计算三sigma统计
                        for (cmdb_id, kpi_name), cmdb_kpi_data in train_data.groupby(['cmdb_id', 'kpi_name']):
                            # print(f"处理 cmdb_id: {cmdb_id}, kpi_name: {kpi_name} 的数据")
                            # if cmdb_id == "adservice.ts:8088" and kpi_name == "java_lang_GarbageCollector_LastGcInfo_endTime.MarkSweepCompact":
                            #     print()
                            # 计算三sigma的均值和标准差
                            mean = cmdb_kpi_data['value'].mean()
                            std = cmdb_kpi_data['value'].std()
                            test_kpi_data = test_data[
                                (test_data['cmdb_id'] == cmdb_id) & (test_data['kpi_name'] == kpi_name)]
                            # 对后续数据进行异常检测

                            anomalies_fault = detect_anomalies(test_kpi_data, 'value', mean, std)
                            if not anomalies_fault.empty:
                                print(f"故障数据中 cmdb_id: {cmdb_id}, kpi_name: {kpi_name} 存在异常数据点")
                                anomaly_combinations.append((cmdb_id, kpi_name))

                            # for (cmdb_id_test, kpi_name_test), cmdb_kpi_test_data in test_data.groupby(
                            #         ['cmdb_id', 'kpi_name']):
                            #     if cmdb_id_test == cmdb_id and kpi_name_test == kpi_name:
                            #         anomalies_fault = detect_anomalies(cmdb_kpi_test_data, 'value', mean, std)
                            #
                            #         if not anomalies_fault.empty:
                            #             print(f"故障数据中 cmdb_id: {cmdb_id}, kpi_name: {kpi_name} 存在异常数据点")
                            #             anomaly_combinations.append((cmdb_id, kpi_name))



                except:
                    print()
            # 如果有异常，存储到output_anomaly文件夹
            if anomaly_combinations:
                output_file = os.path.join(output_anomaly_root, f"{folder_name}_anomalies.csv")
                anomaly_df = pd.DataFrame(anomaly_combinations, columns=['cmdb_id', 'kpi_name'])
                anomaly_df.to_csv(output_file, index=False)
                print(f"异常数据已存储为: {output_file}")


            if filtered_dfs:
                output_file = os.path.join(output_server, f"{folder_name}.csv")
                final_df = pd.concat(filtered_dfs, ignore_index=True).drop_duplicates(keep='first')
                final_df.to_csv(output_file, index=False)
                print(f"所有符合条件的条目已存储到 {output_file}")
            else:
                print("没有找到符合条件的数据")



    return anomalous_combinations


# 主函数
def process_data(fault_data_root, normal_data_root, json_file, output_anomaly_root,output_server):
    # 生成正常数据中的cmdb_id和kpi_name的三sigma均值和标准差，并保存为JSON
    # print("生成正常数据的三sigma统计信息并保存到JSON...")
    # generate_normal_statistics(normal_data_root, json_file)
    #
    # # 从JSON文件中加载正常数据的统计信息
    # print("从JSON文件加载正常数据的三sigma统计信息...")
    # normal_statistics = load_normal_statistics_from_json(json_file)

    # 分析故障数据中的异常并存储结果
    print("开始分析故障数据...")
    anomalous_combinations = analyze_fault_data(fault_data_root, output_anomaly_root,output_server)

    # 输出存在异常的 cmdb_id 和 kpi_name 组合
    if anomalous_combinations:
        print(f"存在异常的 cmdb_id 和 kpi_name 组合: {set(anomalous_combinations)}")
    else:
        print("没有发现异常的 cmdb_id 和 kpi_name 组合")


# 假设故障数据目录为 'output_data'，正常数据目录为 'output_normal_data'，JSON文件路径为 'normal_statistics.json'，异常输出目录为 'output_anomaly'
fault_data_root = '../output_data'
normal_data_root = '../output_normal_data'
json_file = '../normal_statistics.json'
output_anomaly_root = '../output_anomaly'
output_server="../output_data_server"

# 确保输出目录存在
if not os.path.exists(output_anomaly_root):
    os.makedirs(output_anomaly_root)

# 处理数据
process_data(fault_data_root, normal_data_root, json_file, output_anomaly_root,output_server)
