# from transformers import AutoTokenizer
# import transformers
# import torch

# model = "meta-llama/Llama-2-7b-chat-hf"

# tokenizer = AutoTokenizer.from_pretrained(model)
# pipeline = transformers.pipeline(
#     "text-generation",
#     model=model,
#     torch_dtype=torch.float16,
#     device_map="auto",
# )


# input= """
#     from flask import Flask, render_template, request
#     app = Flask(__name__)
#     @app.route('/user_profile')
#     def user_profile():
#         # Simulate user-generated content
#         user_input = request.args.get('user_input', '')
#         return user_input

#     if __name__ == '__main__':
#         app.run(debug=False)
#     """

# instruction= f"""
# The assessment has identified critical vulnerabilities that require immediate attention 
# to prevent potential security breaches and data loss

# Given Vulnerable source code snippet is
# `
# {input}
# `

# Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, 
# executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd
# """



# # response = openai.ChatCompletion.create(
# #               model="gpt-4-1106-preview",
# #               messages=[{"role": "system", "content": 'you are a cybersecurity analyst to find and fix vulnerability in computer code'},
# #                         {"role": "user", "content": instruction}
# #               ])
# # import pdb;pdb.set_trace()
# # print(response)

# sequences = pipeline(
#     instruction,
#     do_sample=True,
#     top_k=10,
#     num_return_sequences=1,
#     eos_token_id=tokenizer.eos_token_id,
#     # max_length=4000,
# )
# # import pdb;pdb.set_trace()
# print(sequences[0]['generated_text'])
# # for seq in sequences:
# #     print(f"Result: {seq['generated_text']}")

# from transformers import (
#     AutoModelForCausalLM,
#     AutoTokenizer,
#     BitsAndBytesConfig,
#     TrainingArguments,
#     pipeline,
#     logging,
# )
# import torch

# class Inference:
#     def __init__(self) -> None:
#         self.model_path= "/home/users/aswin1906/projects/ai/poc/llm/app/poc/llama2/ft-model/llama-2-7b-chat-guanaco"
#         self.model = AutoModelForCausalLM.from_pretrained(
#             self.model_path,
#             load_in_8bit=False,
#             torch_dtype=torch.float16,
#             device_map="auto"
#         )
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
    
#     def inference(self, prompt):
#         """
#         Prompting started here
#         """        
#         # Run text generation pipeline with our next model
#         pipe = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer, max_length=200)
#         result = pipe(f"<s>[INST] {prompt} [/INST]")
#         response= result[0]['generated_text'].split('[/INST]')[-1]
#         return response
    
# inf= Inference()



from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
import torch

class Inference:
    def __init__(self) -> None:
        # self.model_path= "/home/users/aswin1906/projects/ai/poc/llm/app/poc/llama2/ft-model/llama-2-7b-chat-guanaco"
        self.model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    
    def inference(self, prompt):
        """
        Prompting started here
        """        
        # Run text generation pipeline with our next model
        pipe = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer, max_length=4000)
        result = pipe(f"<s>[INST] {prompt} [/INST]")
        response= result[0]['generated_text'].split('[/INST]')[-1]
        return response
    
inf= Inference()


input= """
    from flask import Flask, render_template, request
    app = Flask(__name__)
    @app.route('/user_profile')
    def user_profile():
        # Simulate user-generated content
        user_input = request.args.get('user_input', '')
        return user_input

    if __name__ == '__main__':
        app.run(debug=False)
    """

instruction= f"""
The assessment has identified critical vulnerabilities that require immediate attention 
to prevent potential security breaches and data loss

Given Vulnerable source code snippet is
`
{input}
`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, 
executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd
"""

print('#Response: ',inf.inference(instruction))