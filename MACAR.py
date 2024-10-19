import argparse
from tqdm import tqdm
from util import apiRecommendAgent, dataProcess
from concurrent.futures import ThreadPoolExecutor

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True,
                        help="gpt type")
    parser.add_argument("--dataset", type=str, required=True,
                        help="dataset file path")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="data write file path")
    parser.add_argument("--tem", type=float, default=0.0,
                        help="temperature of gpt")
    parser.add_argument("--agent1_answer_dir", type=str, default=None,
                        help="agent1 answer based on RQ1")
    args = parser.parse_args()
    tool = dataProcess.Tool()

    if "4" in args.model:
        gpt_type = 4
    else:
        gpt_type = 3.5

    if "APIBENCH-Q" in args.dataset:
        dataset_type = "APIBENCH-Q"
    else:
        dataset_type = "New-Benchmark"

    dataset = tool.read_json(args.dataset)
    dataset_length = len(dataset)
    agent1_answer = None

    if args.agent1_answer_dir is not None:
        agent1_answer = tool.read_json(args.agent1_answer_dir)

    result_path = f"{args.output_dir}/MACAR(GPT-{gpt_type})-{dataset_type}.json"
    result_length = tool.judge_path_is_exist(result_path)

    for i, item in tqdm(enumerate(dataset), total=dataset_length, desc='Processing'):
        if i < result_length:
            continue

        query = dataset[item]["Query"]
        ground_truth = dataset[item]["GroundTruth"]

        agent2 = apiRecommendAgent.Agent2StructCoT(programming_query=query, model=args.model)
        if agent1_answer is None:
            agent1 = apiRecommendAgent.Agent1BasePrompt2(recommend_number=10, programming_query=query,
                                                         model=args.model)
            with ThreadPoolExecutor(max_workers=2) as executor:
                future1 = executor.submit(agent1.try_get_answer, args.tem)
                future2 = executor.submit(agent2.try_get_answer, args.tem)

                recommendation_list1 = future1.result()
                agent2_answer = future2.result()
        else:
            recommendation_list1 = agent1_answer[item]["Answer"]
            agent2_answer = agent2.try_get_answer(args.tem)



        code_snippet = agent2.get_java_code(agent2_answer)
        agent3 = apiRecommendAgent.Agent3ExtractApiFromCode(programming_query=query,
                                                            model=args.model,
                                                            code=code_snippet)
        recommendation_list2 = agent3.try_get_answer(args.tem)

        agent4 = apiRecommendAgent.Agent4LastJudge(programming_query=query,
                                                   model=args.model,
                                                   recommendation_list1=recommendation_list1,
                                                   recommendation_list2=recommendation_list2)
        final_answer = agent4.try_get_answer(args.tem)

        tmp_dict = {"Query": query, "GroundTruth": ground_truth,
                    "FinalAnswer": final_answer.splitlines(),
                    "RecommendationList1": recommendation_list1.splitlines(),
                    "RecommendationList2": recommendation_list2.splitlines(), "Code": code_snippet.splitlines()}
        tool.write_json(result_path, {item: tmp_dict})
