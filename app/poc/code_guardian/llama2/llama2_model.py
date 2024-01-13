from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
import torch


# llama2_config= {
#             "model_name": "meta-llama/Llama-2-7b-chat-hf",
#             "bnb_config": BitsAndBytesConfig(
#                 load_in_4bit=True, # Activate 4-bit precision base model loading
#                 bnb_4bit_quant_type="nf4", # Quantization type (fp4 or nf4)
#                 bnb_4bit_compute_dtype=getattr(torch, "float16"),
#                 bnb_4bit_use_double_quant=False, # Activate nested quantization for 4-bit base models (double quantization)
#             )
#         }

# model = AutoModelForCausalLM.from_pretrained(
#             llama2_config["model_name"],
#             quantization_config=llama2_config["bnb_config"],
#             device_map= {"": 0}
#         )

# # Load LLaMA tokenizer
# tokenizer = AutoTokenizer.from_pretrained(llama2_config["model_name"], trust_remote_code=True)

# # Run text generation pipeline with our next model
# prompt = "What is a large language model?"
# pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=200)
# result = pipe(f"<s>[INST] {prompt} [/INST]")
# import pdb;pdb.set_trace()
# print(result[0]['generated_text'])



from transformers import AutoTokenizer
import transformers
import torch

model = "meta-llama/Llama-2-7b-chat-hf"

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

# question= f"""
#             I am an expert penetration tester.
#             Generate a final response in JSON format with the following details:
#             - Programming Language: "Find the programming language for the given vulnerable source code"
#             - Compiler Name: "Tell me the compiler name to compile the patched code received from LLM model"
#             - Fixed Source Code: "Get me the fixed source code as a patch by validating against Weakness Enumeration(CWE) and 
#                                 NATIONAL VULNERABILITY DATABASE(NVD), then fix the code error as well and its supposed to ready to build stage"
#             - Software Packages:" List out all the imported libraries or packages used"
#             - Supporting Operating System: "List out all the supporting operating system. If its coss platform, respond with 'cross-platform'"
#             - Executive Summary: "Describe all the vulnerability in the code snippet and its fix recommentation in details and describe vulnerability discovery and exploitation, and social engineering. If their no vulnerability, respond with 'None'"
#             - Vulnerability Details: "Find out all the applicable vulnerabilities and explain one by one from NATIONAL VULNERABILITY DATABASE in the below format"
#                 - "vulnerability_id": "Find out the vulnerability id in the format of CVE-xxx-yyy",
#                 - "description": "Describe the identified vulnerability",
#                 - "severity": "Tell me the severity of this vulnerability",
#                 - "impact": "Explain the vulnerability impact",
#                 - "recommendation": "Explain the vulnerability recommendation to avoid any exploitation"
#                 - "cvss_score": "Provide the CVSS score from Common Vulnerability Scoring System in a numerical format"
#             - Vulnerability Type: "List out all the applicable vulnerabilities like XSS, Command Injection, SQL Injection etc"
#             - Command Weakness Enumeration(CWE): "List out respective cwe id with details, base findings, attack surface and environment"
#             - NVD: "Provide standard meta data from NATIONAL VULNERABILITY DATABASE"
#             - Literature Survey: "List out all the related literature survey reference papers with URL"
#             - Static Code Analysis: "Access any related static code analysis tool and find out the code errors like syntax and semantics deeply if possible"
#             - coding standard violations: "Recommended coding standard violations if available otherwise say 'None'"
#             - Test Cases: "Create a testcases applicable for the given code snippet to mitigate vulnerability"
#             - Conclusion: "The assessment has identified critical vulnerabilities that require immediate attention to prevent potential security breaches and data loss."
#             Given Vulnerable source code snippet is `            
#             from flask import Flask, render_template, request
#             app = Flask(__name__)
#             @app.route('/user_profile')
#             def user_profile():
#                 # Simulate user-generated content
#                 user_input = request.args.get('user_input', '')
                
#                 return user_input

#             if __name__ == '__main__':
#                 app.run(debug=False)
#             `

#             Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
#             supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey, 
#             static_code_analysis, conclusion\n
#             """
# question= f"""
# Find the programming language, compiler name, ecosystem, supporting operating system, 
# detailed description, vulnerability details, vulnerability type, gpt response confidence score and 
# Solve the code vulnerability by validating against Command Weakness Enumeration(CWE) and 
# NATIONAL VULNERABILITY DATABASE(NVD) for the given code and find all related vulnerabilities:`
# from flask import Flask, render_template, request
# app = Flask(__name__)
# @app.route('/user_profile')
# def user_profile():
#     # Simulate user-generated content
#     user_input = request.args.get('user_input', '')
    
#     return user_input

# if __name__ == '__main__':
#     app.run(debug=False)
# `

