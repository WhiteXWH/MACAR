import json
import os
import re
import yaml
import openai
import numpy as np


class Tool:
    rank = [3, 5, 10]

    @staticmethod
    def get_answer_from_gpt(model, query, tem):
        key_path = '../data/Key.yaml'

        with open(key_path, 'r') as file:
            key = yaml.safe_load(file)
            file.close()

        openai.api_key = key

        messages = [
            {"role": "system", "content": "You are an experienced Java developer."},
            {"role": "user", "content": query}
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=tem,
            timeout=300,
        )

        return response['choices'][0]['message']['content']

    @staticmethod
    def read_json(path, coding='utf-8'):
        with open(path, 'r', encoding=coding) as file:
            data = json.load(file)
            file.close()
        return data

    def write_json(self, json_path, data, dump=4):
        # json_str = json.dumps(data, indent=dump)
        if not os.path.exists(json_path):
            with open(json_path, 'w') as f:
                json.dump({}, f)

        total_data = self.read_json(json_path)

        for item in data:
            total_data[item] = data[item]

        with open(json_path, 'w') as f:
            json.dump(total_data, f, indent=dump)

    def judge_path_is_exist(self, path):
        result_length = 0
        if os.path.exists(path):
            result_length = len(self.read_json(path))
        else:
            os.mkdir(path)
        return result_length

    @staticmethod
    def remove_parentheses_with_args(text):
        result = ""
        stack = []
        for item in text:
            if item == "(":
                stack.append("(")
            elif item == ")":
                if stack:
                    stack.pop()
            if not stack and item != ")":
                result += item

        return result

    @staticmethod
    def remove_unnecessary_str(text):
        text = text.replace(",", "")
        text = text.replace("#", ".")
        text = text.replace("`", "")
        text = text.replace("[]", "")
        text = text.replace("*", "")

        if re.search(r'-\s*\w+\s*\([^()]*\)', text):
            text = text.replace("-", ".")
        elif "->" not in text:
            text = re.sub(r'-.*', '', text)
        text = re.sub(r'\d+\.\s+', '', text)
        text = re.sub(r'\s+', '', text)
        text = re.sub(r':.*$', '', text)
        # text = re.sub(r'\.\s*<.*?>', '', text)

        return text

    @staticmethod
    def check_constructor(method):
        dot_split = re.split(r"\.", method)

        if len(dot_split) < 2:
            return False

        if dot_split[-1] == dot_split[-2] and dot_split[-1].isupper():
            return True

        if "init" in method:
            return True

        return False

    @staticmethod
    def hit_calculate(start, end, success_rate, pos, number, hits, tmp_map):
        for i in range(start, end):
            if pos[i] == 0:
                pos[i] = number
                success_rate[i] = 1
            else:
                pos[i] = min(pos[i], number)
            tmp_map[i] += hits / number

        return success_rate, pos, tmp_map

    def evaluate_(self, ground_truth, answer):

        api_set = set()
        tmp_map = np.zeros(3)
        tmp_mrr = np.zeros(3)
        success_rate = np.zeros(3)
        pos = np.zeros(3)
        hits = 0

        for api in ground_truth:
            api = self.remove_unnecessary_str(api)
            api = self.remove_parentheses_with_args(api)

            for i, tmp_api in enumerate(answer):
                hit_flag = 0
                # split_flag = 1
                if len(tmp_api) == 0 or tmp_api[0].isdigit() == False:
                    continue

                number = int(tmp_api[0])
                if len(tmp_api) > 1 and tmp_api[1].isdigit():
                    number = 10

                tmp_api = self.remove_unnecessary_str(tmp_api)
                tmp_api = self.remove_parentheses_with_args(tmp_api)

                if tmp_api in api_set:
                    continue

                if self.check_constructor(tmp_api) and self.check_constructor(api):
                    hit_flag = 1

                if tmp_api == api:
                    hit_flag = 1

                # for i in range(0, len(splitList) - 1):
                #     if splitList[i] not in tmp_api:
                #         split_flag = 0
                # if splitList[-1] not in tmp_api:
                #     split_flag = 0

                if hit_flag:
                    api_set.add(api)
                    hits += 1
                    if number <= 3:
                        success_rate, pos, tmp_map = self.hit_calculate(0, 3, success_rate, pos, number, hits, tmp_map)
                    elif number <= 5:
                        success_rate, pos, tmp_map = self.hit_calculate(1, 3, success_rate, pos, number, hits, tmp_map)
                    else:
                        success_rate, pos, tmp_map = self.hit_calculate(2, 3, success_rate, pos, number, hits, tmp_map)

        tmp_map /= len(ground_truth)

        for j in range(3):
            if pos[j]:
                tmp_mrr[j] = max(tmp_mrr[j], 1 / pos[j])

        return [success_rate, tmp_mrr, tmp_map]

    def print_result(self, evaluate_result, length):
        evaluate_result /= length
        evaluate_result = np.round(evaluate_result, 3)
        for i in range(3):
            print(f"TOP{self.rank[i]} Success Rate: {evaluate_result[0][i]}," + " " +
                  f" MRR: {evaluate_result[1][i]}, MAP: {evaluate_result[2][i]}")

    def calculate(self, data, answer_name, number_list, fail_samples_path=None):
        result = np.zeros((3, 3))
        fail_samples = dict()

        for item in number_list:
            ground_truth = data[item]["GroundTruth"]
            answer = data[item][answer_name]

            success_rate, mrr, _map = self.evaluate_(ground_truth, answer)
            result += success_rate, mrr, _map

            if not success_rate[-1]:
                fail_samples[item] = data[item]

        if fail_samples_path is not None:
            self.write_json(fail_samples_path, fail_samples)

        return result
