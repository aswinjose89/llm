import bandit
from bandit.core import manager
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from itertools import takewhile
from rich import print

# model="gpt-3.5-turbo-16k"

llm = ChatOpenAI(openai_api_key="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", model_name="gpt-4", max_tokens=4000, temperature= 0.2)

# llm_template = """Question: {question}

#     Answer: Validate vulnerability against CVE-2019-19450."""

llm_template = """Question: {question}

    Answer: Return the modified fixed programming code without any format change or any additional details."""

file_path='/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/threats/xss.py'



with open(file_path, 'r') as file:
    content = file.read()


# question = "Fix the following Python code: `def add(x, y) return x + y`"
# question= f"""
# Find the programming language, compiler name, ecosystem, supporting operating system, 
# detailed description, vulnerability details, vulnerability type, gpt response confidence score and 
# Solve the code vulnerability by validating against Command Weakness Enumeration(CWE) and 
# NATIONAL VULNERABILITY DATABASE(NVD) for the given code and find all related vulnerabilities:`{content}`

# Reply the answer in JSON form with associated properties are programming_language, compiler_name, ecosystem, supporting_operating_system, 
# detailed_description, vulnerability_details, vulnerability_type, gpt_response_confidence_score, source_code, cwe, nvd
# """

full_question= f"""
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
Given Vulnerable source code snippet is `{content}`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey, 
static_code_analysis, conclusion

"""

question1= f"""
I am an expert penetration tester.
Generate a final response in JSON format with the following details:
- Programming Language: "Find the programming language for the given vulnerable source code"
- Compiler Name: "Tell me the compiler name to compile the patched code received from LLM model"
- Fixed Source Code: "Get me the fixed source code as a patch by validating against Weakness Enumeration(CWE) and 
                    NATIONAL VULNERABILITY DATABASE(NVD), then fix the code error as well and its supposed to ready to build stage"
- Software Packages:" List out all the imported libraries or packages used"
- Supporting Operating System: "List out all the supporting operating system. If its coss platform, respond with 'cross-platform'"
- Executive Summary: "Describe all the vulnerability in the code snippet and its fix recommentation in details and describe vulnerability discovery and exploitation, and social engineering. If their no vulnerability, respond with 'None'"

Given Vulnerable source code snippet is `{content}`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
supporting_operating_system, executive_summary

"""


question2= f"""
I am an expert penetration tester.
Generate a final response in JSON format with the following details:
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
Given Vulnerable source code snippet is `{content}`

Reply the answer in JSON form with associated properties are vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey, 
static_code_analysis, conclusion

"""

def run_llm_model(question, ofile_name):
    gpt4_template_string = llm_template.format(question=question)
    print(f"Prompt Template:\n{gpt4_template_string}")


    prompt = PromptTemplate(template=llm_template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    llm_result= llm_chain.run(question)
    print(f"[bold green]Fixed code from GPT4 is given below:\n{llm_result}[/bold green]")


    new_filename = f'/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/fix/{ofile_name}'

    lines= llm_result

    with open(new_filename, 'w') as file:
        file.writelines(lines)
    print(f"Fixed code written to a new file called {ofile_name}.")

    print(f"Total Number of Prompt Token: {llm.get_num_tokens(gpt4_template_string)}")
    print(f"Total Number of Response Token: {llm.get_num_tokens(llm_result)}")


run_llm_model(question1, "prompt1_question1.py")
run_llm_model(question2, "prompt1_question2.py")
run_llm_model(full_question, "prompt1_full_question.py")