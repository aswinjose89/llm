# from transformers import AutoModelForCausalLM, AutoTokenizer

# device = "cuda" # the device to load the model onto

# model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
# tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

# text = "<s>[INST] What is your favourite condiment? [/INST]"
# "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!</s> "
# "[INST] Do you have mayonnaise recipes? [/INST]"

# encodeds = tokenizer(text, return_tensors="pt", add_special_tokens=False)

# model_inputs = encodeds.to(device)
# model.to(device)

# generated_ids = model.generate(**model_inputs, max_new_tokens=1000, do_sample=True)
# decoded = tokenizer.batch_decode(generated_ids)
# print(decoded[0])

from transformers import AutoModelForCausalLM, AutoTokenizer

device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

instruction=  """
The assessment has identified critical vulnerabilities that require immediate attention 
to prevent potential security breaches and data loss

Given Vulnerable source code snippet is
`
int id_sequence[3];
id_sequence[0] = 123;
id_sequence[1] = 234;
id_sequence[2] = 345;
id_sequence[3] = 456;
`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd

"""

messages = [
    # {"role": "user", "content": "What is your favourite condiment?"},
    # {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
    {"role": "user", "content": instruction}
]

encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")

model_inputs = encodeds.to(device)
model.to(device)

generated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
decoded = tokenizer.batch_decode(generated_ids)
print(decoded[0])
