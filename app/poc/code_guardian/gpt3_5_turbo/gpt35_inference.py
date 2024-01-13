import openai
import os
import json
import os
import tiktoken
import numpy as np
from collections import defaultdict
import time


openai.api_key = "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"

system_message = "You are Aswin a helpful and charming assistant who talks about Common Vulnerabilities and Exposures(CVE) in details to find the solution or patch to rectify the problem quickly for the user"
test_messages = []
test_messages.append({"role": "system", "content": system_message})
user_message = "Hey Aswin, What is the patch and severity for jQuery Cross Site Scripting vulnerability from CVE-2020-23064"
test_messages.append({"role": "user", "content": user_message})

print(test_messages)

job_id="ftjob-52t7O4hZVGvUyEP9iA03rGaA"
response = openai.FineTuningJob.retrieve(job_id)
fine_tuned_model_id = response["fine_tuned_model"]
response = openai.ChatCompletion.create(
    model=fine_tuned_model_id, messages=test_messages, temperature=0, max_tokens=500
)
print(response["choices"][0]["message"]["content"])