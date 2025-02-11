import time
import math
import random
import numpy
from MCTS.base import treeNode
from Agent.Trace_Agent import Trace_Agent


def get_next_steps_roll(node: treeNode, step_n: int, mcts_task):
    next_steps = []
    for i in range(mcts_task.roll_branch):
        proposal = ''
        cnt = 3
        while not proposal and cnt:
            proposal = mcts_task.get_next_step_simulation(node, step_n)
            cnt -= 1
        if not proposal:
            continue

        score = extract_content(proposal)
        next_steps.append((int(score),proposal))
    return next_steps


def get_next_steps_expand(node: treeNode, mcts_task):
    ground_truth_topo=Trace_Agent()
    next_steps = {}
    reflection = node.reflection
    for service in ground_truth_topo[node.pcd]:


        proposal = ''
        cnt = 3
        while not proposal and cnt:
            if mcts_task.use_reflection == 'common':
                proposal = mcts_task.get_next_step_use_reflection(node.y, node.depth + 1, reflection)
            else:
                proposal = mcts_task.get_next_step(service, node.y, node.depth + 1)
            cnt -= 1
        if not proposal:
            continue

        next_steps[service] =  proposal
    return next_steps


def randomPolicy(node: treeNode, mcts_task):
    max_V = mcts_task.low
    strs = node.y
    cur_step = node.depth + 1
    if mcts_task.use_reflection == 'common':
        reflection = mcts_task.get_reflection(strs, cur_step)
    else:
        reflection = mcts_task.get_simple_reflection(strs, cur_step)
    node.update_reflection(reflection)
    if reflection == '<end>':
        print('This step has been resolved and does not require simulation.\n')
        return node.V
    for i in range(mcts_task.roll_forward_steps):
        next_steps = get_next_steps_roll(strs, cur_step, mcts_task)
        if not next_steps:
            break
        action = random.choice(next_steps)  # str
        strs = strs + action
        cur_step += 1
        value = mcts_task.get_step_value(strs)
        if value > max_V:
            max_V = value
        if mcts_task.use_reflection == 'common':
            cur_ref = mcts_task.get_reflection(strs, cur_step)
        else:
            cur_ref = mcts_task.get_simple_reflection(strs, cur_step)
        if cur_ref == '<end>':
            break
    return max_V


def greedyPolicy(node: treeNode, mcts_task):
    max_V = mcts_task.low
    strs = node.y
    cur_step = node.depth + 1

    if mcts_task.use_reflection == 'common':
        reflection = mcts_task.get_reflection(strs, cur_step)
    else:
        reflection = mcts_task.get_knowledge_reflection(node, cur_step)#
    node.update_reflection(reflection)
    if reflection == '<end>':
        print('This service has been confirmed for root cause and does not require simulation further.\n')
        return node.V

    for i in range(mcts_task.roll_forward_steps):
        actions = get_next_steps_roll(node, cur_step, mcts_task)
        if not actions:
            break
        new_ys = [strs + action[1] for action in actions]
        cur_step += 1
        values = [action[0] for action in actions]
        idx = numpy.argmax(values)
        strs = new_ys[idx]
        value = values[idx]
        if value > max_V:
            max_V = value

    return max_V


def MCTS_search(mcts_task,analysis_path):
    root = treeNode('frontend',analysis_path)

    if mcts_task.limit_type == 'time':
        timeLimit = time.time() + mcts_task.time_limit / 1000
        time_start = time.time()
        while time.time() < timeLimit:
            print(f'<开始新搜索轮次，目前总时间:{time.time() - time_start}>\n')
            flag, node, root = executeRound(root, mcts_task)
            if flag:
                print('已找到解决方案！\n')
                return root, node, time.time() - time_start
    else:
        for i in range(mcts_task.iteration_limit):
            print(f'<开始新搜索轮次，目前已完成轮次数:{i}>\n')
            flag, node, root = executeRound(root, mcts_task)
            if flag:
                print('已找到解决方案！\n')
                return root, node, i + 1
    return root, None, None


