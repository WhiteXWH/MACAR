from util import dataProcess
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True,
                        help="dataset type")


    args = parser.parse_args()
    tool = dataProcess.Tool()

    fail_samples = tool.read_json(f"result/MACAR/MACAR(GPT-3.5)-{args.dataset}-fail_samples.json")
    fail_samples_length = len(fail_samples)
    macar_gpt4 = tool.read_json(f"result/MACAR/MACAR(GPT-4)-{args.dataset}-fail_samples.json")
    fail_samples_number_set = fail_samples.keys()

    gpt4_result = tool.calculate(macar_gpt4, "RecommendationList1", fail_samples_number_set)
    macar_gpt35_result = tool.calculate(fail_samples, "FinalAnswer", fail_samples_number_set)
    macar_gpt4_result = tool.calculate(macar_gpt4, "FinalAnswer", fail_samples_number_set)

    print("-" * 20 + f"GPT-4" + "-" * 20)
    tool.print_result(gpt4_result, fail_samples_length)
    print("-" * 20 + f"MACAR(GPT-3.5)" + "-" * 20)
    tool.print_result(macar_gpt35_result, fail_samples_length)
    print("-" * 20 + f"MACAR(GPT-4)" + "-" * 20)
    tool.print_result(macar_gpt4_result, fail_samples_length)
