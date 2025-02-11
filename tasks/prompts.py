zero_single_proposal_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识确定根因服务和原因。输入中可能包括了一些已有的解答步骤，请你在这些步骤的基础上继续完成解答。

如果输入中没有提供任何已有步骤，你需要基于当前服务相关的Metric和Log等基础Agent提供的分析结果给出当前服务根因得分的答案。如果提供了部分服务的分析结果，你需要按照已有步骤的思路和先验知识，输出当前服务为根因的得分。
输出格式限定为: 

如果定位根因为service，则给出当前service下每个pod的严重程度，例如:<root_service_start>adservice<root_service_end>，该服务下故障最严重的pod为adservice-0

“1.当前服务可能为根因的得分是:<root_score_start>1-10之间的数字<root_score_end>“
“2.<root_cause_start>故障详细信息<root_cause_end>”

你的输出必须为一个完整的步骤，其中应该包括详细的分析、推理、选择答案等。
下面是先验知识和当前服务的分析结果，请你按照规定格式进行输出。
'''






#这个是用来做单步调用的prompt，确定
zero_single_proposal_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识确定根因服务和原因。输入中可能包括了一些已有的解答步骤，请你在这些步骤的基础上继续完成解答。

如果输入中没有提供任何已有步骤，你需要基于当前服务相关的Metric和Log等基础Agent提供的分析结果给出当前服务根因得分的答案。如果提供了部分服务的分析结果，你需要按照已有步骤的思路和先验知识，输出当前服务为根因的得分。
输出格式限定为: 

如果定位根因为service，则给出当前service下每个pod的严重程度，例如:<root_service_start>adservice<root_service_end>，该服务下故障最严重的pod为adservice-0

“1.当前服务可能为根因的得分是:<root_score_start>1-10之间的数字<root_score_end>“
“2.<root_cause_start>故障详细信息<root_cause_end>”

你的输出必须为一个完整的步骤，其中应该包括详细的分析、推理、选择答案等。
下面是先验知识和当前服务的分析结果，请你按照规定格式进行输出。
'''

zero_single_proposal_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识总结当前服务的异常信息。输入中包括了一些已有的解答步骤，请你在这些步骤的基础上继续完成解答。

如果输入中没有提供任何已有步骤，你需要基于当前服务相关的Metric和Log等基础Agent提供的分析结果给出当前服务根因得分的答案。如果提供了部分服务的分析结果，你需要按照已有步骤的思路和先验知识，总结当前服务的异常状态。
输出格式限定为: 

“1.<root_cause_start>异常信息总结，应包含该服务具体的异常信息与Log和Metric异常条目<root_cause_end>”

你的输出必须为一个完整的步骤，其中应该包括详细的分析、推理、总结等。
下面是先验知识和当前服务的分析结果，请你按照规定格式进行输出。
'''


zero_single_proposal_prompt_gpt_microservice_bak = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识总结当前服务的异常信息。输入中包括了一些已有的解答步骤，请你在这些步骤的基础上继续完成解答。

如果输入中没有提供任何已有步骤，你需要基于当前服务相关的Metric和Log等基础Agent提供的分析结果给出当前服务根因得分的答案。如果提供了部分服务的分析结果，你需要按照已有步骤的思路和先验知识，输出当前服务为根因的得分。
输出格式限定为: 

“1.当前服务的异常得分为:<root_score_start>1-10之间的数字<root_score_end>“
“2.<root_cause_start>异常信息总结<root_cause_end>”

你的输出必须为一个完整的步骤，其中应该包括详细的分析、推理、选择答案等。
下面是先验知识和当前服务的分析结果，请你按照规定格式进行输出。
'''




surround_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识给当前服务的异常程度打分，打分要基于当前服务的异常情况和对周围服务异常行为的影响进行打分。输入中包含当前服务的异常行为和所有调用该服务的服务的异常行为，
周围服务的异常行为越强，则评分应该越高，评分在1-10之间。输出格式限定为: 

