The dataset and code for paper "Exploring ChatGPT’s Potential in Java API Method Recommendation: An Empirical Study".

### Please fill the Key into "data/Key.yml". 

## RQ1

### Evaluation
Running the following command will evaluate ChatGPT online on APIBENCH-Q or New Benchmark,
with ranging from 0 to 2.0, and generate answer samples in .json format in "result/RQ1".
``` bash       
python naive_recommend.py --prompt_type 2 --model gpt-3.5-turbo-0125 --dataset data/New-Benchmark.json --output_dir result/RQ1
```

### Calculate the result
``` bash
python RQ1_calculate.py --answer_dir result/RQ1
```

## MACAR
### Evaluation
The default temperature of all agents is 0.
``` bash
python MACAR.py --model gpt-3.5-turbo-0125 --dataset data/APIBENCH-Q.json --output_dir result/MACAR 
```
Besides, you can use the results obtained from RQ1 as recommend list1, as shown below:
``` bash
python MACAR.py --model gpt-3.5-turbo-0125 --dataset data/APIBENCH-Q.json --output_dir result/MACAR --agent1_answer_dir result/RQ1/P2-tem=0.0.json
``` 
### Calculate the result
Running the following command will calculate the results and generate failure samples that ChatGPT could not solve in "result/fail_sample". 
<br> Please enter the results path you want to evaluate after "**--answer_dir**", as shown below.
``` bash        
python MACAR_calculate.py --answer_dir result/MACAR/MACAR(GPT-3.5)-APIBENCH-Q.json --output_dir result/fail_sample
```

<br>

Running the following command will calculate the results of MACAR (GPT-4) and GPT-4 on APIBENCH-Q or New Benchmark failure samples:
<br> Please enter the failure sample path after "**--fail_dir**" and the MACAR path in "**--macar_dir**", as shown below.
``` bash        
python fail_sample_calculate.py --fail_dir result/fail_sample/MACAR(GPT-3.5)-APIBENCH-Q-fail_samples.json --macar_dir result/MACAR/MACAR(GPT-3.5)-APIBENCH-Q.json
```
