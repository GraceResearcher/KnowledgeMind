import os
import pandas as pd

# 定义基本路径和子文件夹
base_dir = r"E:\2022data\data\2022-03-19-cloudbed1\cloudbed-1"
folders = [
    "log\\all",
    "metric\\container",
    "metric\\istio",
    "metric\\jvm",
    "metric\\node",
    "metric\\service",
    "trace\\all",
]

# 时间戳范围（两个小时范围）
base_timestamp = 1647662400  # 示例起始时间戳（秒级时间戳）
start_time = base_timestamp
end_time = base_timestamp + 2 * 3600  # 两小时后的时间戳

# 定义目标输出路径
output_base_path = r"E:\output_normal_data"
os.makedirs(output_base_path, exist_ok=True)  # 确保输出目录存在

# 遍历子文件夹路径
for folder in folders:
    full_path = os.path.join(base_dir, folder)

    if os.path.exists(full_path):
        # 遍历该路径下所有 CSV 文件
        for file in os.listdir(full_path):
            if file.endswith(".csv"):
                file_path = os.path.join(full_path, file)

                try:
                    # 读取 CSV 文件
                    df_csv = pd.read_csv(file_path)

                    # 如果没有 timestamp 列，跳过
                    if "timestamp" not in df_csv.columns:
                        print(f"文件 {file_path} 中没有 timestamp 列，跳过")
                        continue

                    # 特殊处理 trace\\all 的 timestamp
                    df_csv["timestamp"] = pd.to_numeric(df_csv["timestamp"], errors="coerce")
                    if folder == "trace\\all":
                        df_csv["timestamp"] = (df_csv["timestamp"] / 1000).astype(int)

                    # 筛选 timestamp 在 [start_time, end_time] 范围内的数据
                    filtered_data = df_csv[
                        (df_csv["timestamp"] >= start_time) &
                        (df_csv["timestamp"] <= end_time)
                        ]

                    # 如果筛选后有数据，将其保存到输出目录
                    if not filtered_data.empty:
                        output_folder = os.path.join(output_base_path, folder.replace("\\", "_"))
                        os.makedirs(output_folder, exist_ok=True)  # 确保文件夹存在

                        output_file = os.path.join(output_folder, file)
                        filtered_data.to_csv(output_file, index=False)
                        print(f"已保存数据到: {output_file}")

                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {e}")