“1.当前服务的得分是:<root_score_start>1-10之间的数字<root_score_end>“
“2.<root_cause_start>分析的具体过程<root_cause_end>”

你的输出必须为一个完整的步骤，其中应该包括详细的分析、推理、选择答案等。
'''



evaluate_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识和当前所有服务的异常信息，给当前所有服务的异常程度进行打分并输出得分最高的服务，某个服务的异常的Metric和Log条目数量越多则异常程度越高，某个服务的Metric和Log的分析结果同时出现异常应该比只出现Metric或Log异常具备更高的分数。输入中包含所有服务的异常行为，评分要在1-8之间，且得分最高的要比其他分数至少高2分。输出包含所有服务的评分，输出格式限定为: 
“1.<root_service_start>服务1<root_service_end>:<root_score_start>9<root_score_end>“



你的输出必须为一个完整的步骤，其中应该包括详细的分析和推理过程并给出该服务获得最高分的原因。
'''



summary_type_prompt_gpt_microservice = '''
你是一个运维工程师，现在系统出现了故障，你需要基于你的已有知识和当前服务的异常信息，来评估可能的异常类型，该服务某个类型的异常的Metric和Log条目数量越多则可能是该类故障异常程度越高，例如cpu指标异常数量为10，则top1为cpu故障。
已有知识:日志中的
1.java.lang.NullPointerException
2.io.grpc.internal.ServerImpl$JumpToApplicationThreadServerStreamListener$1HalfClosed
3.java.net.SocketTimeoutException
4.severity: warning, message: failed to retrieve ads
等异常条目均由网络异常导致


输出格式限定为: 
“top 1.<root_type_start>CPU故障，故障详细分析...<root_type_end>“
“top 2.<root_type_start>故障详细分析...<root_type_end>“
“top 3.<root_type_start>故障详细分析...<root_type_end>“


你的输出必须为一个完整的步骤，其中应该包括详细的分析和推理过程,注意如果无法得到top2和top3则只输出top1即可。
'''










#这个是用来做单步调用的prompt，确定
naive_prompt_gpt_microservice = f'''
你是一名经验丰富的运维工程师，当前系统发生了故障。你的任务是基于已有知识，结合多个基础 Agent 所提供的总结信息，分析并确定根因服务或节点，并给出故障的详细类型。

请注意：

1.根因可能存在于 pod、service 或 node。以adservice为例,adservice为service; adservice-0、adservice-1、adservice-2、adservice2-0为4个pod。请注意不要给错具体的根因
2.service 与 pod 的关系：每个 service 下包含多个 pod，例如 adservice 下可能有 adservice-0、adservice-1、adservice-2、adservice2-0。
3.如果某个 service 下面多个 pod 都出现异常，则该 service 更有可能是根因，而非单个 pod。
4.请综合多个基础 Agent 提供的信息，进一步分析故障的根因及类型。
'''








single_reflection_prompt_simple_microservice = '''
你是一个运维知识专家，给定一个系统故障场景和一些相应的解答步骤（不一定完整）。你需要判断给定的步骤是否已经解决问题并给出答案。

你需要区分两种情况给出对应的输出:
1，如果给定的步骤已经在知识库中找到了完全匹配的答案，那么请直接输出:“问题已解决，并输出知识库中所给出的根因服务和故障原因，以及可能的解决方案”，不需要输出其他内容。
2，如果给定步骤还没有在知识库中找到完全匹配的答案，那么请直接输出:“问题未解决”即可，不需要输出其他内容。
注意，如果现有步骤所分析的服务没有在知识库中找出具有完全相同所有异常信息的案例，那么应当视为未解决。
'''











