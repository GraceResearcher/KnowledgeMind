#
#这个直接当故障定位入口得了

import pandas as pd
import os


def mapping_path(df):
    # 基础路径
    base_path = "E:\\2022data\\data"
    # 定义路径模板
    folders = [
        "log\\all",
        "metric\\container",
        "metric\\istio",
        "metric\\jvm",
        "metric\\node",
        "metric\\service",
        "trace\\all",
    ]

    # 遍历 DataFrame 构建路径
    all_data = {}
    df["formatted_date"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%Y-%m-%d")
    for _, row in df.iterrows():
        cluster = row["cluster"]
        timestamp = row["formatted_date"]
        cluster_name = cluster.replace("-", "")  # 去掉cluster中的'-'
        base_dir = os.path.join(base_path, f"{timestamp}-{cluster_name}", cluster)

        cluster_data = {}
        cluster = row["cluster"]
        timestamp = row["timestamp"]
        cmdb_id = row["cmdb_id"]
        failure_type = row["failure_type"]
        output_folder = f"{cmdb_id}_{failure_type}_{cluster}_{timestamp}"
        output_path = os.path.join("./output_data", output_folder)
        for folder in folders:
            full_path = os.path.join(base_dir, folder)

            # 检查路径是否存在，尝试读取文件（这里假设是CSV文件）
            if os.path.exists(full_path):
                for file in os.listdir(full_path):
                    if file.endswith(".csv"):
                        file_path = os.path.join(full_path, file)

                        # 读取 CSV 文件
                        try:
                            df_csv = pd.read_csv(file_path)

                            # 筛选 timestamp 在 [timestamp, timestamp + 180] 的数据
                            if "timestamp" in df_csv.columns:
                                df_csv["timestamp"] = pd.to_numeric(df_csv["timestamp"], errors="coerce")
                                if folder == "trace\\all":
                                    df_csv["timestamp"] = (df_csv["timestamp"] / 1000).astype(int)

                                if folder=="log\\all":
                                    filtered_data = df_csv[
                                        (df_csv["timestamp"] >= timestamp) &
                                        (df_csv["timestamp"] <= timestamp + 180)
                                        ]
                                else:
                                    filtered_data = df_csv[
                                        (df_csv["timestamp"] >= timestamp-600) &
                                        (df_csv["timestamp"] <= timestamp + 180)
                                        ]

                                # 保存筛选后的数据到目标文件夹
                                if not filtered_data.empty:
                                    if not os.path.exists(output_path):
                                        os.makedirs(output_path)
                                    output_file = os.path.join(output_path, file)
                                    filtered_data.to_csv(output_file, index=False)
                                    print(f"已保存到: {output_file}")
                        except Exception as e:
                            print(f"读取文件 {file_path} 时出错: {e}")
            else:
                print(f"路径 {full_path} 不存在")

        all_data[cluster] = cluster_data

    # 输出结果示例
    print(all_data)



data_path="E:/2022data/"
ground_truth=data_path+"ground_truth_total.csv"
gt_df=pd.read_csv(ground_truth,encoding="gbk",encoding_errors="ignore")
mapping_path(gt_df)

