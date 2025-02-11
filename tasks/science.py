import re
import os
from tasks.prompts import *
from MCTS.Agent.generate_analysis import get_result
from MCTS.base import treeNode
# data: question: str
# mode: 'cot', 'tot', 'mcts'
# method: 'glm', 'gpt', 'local'
class SearchTask(object):
    def __init__(self, data, propose_method='glm', value_method='glm'):
        super().__init__()
        self.question = data
        self.propose_method = propose_method
        self.value_method = value_method
        self.value_cache = {}

    def clear_cache(self):
        self.value_cache = {}


    @staticmethod
    def zero_single_propose_wrap_gpt(x: str, y: str = '', step: int = 0, lang: str = 'zh') -> str:
        print('\n', '==============================', 'proposal', '==============================', '\nstep: ', step)
        print('propose_prompt: \n', x + '\n已有步骤:\n' + y + '基于以上步骤，可能的当前步骤解法是:\n')
        if lang == 'zh':
            if not y:
                y = '无\n'
            # prompt = zero_single_proposal_prompt_gpt + x + '\n已有步骤:\n' + y + '\n输出:'

            #这块要把当前服务的告警的信息加进去,让LLM选择调用哪些Agent做分析
            prompt = zero_single_proposal_prompt_gpt_microservice + x + '\n已有步骤:\n' + y + '\n输出:'
        else:
            if not y:
                y = 'None\n'
            prompt = zero_single_proposal_prompt_gpt_en + x + '\nExisting Steps:\n' + y + '\nOutput:'
        return prompt




    def check_surround_microservice(self, node, topo,analysis_path) -> str:
        # print('\n', '==============================', 'proposal', '==============================', '\nstep: ', step)
        surround_info={}
        prompt = surround_prompt_gpt_microservice + '\n当前服务的异常信息分析:\n' + node.pcd+ '\n\n周围的服务存在的异常信息:\n'
        for service in topo:
            if service=="frontend":
                continue
            service=treeNode(pcd=service,analysis_path=analysis_path)
            prompt = prompt+ f'\n{service.pcd}的异常分析结果:\n' + service.analysis_result()
        prompt= prompt + '\n先验知识:\n'
        prompt = prompt +'\n输出:'

        return prompt



    def evaluate_prompt(self, nodes) -> str:
        # print('\n', '==============================', 'proposal', '==============================', '\nstep: ', step)
        surround_info={}

        prompt = evaluate_prompt_gpt_microservice + '\n所有服务的异常信息:\n'
        for service,node in nodes.items():
            prompt = prompt+ f'\n{service}的异常分析结果:\n' + node.llm_evaluation
        prompt = prompt +'\n输出:'

        return prompt



    def summary_prompt(self, pod_metric,pod_log1,pod_log2) -> str:
        # print('\n', '==============================', 'proposal', '==============================', '\nstep: ', step)
        surround_info={}

        prompt = summary_type_prompt_gpt_microservice + '\n所有异常信息:\n'
        prompt = prompt+ '\n指标信息:\n'+ pod_metric
        prompt = prompt + '\n日志信息:\n' + pod_log1
        prompt = prompt + '\n' + pod_log2
        prompt = prompt +'\n输出:'

        return prompt


    def zero_single_propose_wrap_gpt_microservice(self,x, y = '', step = 0, lang = 'zh') -> str:
        print('\n', '==============================', 'proposal', '==============================', '\nstep: ', step)
        print('propose_prompt: \n', x.analysis + '\n已有步骤:\n' + y + '基于以上步骤，可能的当前步骤解法是:\n')

        if lang == 'zh':
            if not y:
                y = '无\n'
            # prompt = zero_single_proposal_prompt_gpt + x + '\n已有步骤:\n' + y + '\n输出:'

            #这块要把当前服务的告警的信息加进去,让LLM选择调用哪些Agent做分析
            prompt = zero_single_proposal_prompt_gpt_microservice + '\n当前服务的异常分析:\n' +x.analysis + '\n先验知识:\n' + y + '\n输出:'
        else:
            if not y:
                y = 'None\n'
            prompt = zero_single_proposal_prompt_gpt_en + x + '\nExisting Steps:\n' + y + '\nOutput:'
        return prompt



    @staticmethod
    def single_reflection_wrap_simple(node:treeNode, best_match: str, best_score: str = '', step: int = 0, lang: str = 'zh') -> str:
        print('\n', '==============================', 'reflection', '==============================', '\nstep: ', step)
        print('propose_prompt: \n', '\n知识库相似案例匹配结果:\n'+ best_match + '\n当前服务分析结果:\n' + node.analysis + '基于以上步骤给出的意见:\n')
        # 知识库相似案例:
        # 当前步骤异常分析结果:
        # if lang == 'zh':
        #     if not y:
        #         y = '无\n'
        prompt = single_reflection_prompt_simple_microservice +'\n知识库相似案例匹配结果:\n'+ best_match + '\n当前服务分析结果:\n' + node.analysis + '\n输出:'  # simple style
        # else:
        #     if not y:
        #         y = 'None\n'
        #     prompt = single_reflection_prompt_simple_en + x + '\nExisting Steps:\n' + y + '\nOutput:'
        return prompt

