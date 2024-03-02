


# dataset={"prompt": "<prompt text>", "completion": "<ideal generated text>"}


import openai

openai.api_key ="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"


training_file_name = './gpt4_dataset/train.jsonl'

training_response= openai.File.create(
  file=open(training_file_name, "rb"),
  purpose="fine-tune"
)

training_file_id = training_response["id"]

# Define your fine-tuning parameters
fine_tuning_parameters = {
    "training_file": training_file_id,
    "model": "davinci-002",
    "suffix": "AIxCC",
    "hyperparameters": {
        "n_epochs":50,
        "batch_size": 10
    }
}

response= openai.FineTuningJob.create(**fine_tuning_parameters)


import pdb;pdb.set_trace()
job_id = response["id"]

print(response)

response = openai.FineTuningJob.retrieve(job_id)
print(response)

response = openai.FineTuningJob.list_events(id=job_id, limit=50)

print(response)
# events = response["data"]
# events.reverse()

# for event in events:
#     print(event["message"])