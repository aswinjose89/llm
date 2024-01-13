

import pandas as pd, json
import os

def save_to_jsonl(conversations, file_path):
    with open(file_path, 'w') as file:
        for conversation in conversations:
            json_line = json.dumps(conversation)
            file.write(json_line + '\n')


# data= [
#     {
#         "messages": [
#             {
#             "role": "system",            
#             "content": "You are Vulnerability manager who talks about Common Vulnerabilities and Exposures(CVE) in details to find the solution or patch to rectify the problem quickly for the user"
#             },
#             {
#             "role": "user",
#             "content": "Hey Samantha, I have a problem with my car. The engine seems to overheat after just a short drive. Can you help me troubleshoot this issue?"
#             },
#             {
#             "role": "assistant",
#             "content": "Of course, I'd be happy to help! Overheating engines can be caused by a few different factors. One common cause could be a malfunctioning coolant system. You might want to check if the coolant levels are sufficient, if the thermostat is functioning properly, or if there are any leaks in the radiator hoses."
#             }
#         ]
#     }
# ]

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
        chain= [
            {
                "role": "system",            
                "content": "You are an expert cybersecurity analyst"
            },
            {
                "role": "user",
                "content": "Hey Aswin, I have a vulnerability on my source code which is related to {}. Can you help me to troubleshoot this issue?".format(cve_id)
            },
            {
                "role": "assistant",
                "content": "Of course, I'd be happy to help!. Seems this vulnerability talks about {}".format(row['summary'])
            },
            {
                "role": "user",
                "content": "Hey Aswin, What is the patch and severity for {} from {}?".format(row['summary'], cve_id)
            },
            {
                "role": "assistant",
                "content":"Severity is {} and patch is {}".format(severity, references)
            },
            {
                "role": "user",
                "content": "When did {} is published?".format(cve_id)
            },
            {
                "role": "assistant",
                "content":"Good Question!!, Its is published on {}".format(published_date)
            },
            {
                "role": "user",
                "content": "When did {} is reviewed by github?".format(cve_id)
            },
            {
                "role": "assistant",
                "content":"Its is reviewed on {}".format(github_reviewed_at)
            },
            {
                "role": "user",
                "content": "Thanks for helping me with my vulnerability and answering my questions, Aswin. You've been a great help."
            },
            {
                "role": "assistant",
                "content": "You're welcome! It was a pleasure to assist you and talk with you. Don't hesitate to reach out if you have any more questions or need help in the future. I'm here for you."
            }
        ]
        conversation= {
            "messages": chain
        }
        data.append(conversation)


def get_files() -> list:
    # Specify the directory path
    directory_path = "/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/gpt3_5_turbo/raw_dataset/"
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



