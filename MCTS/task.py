import random
from tasks.science import SearchTask
from MCTS.base import treeNode
from models.get_response import *
from MCTS.mcts import MCTS
from Agent.KnowledgeBase_Agent import *
from MCTS.Agent.Trace_Agent import *


class MCTS_Task(SearchTask):
    def __init__(self, data, propose_method='glm', value_method='glm', branch=2, end_gate=0.9, roll_policy='greedy',
                 roll_branch=1, roll_forward_steps=1, time_limit=None, iteration_limit=None, exploration_constant=0.7,
                 alpha=0.1, inf=1.0, temperature=0.7, max_tokens=2048, seed=170, max_length=2048, truncation=True,
                 do_sample=True, max_new_tokens=256, use_case_prompt=False, use_reflection='simple', low=0, high=1,
                 evaluate='', sample_value='simple', answer=None, verify_method='string', lang='zh', weighted_verify=False,analysis_path=""):
        super().__init__(data, propose_method, value_method)
        assert 0 <= low < high, "Inappropriate value range!"
        self.mode = 'mcts'
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.max_length = max_length
        self.truncation = truncation
        self.do_sample = do_sample
        self.max_new_tokens = max_new_tokens
        self.branch = branch
        self.use_case_prompt = use_case_prompt
        self.low = low
        self.high = high
        self.evaluate = evaluate
        self.end_gate = end_gate
        self.use_reflection = use_reflection
        self.roll_policy = roll_policy
        self.roll_branch = roll_branch
        self.time_limit = time_limit
        self.iteration_limit = iteration_limit
        self.exploration_constant = exploration_constant
        self.roll_forward_steps = roll_forward_steps
        self.alpha = alpha
        self.limit_type = None
        self.INF = inf
        self.node_count = 1
        self.sample_value = sample_value
        self.answer = answer
        self.verify_method = verify_method
        self.reward_model_type = 'prm' if USE_PRM else 'vm'
        self.lang = lang
        self.weighted_verify = weighted_verify
        self.total_Node={}
        self.analysis_path=analysis_path

    def update_count(self):
        self.node_count += 1

    def clear_cache(self):
        self.value_cache = {}
        self.node_count = 1

    def set_limit_type(self):
        if self.time_limit is not None:
            if self.iteration_limit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.limit_type = 'time'
        else:
            if self.iteration_limit is None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if self.iteration_limit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.limit_type = 'iterations'

    def get_next_step_simulation(self,node:treeNode,step_n):#找出当前服务的所有依赖，看这些是否存在调用上的故障
        child_parent_dependency = build_reverse_tree()
        #
        prompt = self.check_surround_microservice(node,list(child_parent_dependency[node.pcd]),self.analysis_path)

        response = get_proposal(prompt, self.propose_method, self.temperature, self.max_tokens, self.seed,
                                self.max_length,
                                self.truncation, self.do_sample, self.max_new_tokens)
        return response



    def evaluate_expand_result(self,nodes):
        prompt=self.evaluate_prompt(nodes)

        response = get_proposal(prompt, self.propose_method, self.temperature, self.max_tokens, self.seed,
                                self.max_length,
                                self.truncation, self.do_sample, self.max_new_tokens)
        return response






    def get_next_step(self,service, y, step_n):
        if self.use_case_prompt:
            prompt = self.single_propose_prompt_wrap(self.question, y, step_n)
        else:
            if self.propose_method == 'gpt':
                # prompt = self.zero_single_propose_wrap_gpt(self.question, y, step_n, self.lang)
                self.total_Node[service]=treeNode(pcd=service, analysis_path=self.analysis_path,depth=step_n)
                prompt = self.zero_single_propose_wrap_gpt_microservice(self.total_Node[service], y, step_n, self.lang)
            elif self.propose_method == 'mistral' or self.propose_method == 'llama':
                prompt = self.zero_single_propose_wrap_mistral(self.question, y, step_n)
            else:
                prompt = self.zero_single_propose_wrap(self.question, y, step_n, self.lang)

        response = get_proposal(prompt, self.propose_method, self.temperature, self.max_tokens, self.seed,
                                self.max_length,
                                self.truncation, self.do_sample, self.max_new_tokens)
        self.total_Node[service].llm_evaluation=response
        return self.total_Node[service]



    def get_next_step_use_reflection(self, y, step_n, reflection):  # 暂不支持 case-prompt
        if self.propose_method == 'gpt' or self.propose_method == 'local':
            propose_prompt = self.zero_single_propose_wrap_use_reflection_gpt(self.question, y, step_n, reflection,
                                                                              self.lang)
        else:
            propose_prompt = self.zero_single_propose_wrap_use_reflection(self.question, y, step_n, reflection,
                                                                          self.lang)
        response = get_proposal(propose_prompt, self.propose_method, self.temperature, self.max_tokens, self.seed,
                                self.max_length,
                                self.truncation, self.do_sample, self.max_new_tokens)
        if not response:
            print('获得下一步失败！\n')
            return ''

        if len(response) > 5:
            response = response[:5]

        p = ''
        for _ in response:
            p = p + _ + ' '
        p = p.strip()

        if self.lang == 'zh':
            if '下一步:' in p:
                stp = p.split('下一步:')[1].strip()
                if len(stp) < 2:
                    print('输出步骤过短！\n')
                    return ''
                if stp in y:
                    print('输出步骤重复！\n')
                    return ''

                revised_ = '步骤' + str(step_n) + ':' + stp
                print(f'标准化后新的步骤:{revised_}\n')
                return revised_ + '\n'

            elif '步骤' in p and ':' in p:
                pre_len = len(p.split(':')[0])
                p_ = p[pre_len:]
                p_ = p_.split('步骤')[0].strip()
                if len(p_) < 3:
                    print('输出步骤过短！\n')
                    return ''
                if p_[1:] in y:
                    print('输出步骤重复！\n')
                    return ''

                revised_ = '步骤' + str(step_n) + p_
                print(f'标准化后新的步骤:{revised_}\n')
                return revised_ + '\n'

            else:
                print('输出格式有误！\n')
                return ''

        else:
            if "Next step:" in p:
                stp = p.split('Next step:')[1].strip()
                if len(stp) < 2:
                    print('输出步骤过短！\n')
                    return ''
                if stp in y:
                    print('输出步骤重复！\n')
                    return ''

                revised_ = 'Step ' + str(step_n) + ': ' + stp
                print(f'标准化后新的步骤:{revised_}\n')
                return revised_ + '\n'

            elif "Step" in p and ":" in p:
                pre_len = len(p.split(':')[0])
                p_ = p[pre_len:]
                p_ = p_.split('Step')[0].strip()
                if len(p_) < 4:
                    print('输出步骤过短！\n')
                    return ''
                p_ = p_[1:].strip()
                if p_ in y:
                    print('输出步骤重复！\n')
                    return ''

                revised_ = 'Step ' + str(step_n) + ': ' + p_
                print(f'标准化后新的步骤:{revised_}\n')
                return revised_ + '\n'

            else:
                print('输出格式有误！\n')
                return ''


    def get_knowledge_reflection(self, node:treeNode, step_n):
        temp=node.get_metric_result()
        best_match,best_score = match_case(node.pcd, node.get_metric_result(), knowledge_base)
        response = []
        if best_match is not None:

            reflection_prompt = self.single_reflection_wrap_simple(node, best_match, best_score, step_n, self.lang)
            cnt = 3

            while not response and cnt:
                response = get_proposal(reflection_prompt, self.propose_method, self.temperature, self.max_tokens,
                                        self.seed,
                                        self.max_length,
                                        self.truncation, self.do_sample, 128)
                cnt -= 1

        p = ''
        for _ in response:
            p = p + _ + ' '
        p = p.strip()

        if self.lang == 'zh':
            if '已解决' in p or '已经解决' in p:
                if step_n > 1:
                    print('此步问题已解决，停止下探。\n')
                    print('标准化后的意见: <end>\n')
                    return '<end>'
            print('标准化后的意见: <continue>\n')
            return '<continue>'

        else:
            if 'unsolved' in p or step_n <= 1:
                print('标准化后的意见: <continue>\n')
                return '<continue>'
            elif 'solved' in p:
                print('标准化后的意见: <end>\n')
                return '<end>'
            else:
                print('标准化后的意见: <continue>\n')
                return '<continue>'




    def get_simple_reflection(self, y, step_n):
        if step_n == 1:
            return '<continue>'
        if self.propose_method in ['local', 'mistral', 'llama'] and self.lang == 'en':
            if 'answer is' in y or '\\boxed' in y:
                return '<end>'
        if self.propose_method == 'mistral':
            reflection_prompt = self.single_reflection_wrap_simple_mistral(self.question, y, step_n)
        else:
            reflection_prompt = self.single_reflection_wrap_simple(self.question, y, step_n, self.lang)#生成指定的prompt
        cnt = 3
        response = []
        while not response and cnt:
            response = get_proposal(reflection_prompt, self.propose_method, self.temperature, self.max_tokens,
                                    self.seed,
                                    self.max_length,
                                    self.truncation, self.do_sample, 128)
            cnt -= 1
        if not response:
            print('获得意见失败！\n')
            return '<end>'

        p = ''
        for _ in response:
            p = p + _ + ' '
        p = p.strip()

        if self.lang == 'zh':
            if '已解决' in p or '已经解决' in p:
                if step_n > 1:
                    print('此步问题已解决，停止下探。\n')
                    print('标准化后的意见: <end>\n')
                    return '<end>'
            print('标准化后的意见: <continue>\n')
            return '<continue>'

        else:
            if 'unsolved' in p or step_n <= 1:
                print('标准化后的意见: <continue>\n')
                return '<continue>'
            elif 'solved' in p:
                print('标准化后的意见: <end>\n')
                return '<end>'
            else:
                print('标准化后的意见: <continue>\n')
                return '<continue>'






    def analyze_service_pod(self,node:treeNode):
        service=node.pcd
        df_metric=node.get_metric_df(service)
        df_log_1,df_log_2=node.get_log_df(service)
        if len(df_metric['cmdb_id'].unique())<4:
            merged_df = pd.concat([df_metric, df_log_1, df_log_2], ignore_index=True)
            cmdb_counts = merged_df['cmdb_id'].value_counts()
            pod = cmdb_counts.idxmax()
            pod_metric = node.get_metric_df(pod)
            pod_log1,pod_log2=node.get_log_df(pod)
            prompt_summary=self.summary_prompt(pod_metric.to_string(index=False),pod_log1.to_string(index=False),pod_log2.to_string(index=False))
            response=get_proposal(prompt_summary, self.propose_method, self.temperature, self.max_tokens, self.seed,
                         self.max_length,
                         self.truncation, self.do_sample, 128)
            print(f'异常pod为:{pod},详细故障类型分析为:',response)
            return f'pod anomaly:{pod}',response
        else:
            pod_metric = node.get_metric_df(service)
            pod_log1, pod_log2 = node.get_log_df(service)
            prompt_summary = self.summary_prompt(pod_metric.to_string(index=False), pod_log1.to_string(index=False),
                                                     pod_log2.to_string(index=False))
            response = get_proposal(prompt_summary, self.propose_method, self.temperature, self.max_tokens, self.seed,
                                    self.max_length,
                                    self.truncation, self.do_sample, 128)
            print(f'异常服务为:{service},详细故障类型分析为:', response)
            return f'service anomaly:{service}',response

    def run(self):
        self.clear_cache()
        self.set_limit_type()
        node, finish, root = MCTS(self,self.analysis_path)
        # vm
        result_service,result_analysis=self.analyze_service_pod(node)

        return result_service, result_analysis
        # return node,finish,root
