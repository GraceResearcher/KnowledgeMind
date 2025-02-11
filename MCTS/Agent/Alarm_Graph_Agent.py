#拆解存在告警的树，生成带virtual的告警传播图


import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 读取CSV文件
df = pd.read_csv('AIOPS_2022_dependency_relationships.csv')

# 创建有向图
G = nx.DiGraph()

# 用于存储依赖关系
dependency_data = []

# 遍历每一行数据，根据parent_cmdb_id与cmdb_id建立依赖关系
for _, row in df.iterrows():
    parent_cmdb_id = row['parent_cmdb_id']
    cmdb_id = row['cmdb_id']

    # 如果parent_cmdb_id存在，且parent_cmdb_id与cmdb_id不同，建立依赖关系
    if pd.notna(parent_cmdb_id) and parent_cmdb_id != cmdb_id:
        # 保存依赖关系
        G.add_edge(parent_cmdb_id, cmdb_id)

# 查找根节点（没有任何parent_cmdb_id指向它的cmdb_id）
all_cmdb_ids = set(df['cmdb_id'])
child_cmdb_ids = set(G.nodes)
root_nodes = all_cmdb_ids - child_cmdb_ids  # 没有被任何parent_cmdb_id指向的节点


# 如果有多个根节点，遍历每一个根节点构建拓扑
def build_topology(graph, root_nodes):
    # 存储拓扑结构
    topologies = {}

    for root in root_nodes:
        # 使用深度优先搜索（DFS）构建从root开始的拓扑
        visited = set()
        stack = [root]
        topology = []

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                topology.append(node)
                # 将当前节点的所有子节点添加到栈中
                stack.extend(graph.neighbors(node))

        topologies[root] = topology

    return topologies


# 获取完整的调用拓扑
topologies = build_topology(G, root_nodes)

# 打印拓扑结构
for root, topology in topologies.items():
    print(f"从根节点 {root} 开始的调用拓扑:")
    print(" -> ".join(topology))

# 如果需要绘制整个拓扑图
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
plt.title("完整的调用拓扑")
plt.show()


