import pandas as pd

# 读取CSV文件
df = pd.read_csv("AIOPS_2022_dependency_relationships.csv")
df[['parent_cmdb_id', 'cmdb_id']] = df[['parent_cmdb_id', 'cmdb_id']].replace(r'([a-zA-Z]+)[\d-]*$', r'\1', regex=True)
df=df.drop_duplicates(keep='first')
df=df[df['parent_cmdb_id']!=df['cmdb_id']]
# 假设我们有一个函数可以将服务名称转换为其对应的cmdb_id
def get_cmdb_id_from_service(service_name):
    # 这个函数需要根据你的实际数据来实现
    # 例如，我们假设有一个字典或查询接口来映射服务名称到cmdb_id
    service_to_cmdb_id_map = {
        "service1": "cmdb_id_1",
        "service2": "cmdb_id_2",
        # 添加更多的映射关系
    }
    return service_to_cmdb_id_map.get(service_name)


# 获取服务名称对应的cmdb_id
def get_service_topology(service_name):
    cmdb_id = get_cmdb_id_from_service(service_name)
    if cmdb_id is None:
        print(f"Service '{service_name}' not found.")
        return None


    # 过滤出与该服务相关的所有依赖关系
    # 查找该服务作为parent_cmdb_id和cmdb_id出现的行
    relevant_rows = df[(df['parent_cmdb_id'] == cmdb_id) | (df['cmdb_id'] == cmdb_id)]

    # 递归获取所有依赖关系
    def find_dependencies(service_id):
        # 获取当前服务依赖的所有服务
        children = relevant_rows[relevant_rows['parent_cmdb_id'] == service_id]['cmdb_id'].tolist()
        parents = relevant_rows[relevant_rows['cmdb_id'] == service_id]['parent_cmdb_id'].tolist()

        dependencies = set(children + parents)

        # 对于每一个依赖的服务递归查找其依赖关系
        for dep in dependencies.copy():
            dependencies.update(find_dependencies(dep))

        return dependencies

    # 获取所有依赖
    dependencies = find_dependencies(cmdb_id)

    # 返回依赖关系的拓扑结构（去除原始服务本身）
    return dependencies - {cmdb_id}


# 测试代码
service_name = "service1"
topology = get_service_topology(service_name)
print(f"Dependencies for {service_name}: {topology}")
