from util import dataProcess
import argparse
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--answer_dir", type=str, required=True,
                        help="answer filepath")

    args = parser.parse_args()
    tool = dataProcess.Tool()

    for path in os.listdir(args.answer_dir):
        read_path = f"{args.answer_dir}/{path}"
        pre_file_str = path.split(".json")[0]
        fail_samples_path = f"{args.answer_dir}/{pre_file_str}-fail_samples.json"

        tem = path.split("=", 1)[-1].split(".json")[0]
        prompt_type = path.split("P", 1)[-1].split("-")[0]

        dataset = tool.read_json(read_path)
        dataset_length = len(dataset)

        evaluate_result = tool.calculate(dataset, "Answer", dataset.keys())
        print("-" * 20 + f"Prompt-{prompt_type}, tem={tem}" + "-" * 20)
        tool.print_result(evaluate_result, dataset_length)
        print("\n\n")