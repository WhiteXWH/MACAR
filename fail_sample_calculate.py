from util import dataProcess
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail_dir", type=str, required=True,
                        help="fail samples file path")
    parser.add_argument("--macar_dir", type=str, required=True,
                        help="fail samples file path")

    args = parser.parse_args()
    tool = dataProcess.Tool()

    fail_samples = tool.read_json(args.fail_dir)
    fail_samples_length = len(fail_samples)
    fail_samples_number_set = fail_samples.keys()
    macar_gpt4 = tool.read_json(args.macar_dir)

    gpt4_result = tool.calculate(macar_gpt4, "RecommendationList1", fail_samples_number_set)
    macar_gpt35_result = tool.calculate(fail_samples, "FinalAnswer", fail_samples_number_set)
    macar_gpt4_result = tool.calculate(macar_gpt4, "FinalAnswer", fail_samples_number_set)

    print("-" * 20 + f"GPT-4" + "-" * 20)
    tool.print_result(gpt4_result, fail_samples_length)
    print("-" * 20 + f"MACAR(GPT-3.5)" + "-" * 20)
    tool.print_result(macar_gpt35_result, fail_samples_length)
    print("-" * 20 + f"MACAR(GPT-4)" + "-" * 20)
    tool.print_result(macar_gpt4_result, fail_samples_length)
