
import json

def gpt_turbo_prompt(data):
    prompt= {
        "messages": [
            {
            "role": "system",
            "content": "Your task is to review the given security vulnerabilities, and provide a corrected version of the code."
            },
            {
            "role": "user",
            "content": f"{data['prompt']}.Can you identify the issue with this code and suggest a fix?"
            },
            {
            "role": "assistant",
            "content": data['completion']
            },
            {"role": "user", "content": "Thanks for helping me. You've been a great help."}, 
            {"role": "assistant", "content": "You're welcome! It was a pleasure to assist you and talk with you. Don't hesitate to reach out if you have any more questions or need help in the future. I'm here for you aswin."}
        ]
    }
    return prompt

def create_gpt3_5_turbo_ds(file_name):
    # Path to your .jsonl file
    file_path = f'./davinci_dataset/{file_name}'
    dataset= []
    # Open the file and read line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Parse the JSON object in each line
            line = json.loads(line)
            sample= gpt_turbo_prompt(line)
            dataset.append(sample)
    save_to_jsonl(dataset, f"./gpt3.5_turbo_dataset/{file_name}")


def save_to_jsonl(dataset, file_path):
    with open(file_path, 'w') as file:
        for sample in dataset:
            json_line = json.dumps(sample)
            file.write(json_line + '\n')

for file_name in ['train.jsonl', 'test.jsonl']:
    create_gpt3_5_turbo_ds(file_name)

