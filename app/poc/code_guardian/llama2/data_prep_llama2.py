

import pandas as pd, json
import os

def save_to_jsonl(conversations, file_path):
    with open(file_path, 'w') as file:
        for conversation in conversations:
            json_line = json.dumps(conversation)
            file.write(json_line + '\n')


def data_clean(dataset, data):
    for index, row in dataset.iterrows():
        severity= eval(row['database_specific'])['severity']
        references= ','.join([row['url'] for row in eval(row['references']) if 'github.com' and 'commit' in row['url']])
        commit_hash= references.split('commit/')[-1]
        is_aliases= True if len(row['aliases'])>3 else False
        if is_aliases:
            cve_id= ','.join(eval(row['aliases']))
        else:
            cve_id= []
        published_date= row['published']
        github_reviewed_at= str(eval(row['database_specific'])['github_reviewed_at'])
        prompt= {
            "system_prompt": "You are an expert cybersecurity analyst",
            "instruction": "I have a vulnerability on my source code which is related to {}. Can you help me to troubleshoot this issue?".format(cve_id),            
            "input": "",
            "output": "Of course, I'd be happy to help!. Seems this vulnerability talks about {}".format(row['summary']),
            
        }   
        prompt["base_text"]= f"{prompt['system_prompt']}\n\n### Instruction:\n{prompt['instruction']}\n\n ### Response:{prompt['output']}"
        prompt["chat_text"]= f"<s>[INST]{prompt['instruction']}[/INST] {prompt['output']}</s>"
        data.append(prompt)
        prompt= {
            "system_prompt": "You are an expert cybersecurity analyst",
            "instruction": "What is the patch and severity for {} from {}?".format(row['summary'], cve_id),            
            "input": "",
            "output": "Severity is {} and patch is {}".format(severity, references)            
        }   
        prompt["base_text"]= f"{prompt['system_prompt']}\n\n### Instruction:\n{prompt['instruction']}\n\n ### Response:{prompt['output']}"
        prompt["chat_text"]= f"<s>[INST]{prompt['instruction']}[/INST] {prompt['output']}</s>"
        
        data.append(prompt)


def get_files() -> list:
    # Specify the directory path
    directory_path = "/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/raw_dataset/"
    file_paths = []  # List to store file paths
    for root, directories, files in os.walk(directory_path):
        for filename in files:
            # Join the two strings to form the full file path.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def prepare_data():
    train_data, val_data= [], []
    dataset_files= get_files()
    for data_path in dataset_files:
        dataset= pd.read_csv(data_path)
        train_percent= 0.7
        train_ds_size= round(len(dataset)*train_percent)
        train_dataset= dataset[:train_ds_size]
        val_dataset= dataset[train_ds_size:]
        data_clean(train_dataset, train_data)  
        data_clean(val_dataset, val_data)
    save_to_jsonl(train_data, "./dataset/all_vulnerability_tasks_train.jsonl")
    save_to_jsonl(val_data, "./dataset/all_vulnerability_tasks_val.jsonl")
prepare_data()



