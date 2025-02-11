import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 读取CSV文件
df = pd.read_csv('../output_normal_data/trace_jaeger-span.csv')
# 创建一个有向图
G = nx.DiGraph()

# 通过span_id映射cmdb_id，创建一个字典
span_to_cmdb = dict(zip(df['span_id'], df['cmdb_id']))

# 用于存储依赖关系
dependency_data = []

# 遍历每一行数据，根据parent_span与span_id建立依赖关系
for _, row in df.iterrows():
    cmdb_id = row['cmdb_id']
    span_id = row['span_id']
    parent_span = row['parent_span']

    # 如果parent_span存在，且parent_span与span_id不同，建立依赖关系
    if pd.notna(parent_span) and parent_span != span_id:
        # 查找parent_span对应的cmdb_id
        parent_cmdb_id = span_to_cmdb.get(parent_span)

        if parent_cmdb_id:
            # 保存依赖关系
            dependency_data.append([parent_cmdb_id, cmdb_id])

# 将依赖关系保存为CSV文件
dependency_df = pd.DataFrame(dependency_data, columns=['parent_cmdb_id', 'cmdb_id'])
dependency_df = dependency_df.drop_duplicates()
dependency_df.to_csv('./AIOPS_2022_dependency_relationships.csv', index=False)
