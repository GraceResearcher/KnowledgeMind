import os
import pandas as pd


def find_common_kpi_names(folder_path):
    # 存储所有文件的 kpi_name 列表
    all_kpi_names = None

    # 遍历文件夹下所有的 CSV 文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)

            # 读取 CSV 文件
            df = pd.read_csv(file_path)

            # 提取 kpi_name 列
            kpi_names = set(df['kpi_name'].dropna())  # 去除缺失值并转为集合

            # 对所有文件中的 kpi_name 进行交集操作
            if all_kpi_names is None:
                all_kpi_names = kpi_names
            else:
                all_kpi_names &= kpi_names  # 交集操作

    return all_kpi_names


# 使用方法
folder_path = "../output_anomaly"  # 你可以替换为实际路径
common_kpis = find_common_kpi_names(folder_path)

# 输出共同存在的 kpi_name
if common_kpis:
    print("共同存在的 KPI 名称：", common_kpis)
else:
    print("没有共同的 KPI 名称。")
