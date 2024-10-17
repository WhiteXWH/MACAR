import argparse
import os

import numpy as np
from tqdm import tqdm
from util import apiRecommendAgent, dataProcess

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_type", type=int, required=True,
                        help="prompt type")
    parser.add_argument("--tem", type=float, default=2.0,
                        help="temperature of gpt")
    parser.add_argument("--model", type=str, required=True,
                        help="gpt type")
    parser.add_argument("--dataset", type=str, required=True,
                        help="dataset file path")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="data write file path")

    args = parser.parse_args()
    tool = dataProcess.Tool()

    dataset = tool.read_json(args.dataset)
    tem_range = np.arange(0, args.tem, 0.5)
    dataset_length = len(dataset)

    os.makedirs(args.output_dir, exist_ok=True)

    for tem in tem_range:
        result_path = f"{args.output_dir}/P{args.prompt_type}-tem={tem}.json"
        result_length = tool.judge_path_is_exist(result_path)
        print(f"P{args.prompt_type}-tem={tem} ", end="")
        for i, item in tqdm(enumerate(dataset), total=dataset_length, desc='Processing'):
            if i < result_length:
                continue
            query = dataset[item]["Query"]
            ground_truth = dataset[item]["GroundTruth"]

            if args.prompt_type == 1:
                agent = apiRecommendAgent.Prompt1(recommend_number=10,
                                                  programming_query=query,
                                                  model=args.model)
            else:
                agent = apiRecommendAgent.Agent1BasePrompt2(recommend_number=10,
                                                            programming_query=query,
                                                            model=args.model)

            answer = agent.try_get_answer(tem)
            tmp_dict = {
                "Query": query,
                "GroundTruth": ground_truth,
                "Answer": answer.splitlines()
            }

            tool.write_json(result_path, {item: tmp_dict})
