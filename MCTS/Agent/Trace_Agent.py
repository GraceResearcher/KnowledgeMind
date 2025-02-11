#分析Trace的latency是否存在异常值以及http状态不正常等信息
import numpy as np
import pandas as pd

MCTS_trace={}
def Trace_Agent():
    # 读取CSV文件
    df = pd.read_csv("G:/2-4/ReST-MCTS-main/MCTS/Agent/AIOPS_2022_dependency_relationships.csv")
    df[['parent_cmdb_id', 'cmdb_id']] = df[['parent_cmdb_id', 'cmdb_id']].replace(r'([a-zA-Z]+)[\d-]*$', r'\1',regex=True)
    df = df.drop_duplicates(keep='first')
    df = df[df['parent_cmdb_id'] != df['cmdb_id']]
    call_dict = df.groupby('parent_cmdb_id')['cmdb_id'].apply(list).to_dict()
    return call_dict

def build_reverse_tree() -> dict:
    tree=Trace_Agent()
    reverse_tree = {}
    for parent, children in tree.items():
        for child in children:
            if child not in reverse_tree:
                reverse_tree[child] = set()  # 改成 set 存储多个父节点
            reverse_tree[child].add(parent)  # 添加父节点
    return reverse_tree



# 测试



