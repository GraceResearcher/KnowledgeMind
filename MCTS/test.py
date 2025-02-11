import time

from MCTS.task import *
question = "确认当前微服务系统的根本故障服务和原因."
for root, dirs, files in os.walk("./output_anomaly_log"):
    for analysis_path in dirs:
        start=time.time()
        task = MCTS_Task(question, 'gpt', 'gpt', lang='zh', time_limit=50000000,analysis_path=analysis_path)
        result_service,analysis = task.run()
        # node, finish, root = task.run()
        result=result_service+'\n\n'+analysis

        output_dir = "./output_result"
        # 确保目录存在
        os.makedirs(output_dir, exist_ok=True)
        # 直接在 analysis_path 后拼接 .txt 作为文件名
        output_file = os.path.join(output_dir, f"{analysis_path}.txt")
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(result)
        print(f"Log saved to {output_file}")

        end=time.time()
        print('!!!!!!!!!!!MCTS时间:'+str(end-start))




#对分数的刻画有问题，因为输出综述了，有点奇怪，得debug一下看看综述咋回事