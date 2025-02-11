import re
from collections import defaultdict

knowledge_base = [
    {
        "case_name": "adservice-0_k8s容器CPU负载_cloudbed-3_1647742414_anomalies.csv",
        "service": "adservice-0",
        "error_type": "K8s 容器 CPU 负载",
        "key_metrics": [
            "container_cpu_cfs_throttled_periods",
            "container_cpu_cfs_throttled_seconds",
            "container_cpu_system_seconds",
            "container_cpu_usage_seconds",
        ],
        "solution": [
            "增加 CPU 资源分配（调整 K8s requests 和 limits）",
            "检查 HPA（Horizontal Pod Autoscaler）是否生效",
            "排查 CFS 调度策略是否影响性能"
        ]
    },
    {
        "case_name": "adservice-2_k8s文件系统负载_cloudbed-5_1647883412_anomalies.csv",
        "service": "adservice-2",
        "error_type": "K8s 文件系统负载异常",
        "key_metrics": [
            "container_fs_inodes./dev/vda1",
            "container_fs_reads./dev/vda",
            "container_fs_reads_MB./dev/vda",
        ],
        "solution": [
            "检查磁盘 inode 使用率，是否过高",
            "查看 pod 运行环境，是否存在大量小文件导致 inode 耗尽",
            "优化日志或缓存存储方式，减少 inode 占用"
        ]
    },
{
    "case_name": "currencyservice-2_CPU负载故障",
    "service": "currencyservice-2",
    "error_type": "CPU 负载异常",
    "key_metrics": [
        "container_cpu_cfs_periods",
        "container_cpu_cfs_throttled_periods",
        "container_cpu_cfs_throttled_seconds",
        "container_cpu_system_seconds",
        "container_cpu_usage_seconds",
        "container_cpu_user_seconds",
        "container_fs_inodes./dev/vda1",
        "container_fs_reads./dev/vda",
        "container_fs_reads_MB./dev/vda",
        "container_fs_writes./dev/vda",
        "container_fs_writes_MB./dev/vda",
        "container_memory_failures.container.pgfault",
        "container_memory_failures.container.pgmajfault",
        "container_memory_failures.hierarchy.pgfault",
        "container_memory_failures.hierarchy.pgmajfault"
    ],
    "solution": [
        "检查 Kubernetes CPU 限制 (`limits.cpu`)，增加 CPU 资源配额",
        "排查 `cgroup` 是否过度限制 CPU 使用",
        "调整 `HPA` (Horizontal Pod Autoscaler) 策略",
        "分析 `CPU throttling` 数据，查看是否 CPU 限流导致性能下降",
        "优化 `filesystem` 操作，减少 `inode` 及 `I/O` 相关异常",
        "监控 `container_memory_failures`，防止 OOM 触发"
    ]
}
]



def jaccard_similarity(set1, set2):
    """ 计算 Jaccard 相似度 """
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0



def normalize_service_name(service_name):
    """
    归一化服务名，例如：
    - adservice-0、adservice-1、adservice-2 →  adservice
    - adservice2-0 → adservice2
    """
    return re.sub(r"-(\d+)$", "", service_name)



def match_case(service_name, detected_metrics, knowledge_base):
    """
    匹配当前异常数据与知识库案例（支持模糊匹配）
    :param service_name: 当前异常服务名，例如 'adservice-2'
    :param detected_metrics: 当前异常的指标列表
    :param knowledge_base: 知识库案例列表，每个案例是一个字典
    :return: 匹配的案例 或 None
    """
    best_match = None
    best_score = 0

    # 获取归一化的服务名称
    normalized_service = normalize_service_name(service_name)

    for case in knowledge_base:
        case_service_normalized = normalize_service_name(case["service"])

        # 允许模糊匹配（如 adservice-2 也可以匹配 adservice-0）
        if case_service_normalized == normalized_service:
            case_metrics = set(case["key_metrics"])
            detected_metrics_set = set(detected_metrics)

            # 计算 Jaccard 相似度
            similarity = jaccard_similarity(detected_metrics_set, case_metrics)

            # 选择相似度最高的案例
            if similarity > best_score:
                best_score = similarity
                best_match = case

    return best_match, best_score



# 📌 知识库案例（已存在的案例）


# 📌 当前异常数据
# service_name = "adservice-2"  # 允许匹配 adservice-0
# detected_metrics = [
#     "container_cpu_usage_seconds",
#     "container_cpu_user_seconds",
#     "container_fs_inodes./dev/vda1"
# ]

# 进行匹配
# matched_case, match_score = match_case(service_name, detected_metrics, knowledge_base)

# 输出匹配结果
# if matched_case:
#     print(f"📌 **匹配到历史案例:** {matched_case['case_name']}")
#     print(f"🔍 **相似度得分:** {match_score:.2f}")
#     print(f"⚠ **故障类型:** {matched_case['error_type']}")
#     print(f"🔧 **推荐解决方案:**")
#     for solution in matched_case["solution"]:
#         print(f"   - {solution}")
# else:
#     print("⚠ 未找到匹配的历史案例")