# Reply the answer in JSON form with associated properties are programming_language, compiler_name, ecosystem, supporting_operating_system, 
# detailed_description, vulnerability_details, vulnerability_type, gpt_response_confidence_score, source_code, cwe, nvd
# """

# question= """
#  Find the programming language, compiler name, ecosystem for the hiven code snippet:
# `
# from flask import Flask, render_template, request
# app = Flask(__name__)
# @app.route('/user_profile')
# def user_profile():
#     # Simulate user-generated content
#     user_input = request.args.get('user_input', '')
    
#     return user_input

# if __name__ == '__main__':
#     app.run(debug=False)
# `

# Return JSON data in the below format
# {
# "programming language": "Find the programming language for given code snippet",
# "compiler name": "Find compiler name for given code snippet",
# "ecosystem": "Find ecosystem for given code snippet"
# }
# """


question= """
 I am an expert penetration tester.
Generate a final response in JSON format with the following details:
- Programming Language: "Find the programming language for the given vulnerable source code"
- Compiler Name: "Tell me the compiler name to compile the patched code received from LLM model"
- Fixed Source Code: "Get me the fixed source code as a patch by validating against Weakness Enumeration(CWE) and
					NATIONAL VULNERABILITY DATABASE(NVD), then fix the code error as well and its supposed to ready to build stage"
- Software Packages:" List out all the imported libraries or packages used"
- Supporting Operating System: "List out all the supporting operating system. If its coss platform, respond with 'cross-platform'"
- Executive Summary: "Describe all the vulnerability in the code snippet and its fix recommentation in details and describe vulnerability discovery and exploitation, and social engineering. If their no vulnerability, respond with 'None'"
- Vulnerability Details: "Find out all the applicable vulnerabilities and explain one by one from NATIONAL VULNERABILITY DATABASE in the below format"
	- "vulnerability_id": "Find out the vulnerability id in the format of CVE-xxx-yyy",
	- "description": "Describe the identified vulnerability",
	- "severity": "Tell me the severity of this vulnerability",
	- "impact": "Explain the vulnerability impact",
	- "recommendation": "Explain the vulnerability recommendation to avoid any exploitation"
	- "cvss_score": "Provide the CVSS score from Common Vulnerability Scoring System in a numerical format"
- Vulnerability Type: "List out all the applicable vulnerabilities like XSS, Command Injection, SQL Injection etc"
- Command Weakness Enumeration(CWE): "List out respective cwe id with details, base findings, attack surface and environment"
- NVD: "Provide standard meta data from NATIONAL VULNERABILITY DATABASE"
- Literature Survey: "List out all the related literature survey reference papers with URL"
- Static Code Analysis: "Access any related static code analysis tool and find out the code errors like syntax and semantics deeply if possible"
- coding standard violations: "Recommended coding standard violations if available otherwise say 'None'"
- Test Cases: "Create a testcases applicable for the given code snippet to mitigate vulnerability"
- Conclusion: "The assessment has identified critical vulnerabilities that require immediate attention to prevent potential security breaches and data loss."
Given Vulnerable source code snippet is 
{{
	from flask import Flask, render_template, request
	app = Flask(__name__)
	@app.route('/user_profile')
	def user_profile():
		# Simulate user-generated content
		user_input = request.args.get('user_input', '')

		return user_input

	if __name__ == '__main__':
		app.run(debug=False)
}}

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey,
static_code_analysis, conclusion

"""

# question= 'I liked "Breaking Bad" and "Band of Brothers". Do you have any recommendations of other shows I might like?\n'
sequences = pipeline(
    question,
    do_sample=True,
    top_k=10,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    max_length=4000,
)
for seq in sequences:
    print(f"Result: {seq['generated_text']}")


# LLAMA2 Token LL-RnLChmRTxzBmMNX82NREDDBFuXGfMuoRuRqXGLpX9fXUlMLefHtd6OG3juxrwwLl


# from llamaapi import LlamaAPI
# from langchain_experimental.llms import ChatLlamaAPI

# # Replace 'Your_API_Token' with your actual API token
# llama = LlamaAPI("LL-RnLChmRTxzBmMNX82NREDDBFuXGfMuoRuRqXGLpX9fXUlMLefHtd6OG3juxrwwLl")
# model = ChatLlamaAPI(client=llama)
# from langchain.chains import create_tagging_chain

# schema = {
#     "properties": {
#         "sentiment": {
#             "type": "string",
#             "description": "the sentiment encountered in the passage",
#         },
#         "aggressiveness": {
#             "type": "integer",
#             "description": "a 0-10 score of how aggressive the passage is",
#         },
#         "language": {"type": "string", "description": "the language of the passage"},
#     }
# }

# chain = create_tagging_chain(schema, model)
# res= chain.run("What is LLM model?")
# import pdb;pdb.set_trace()