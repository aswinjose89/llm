import openai
from rich import print
# response = openai.ChatCompletion.create(
#     model="gpt-4",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Who won the world series in 2020?"},
#         {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#         {"role": "user", "content": "Where was it played?"}
#     ]
# )

# print(response['choices'][0]['message']['content'])


import os
import openai

openai.api_key = "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"

code= """
import Random
a = random.randint(1,12)
b = random.randint(1,12)
for i in range(10):
    question = "What is "+a+" x "+b+"? "
    answer = input(question)
    if answer = a*b
        print (Well done!)
    else:
        print("No.")
"""

# file_path='/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/threats/xss.py'
# with open(file_path, 'r') as file:
#     content = file.read()

question= f"""
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
Given Vulnerable source code snippet is `
public static final double price = 20.00;
int quantity = currentUser.getAttribute("quantity");
double total = price * quantity;
chargeUser(total);

`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey,
static_code_analysis, conclusion
"""

messages=[
        {"role": "system", "content": "You are an assistant with expertise in cybersecurity."},
        {"role": "user", "content": question}
    ]

response = openai.ChatCompletion.create(
  model="gpt-4-1106-preview",
  messages=messages,
  temperature=0,
  max_tokens=4000
)
print("*" * 50)
print("Find the results below")
for ch in response['choices']:
    print(ch['message']['content'])
    file_path = "/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/top_25_cwe/CWE-20.py"
    with open(file_path, 'w') as file:
        file.writelines(ch['message']['content'])