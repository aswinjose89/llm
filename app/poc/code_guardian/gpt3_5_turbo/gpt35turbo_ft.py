import openai
import os
import json
import os
import tiktoken
import numpy as np
from collections import defaultdict
import time

openai.api_key = "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"



training_file_name= "./dataset/vulnerability_tasks_train.jsonl"
validation_file_name= "./dataset/vulnerability_tasks_val.jsonl"
training_response = openai.File.create(
    file=open(training_file_name, "rb"), purpose="fine-tune"
)
training_file_id = training_response["id"]

validation_response = openai.File.create(
    file=open(validation_file_name, "rb"), purpose="fine-tune"
)
validation_file_id = validation_response["id"]

print("Training file id:", training_file_id)
print("Validation file id:", validation_file_id)

# Check if file is ready
print('Checking file status...')
while training_response.status != 'processed':
    time.sleep(10)
    file = openai.File.retrieve(training_response.id)
    print('File status:', file.status)

    # If file fails, print error and exit
    if file.status != 'processed':
        print('File failed:', file)
        exit(1)
    


#Create a Fine Tuning Job
suffix_name = "vul-scan-run1"

job = openai.FineTuningJob.create(
    training_file=training_file_id,
    validation_file=validation_file_id,
    model="gpt-3.5-turbo",
    suffix=suffix_name,
    hyperparameters= {"n_epochs":50, "batch_size": 5 }
)
job_id = job["id"]
print('Job created.')
print(job)


# Loop until status is succeeded. Print status every 60 seconds
# while job.status != 'succeeded':
#     time.sleep(10)
#     job = openai.FineTuningJob.retrieve(job.id)
#     print('Job status:', job.status)

#     # If job fails, print error and exit
#     if job.status != 'running' and job.status != 'succeeded':
#         print('Job failed:', job)
#         exit(1)

# print('Job completed.')
# print('Fine-tuned model:', job.fine_tuned_model)


# response = openai.FineTuningJob.retrieve(job_id)
# print(response)

response = openai.FineTuningJob.list_events(id=job_id, limit=50)
events = response["data"]
events.reverse()

for event in events:
    print(event["message"])

response = openai.FineTuningJob.retrieve(job_id)
fine_tuned_model_id = response["fine_tuned_model"]

print(response)
print("\nFine-tuned model id:", fine_tuned_model_id)

#Inferencing using the new model
system_message = "You are Aswin a helpful and charming assistant who talks about Common Vulnerabilities and Exposures(CVE) in details to find the solution or patch to rectify the problem quickly for the user"
test_messages = []
test_messages.append({"role": "system", "content": system_message})
user_message = "Hey Aswin, I have a vulnerability on my source code which is related to CVE-2020-23064. Can you help me to troubleshoot this issue?"
test_messages.append({"role": "user", "content": user_message})

print(test_messages)

response = openai.ChatCompletion.create(
    model=fine_tuned_model_id, messages=test_messages, temperature=0, max_tokens=500
)
print(response["choices"][0]["message"]["content"])