from util import dataProcess
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer_dir", type=str, required=True,
                        help="answer filepath")
    parser.add_argument("--output_dir", type=str, required=True,
                        help= "failure samples filepath")

    args = parser.parse_args()
    tool = dataProcess.Tool()

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    for file in os.listdir(args.answer_dir):
        dataset = tool.read_json(f"{args.answer_dir}/{file}")
        dataset_length = len(dataset)

        if "APIBENCH-Q" in file:
            dataset_type = "APIBENCH-Q"
        else:
            dataset_type = "New-Benchmark"

        gpt_type = file.split("-", 1)[-1].split(")", 1)[0]
        pre_file_str = file.split(".json")[0]
        fail_samples_path = f"{args.output_dir}/{pre_file_str}-fail_samples.json"

        macar_result = tool.calculate(dataset, "FinalAnswer", dataset.keys())
        gpt_result = tool.calculate(dataset, "RecommendationList1",  dataset.keys(), fail_samples_path)

        print("-" * 20 + f"GPT-{gpt_type}-{dataset_type}" + "-" * 20)
        tool.print_result(gpt_result, dataset_length)
        print("-" * 20 + f"MACAR(GPT-{gpt_type})-{dataset_type}" + "-" * 20)
        tool.print_result(macar_result, dataset_length)