def executeRound(root, mcts_task):
    print('-' * 40)
    print('选择节点阶段\n')
    flag, node = selectNode(root, mcts_task)
    if flag:
        if mcts_task.sample_value != 'full':
            return True, node, root
        else:
            node.reflection = '<end>'

    print('-' * 40)
    print('扩充阶段\n')
    if node.reflection == '<end>':
        print('跳过此阶段。\n')
    else:
        node = expand(node, mcts_task)
    if mcts_task.reward_model_type == 'vm':
        print('-' * 40)
        print('模拟搜索阶段\n')
        if node.reflection == '<end>':
            print('跳过此阶段。\n')
        else:
            roll_node = getBestChild(node, mcts_task)
            best_V = greedyPolicy(roll_node, mcts_task) if mcts_task.roll_policy == 'greedy' else randomPolicy(roll_node,mcts_task)
            roll_node.V = roll_node.V * (1 - mcts_task.alpha) + best_V * mcts_task.alpha
            roll_node.numVisits += 1

    print('-' * 40)
    print('反向传播阶段\n')
    back_propagate(node)
    return False, node, root


def isTerminal(node, mcts_task):
    if mcts_task.reward_model_type == 'vm':
        return node.V >= mcts_task.end_gate
    else:
        return False


def selectNode(node, mcts_task):
    while node.isFullyExpanded:
        node = getBestChild(node, mcts_task)
    if isTerminal(node, mcts_task):
        node.final_ans_flag = 1
        return True, node
    else:
        return False, node

import re
def extract_content(text):
    match = re.search(r'<root_score_start>(.*?)<root_score_end>', text)
    if match:
        return match.group(1)
    else:
        return None


def parse_services(text):
    pattern = re.compile(r"<root_service_start>(.*?)<root_service_end>:<root_score_start>(\d+)<root_score_end>")
    matches = pattern.findall(text)

    service_scores = {service: int(score) for service, score in matches}
    return service_scores


def modify_service_string(s):
    if re.search(r"service\d*-?\d*", s):
        return re.sub(r"service\d*-?\d*", "service", s)
    return s



def expand(node: treeNode, mcts_task):
    if not node.reflection:
        if mcts_task.use_reflection == 'common':
            reflection = mcts_task.get_reflection(node.y, node.depth + 1)
        else:
            reflection = mcts_task.get_simple_reflection(node.y, node.depth + 1)
        node.update_reflection(reflection)
    if node.reflection == '<end>':
        return node
    actions = get_next_steps_expand(node, mcts_task)
    response=mcts_task.evaluate_expand_result(actions)
    score_actions=parse_services(response)
    if not actions:
        node.update_reflection('<end>')
        return node


    for service,score in score_actions.items():
        service=modify_service_string(service)
        if actions[service] not in node.children.keys():
            node.append_children(actions[service])
            child = node.children[service]
            child.update_value(score)
            if mcts_task.sample_value == 'full':
                if mcts_task.use_reflection == 'common':
                    child.update_reflection(mcts_task.get_reflection(child.y, child.depth + 1))
                else:
                    child.update_reflection(mcts_task.get_simple_reflection(child.y, child.depth + 1))
            child.visit_sequence = mcts_task.node_count
            mcts_task.update_count()
    node.isFullyExpanded = True
    return node


def back_propagate(node):
    while node is not None:
        node.numVisits += 1
        if node.isFullyExpanded:
            child_Vs = []
            for child in node.children.values():
                child_Vs.append(child.V * child.numVisits)
            child_sum=[]
            for child in node.children.values():
                child_sum.append(child.numVisits)
            total_num_visits=sum(child_sum)
            if total_num_visits > 0:
                node.V = sum(child_Vs) / total_num_visits
        node = node.parent


def getBestChild(node, mcts_task):
    bestValue = mcts_task.low
    bestNodes = []
    for child in node.children.values():
        nodeValue = child.V + mcts_task.exploration_constant * math.sqrt(
            2 * math.log(node.numVisits) / child.numVisits) if child.numVisits > 0 else child.V + mcts_task.INF
        if nodeValue > bestValue:
            bestValue = nodeValue
            bestNodes = [child]
        elif nodeValue == bestValue:
            bestNodes.append(child)
    return random.choice(bestNodes)


def MCTS(mcts_task,analysis_path):
    root, node, finish = MCTS_search(mcts_task,analysis_path)

    if mcts_task.sample_value == 'full':
        print('采样完成。\n')
        return None, -1, root
    else:
        if mcts_task.reward_model_type == 'vm':
            if finish is not None:
                print(f'已找到最终解!\nSolution:{node.y}\n')
                return node, finish, root

            else:
                best_node, best_V = root.getBestV()
                print(f'在规定时间/轮次内未找到满足要求价值的解答，采用最高价值价值解答代替。\nSolution:{best_node.y}\n')
                return best_node, -1, root
        else:
            print('尚未支持解答选择，采样结束。\n')
            return None, -1, root
