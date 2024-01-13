import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from rich import print


def vulnerable_code():
    code= """
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
    return code

class GPT4SimpleProgram:
    def __init__(self) -> None:
        self.llm_gpt4= ChatOpenAI(openai_api_key="Put Your API Key here", model_name="gpt-4-1106-preview", max_tokens=4000)
        self.llm_tpl = """Question: {question}

        Answer: Return the modified fixed programming code without any format change or any additional details."""
    
    def build_prompt(self, content):
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
            - "vulnerability_id": "Find out the relevant vulnerability id from NATIONAL VULNERABILITY DATABASE",
            - "description": "Describe the identified vulnerability",
            - "severity": "Tell me the severity of this vulnerability",
            - "impact": "Explain the vulnerability impact",
            - "recommendation": "Explain the vulnerability recommendation to avoid any exploitation"
            - "cvss_score": "Provide the CVSS score from Common Vulnerability Scoring System in a numerical format"
        - Vulnerability Type: "List out all the applicable vulnerabilities like XSS, Command Injection, SQL Injection etc"
        - Command Weakness Enumeration(CWE): "List out respective cwe id with details, base findings, attack surface and environment"
        - NVD: "Provide standard meta data from NATIONAL VULNERABILITY DATABASE"
        - Literature Survey: "List out all the related literature survey reference articles"
        - Static Code Analysis: "Access any related static code analysis tool and find out the code errors like syntax and semantics deeply if possible"
        - coding standard violations: "Recommended coding standard violations if available otherwise say 'None'"
        - Test Cases: "Create a testcases applicable for the given code snippet to mitigate vulnerability"
        - Conclusion: "The assessment has identified critical vulnerabilities that require immediate attention to prevent potential security breaches and data loss."
        Given Vulnerable source code snippet is `{content}`

        Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
        supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey, 
        static_code_analysis, conclusion
        """
        template_string = self.llm_tpl.format(question=question)
        print(template_string)
        prompt = PromptTemplate(template=self.llm_tpl, input_variables=["question"]) 
        return prompt, question

    def run_llm(self, prompt, question) -> str:
        llm_chain = LLMChain(prompt=prompt, llm=self.llm_gpt4)
        llm_result= llm_chain.run(question)
        return llm_result

    
    def run(self):        
        code= vulnerable_code()        
        prompt, question= self.build_prompt(code)
        llm_result= self.run_llm(prompt, question) 
        llm_result= llm_result.strip().replace("```json\n","").replace("\n```", "")
        llm_result= json.loads(llm_result)
        llm_result= json.dumps(llm_result, indent=4)
        print(f"[bold green]{llm_result}[/bold green]")


inst= GPT4SimpleProgram()
inst.run()