critic_simplified_microservice = '''
你的任务是根据给定的评分规则和已有的解答步骤，判断这些步骤能否顺利解决该问题并输出分数。打分应该是0到1之间的小数，如果已有步骤全部不正确（每一步都错了）则是 0 分。如果已有步骤全部正确，且计算出了答案则是 1 分。已有步骤错的越多，分数越接近 0 分。已有步骤越接近最终答案，分数越接近 1 分。没有发现异常信息的步骤一般应该给分低。
先生成分析，后给出分数，你的分析和给分应该全部基于输入给定的步骤和关键规则，不要继续生成下面的步骤。请学习以下样例。

输入:
问题: 该系统的故障服务和故障类型是什么。
关键规则: 
1.异常次数与调用次数的比例越接近1，分数应该越高
2.每个步骤中只要出现告警信息则认为该步骤的探索正确。 
3.若某个步骤中的服务存在异常次数与调用次数的比例为1且当前服务位于整个调用链的最底层则当前步骤所给出的异常服务是故障服务，应该给出很高的分数。
4.若最新的步骤所检查的服务不存在告警，则给出较低的评分。
已有步骤:
根据故障传播依赖图所构建的传播关系进行逐步分析，分析链路如下: ts-preserve-service->ts-notification-service->ts-assurance-service
步骤1: 分析ts-preserve-service,当前服务出现Metric异常和Log异常，请求Metric Agent和Log Agent的结果来分析Metric Agent分析结果:存在CPU_Usage
步骤2: 分析ts-preserve-service
步骤3: 分析链路ts-preserve-service到ts-travel-service
输出:
分析: 已有步骤中的第1步是正确的，它所分析的服务存在异常信息。然而，这只是分析的一部分，还需要进一步的步骤来判断相邻服务是否存在故障。因此，已有步骤还没有推断出答案。
分数: 0.1

输入:
问题: 该系统的故障服务和故障类型是什么。
已有步骤:
步骤1: 
输出:
分析: 已有步骤中的第1步是正确的，它所分析的服务存在异常信息。然而，这只是分析的一部分，还需要进一步的步骤来判断相邻服务是否存在故障。因此，已有步骤还没有推断出答案。
分数: 0.2

输入:
问题: 求函数$f(x)=1+x^2$在区间$[-1,2]$上的平均值。
已有步骤:
步骤1: 利用定积分求解平均值：我们可以利用定积分来求解函数在区间 $[-1,2]$ 上的平均值。
步骤2: 首先，我们需要计算定积分 $\\int_{-1}^{2} (1+x^2) dx=6$。
步骤3: 然后，我们可以利用定积分的性质，将定积分的结果除以区间的长度，即 $\\frac{\\int_{-1}^{2} (1+x^2) dx}{3}$，这应该就是函数在区间上的平均值。
步骤4: 计算上面的式子，得到结果为$\\frac{\\int_{-1}^{2} (1+x^2) dx}{3}=\\frac{6}{3}=2$，因此函数的平均值为2。

步骤1: 利用定积分求解平均值：我们可以利用定积分来求解函数在区间 $[-1,2]$ 上的平均值。
步骤2: 首先，我们需要计算定积分 $\\int_{-1}^{2} (1+x^2) dx=6$。
步骤3: 然后，我们可以利用定积分的性质，将定积分的结果除以区间的长度，即 $\\frac{\\int_{-1}^{2} (1+x^2) dx}{3}$，这应该就是函数在区间上的平均值。
步骤4: 计算上面的式子，得到结果为$\\frac{\\int_{-1}^{2} (1+x^2) dx}{3}=\\frac{6}{3}=2$，因此函数的平均值为2。
输出:
分析: 所有步骤均推导正确，且已有步骤已经找出了根因为ts-assurance-service，可以得到满分1分。
分数: 1

下面给定一个问题和已有的步骤，给出分析和打分。注意不要在分析中输出接下来的步骤，评分应该完全依据输入给定的步骤。
输出格式限定为:”分析:...\n分数:...“，其中...表示省略的输出内容，这是你需要填充的部分。

输入:
问题: '''










self_critic_prompt = '''
Given a science problem and an existing solution, your task is to evaluate the correctness of the solution and provide an evaluation score. 
Your output should be a decimal ranging from 0 to 1. The more correct the solution is, the higher your evaluation score should be.

Problem:'''
