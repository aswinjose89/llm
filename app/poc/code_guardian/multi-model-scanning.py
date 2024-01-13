import bandit
from bandit.core import manager
# from langchain.llms import OpenAIChat
from langchain.chat_models import ChatOpenAI
# from langchain.llms.openai import OpenAiChat
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from itertools import takewhile
from rich import print
from rich.console import Console
from rich.table import Table
import json, os


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


class LLMModelLoader:
    def __init__(self) -> None:
        self.llm_gpt3_5_turbo = ChatOpenAI(openai_api_key="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", max_tokens=4000, model="gpt-3.5-turbo-16k", temperature= 0.2)
        self.llm_gpt4 = ChatOpenAI(openai_api_key="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", max_tokens=4000, model="gpt-4", temperature= 0.2)
        
        self.llm_vul_scan_tpl = """Question: {question}

        Answer: Return the modified fixed programming code without any format change or any additional details."""

        self.llm_code_comparision_tpl = """Question: {question}

        Answer: Return the comparision results."""

        self.llm_code_comparision_report_tpl = """Question: {question}

        Answer: Return the modified fixed programming code without any format change or any additional details."""

        self.prompt_mode= [
            {"mode": "threat_scanning", "help_text": "Create a prompt to scan the given source code vulnerability and provide the meta data"},
            {"mode": "code_comparision", "help_text": "Create a prompt to verify original input vulnerable source code and patched code from GPT4 then request for comparision report"},
            {"mode": "code_comparision_report", "help_text": "Create a prompt to verify original input vulnerable source code, patched code from GPT4 and Developer patched code then request for comparision report"}
        ]
        self.llama2_config= {
            "model_name": "meta-llama/Llama-2-7b-chat-hf",
            "bnb_config": BitsAndBytesConfig(
                load_in_4bit=True, # Activate 4-bit precision base model loading
                bnb_4bit_quant_type="nf4", # Quantization type (fp4 or nf4)
                bnb_4bit_compute_dtype=getattr(torch, "float16"),
                bnb_4bit_use_double_quant=False, # Activate nested quantization for 4-bit base models (double quantization)
            )
        }
    
    def load_llama_model(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.llama2_config["model_name"],
            quantization_config=self.llama2_config["bnb_config"],
            device_map= {"": 0}
        )
        return model


class CodeAnalyzer(LLMModelLoader):
    def __init__(self) -> None:
        LLMModelLoader.__init__(self)
        self.report_data, self.llm_data= [], []
        self.threat_directory= '/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/threats/'
        self.root_directory= '/home/users/aswin1906/projects/ai/poc/llm/app/poc/code_guardian/'
    
    def threat_files(self) -> list:
        # Specify the directory path
        directory_path = self.threat_directory
        # List all files in the directory
        files = os.listdir(directory_path)
        # Filter out only files (exclude subdirectories)
        files = [directory_path+file for file in files if os.path.isfile(os.path.join(directory_path, file))]
        return files
    
    def build_prompt(self, llm_prompt_dict, content, prompt_mode, model_name, **kwargs) -> tuple:        
        if prompt_mode==self.prompt_mode[0]['mode']: #"threat_scanning"
            # question= f"""
            # Find the programming language, compiler name, ecosystem, supporting operating system, 
            # detailed description, vulnerability details, vulnerability type, Common Vulnerability Scoring System (CVSS) Score and 
            # Solve the code vulnerability by validating against Command Weakness Enumeration(CWE) and 
            # NATIONAL VULNERABILITY DATABASE(NVD) for the given code and find all related vulnerabilities:`{content}`

            # Reply the answer in JSON form with associated properties are programming_language, compiler_name, 
            # ecosystem, supporting_operating_system, detailed_description, vulnerability_details, vulnerability_type, 
            # cvss_score, fixed_source_code, cwe, nvd
            # """

            # - Vulnerability Details: Find out all the applicable vulnerabilities and explain one by one

            if model_name == "llama2":
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
                Given Vulnerable source code snippet is 
                {{
                    {content}
                }}

                Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
                supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey,
                static_code_analysis, conclusion

                """
            else:
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
                Given Vulnerable source code snippet is `{content}`

                Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, software_packages,
                supporting_operating_system, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd, literature_survey, 
                static_code_analysis, conclusion
                """

            self.llm_tpl= self.llm_vul_scan_tpl
            template_string = self.llm_vul_scan_tpl.format(question=question)
            llm_prompt_dict['llm_threat_scan_prompt']= template_string
        elif prompt_mode==self.prompt_mode[1]['mode']: #"code_comparision"
            question= f"""
            I have an original source code snippet that contains a known vulnerability, and a patched version of that snippet which is 
            intended to fix the vulnerability. Please analyze both versions and determine whether the patch correctly addresses the 
            vulnerability without introducing any new issues.

            Here is the original source code with the vulnerability:
            `{content}`

            Here is the patched source code:
            `{kwargs["patched_source_code"]}`

            Please assess the following:
            1. Does the patched code resolve the original vulnerability?
            2. Are there any new potential security issues introduced by the patch?
            3. Does the patched code maintain the original functionality and performance?
            4. Are there any best practices or coding standards that the patch does not adhere to?

            Provide a detailed analysis of the effectiveness of the patch in JSON form.

            """
            self.llm_tpl= self.llm_code_comparision_tpl
            template_string = self.llm_code_comparision_tpl.format(question=question)
            llm_prompt_dict['llm_code_comparision_prompt']= template_string
        elif prompt_mode==self.prompt_mode[2]['mode']: #"code_comparision_report"
            question= f"""
            I have two patches for a piece of source code that are intended to fix a specific security vulnerability. 
            One patch is from developers committed in github and another patch is from gpt response. 
            Please analyze both patches and determine which one more effectively mitigates the vulnerability, considering 
            the potential for introducing new vulnerabilities and overall security best practices.

            Here is the description of the original vulnerability:
            `{kwargs["executive_summary"]}`

            Here is the first patch from developer code:
            `{kwargs["developer_patched_source_code"]}`

            And here is the second patch from gpt4 response:
            `{kwargs["patched_source_code"]}`

            Please compare the two patches and provide an analysis of which is the better solution for the vulnerability in question, and explain why.

            """
            self.llm_tpl= self.llm_code_comparision_report_tpl
            template_string = self.llm_code_comparision_report_tpl.format(question=question)
            llm_prompt_dict['llm_dev_patch_comp_prompt']= template_string
        prompt = PromptTemplate(template=self.llm_tpl, input_variables=["question"]) 
        return prompt, question

    def run_llm(self, prompt, question, model_mode) -> str:
        if model_mode == "gpt4":
            llm_chain = LLMChain(prompt=prompt, llm=self.llm_gpt4)
            llm_result= llm_chain.run(question)
        elif model_mode == "gpt3.5" or model_mode == "gpt3_5":
            llm_chain = LLMChain(prompt=prompt, llm=self.llm_gpt3_5_turbo)
            llm_result= llm_chain.run(question)
        # print(f"[bold green]Fixed code from GPT4 is given below:\n{llm_result}[/bold green]")
        return llm_result

    def file_writing(self, file_name, content, mode= None):
        if mode=="json":
            file_path = self.root_directory+ "reports/" + file_name
            with open(file_path, 'w') as file:
                json.dump(content, file, indent=4)
        else:
            file_path = self.root_directory+ "fix/" + file_name
            with open(file_path, 'w') as file:
                file.writelines(content)

    def code_build(self, file_name):
        if file_name.endswith(".py"):
            import subprocess
            script_path = self.root_directory+ "fix/" + file_name
            try:
                completed_process = subprocess.run(['python', script_path], stderr=subprocess.PIPE, text=True, check=True)
                return 'Build Successfully'
                # print("Python Build Successful.")
            except subprocess.CalledProcessError as e:
                # print(f"Error running the script: [bold red]{e}[/bold red]")
                # print("Build Error output:")
                # print(f"[bold red]{e.stderr}[/bold red]")
                return f"Found Error in your python code. Find your error below\n[bold red]{e.stderr}[/bold red]"
    
    def gpt_to_dev_patch_comparision(self, llm_result_dict, llm_prompt_dict, developer_patch_content, original_source_code, mode):
        # Developer patch and LLM patch comparision using gpt4
        kwargs= {
            "executive_summary": llm_result_dict[mode][mode+"_threat_scanning_result"]["executive_summary"],
            "developer_patched_source_code": developer_patch_content,
            "patched_source_code": llm_result_dict[mode][mode+"_threat_scanning_result"]["fixed_source_code"]
        }
        prompt, question= self.build_prompt(llm_prompt_dict, original_source_code, self.prompt_mode[2]['mode'], mode, **kwargs)
        llm_result= self.run_llm(prompt, question, mode) 
        llm_result_temp= {}
        llm_result_temp[mode+ "_dev_patch_comp_result"]= llm_result
        # llm_result["id"]= id                 
        # gpt4_dev_patch_comp_results.append(llm_result)  
        llm_result_dict[mode][mode+"_dev_patch_comp_result"]= llm_result_temp 
        return llm_result_temp
    
    def analyze(self):        
        threat_files= self.threat_files()
        id= 0
        gpt4_vul_scan_results, gpt3_5_vul_scan_results = [], []
        gpt4_code_comparision_results, gpt3_5_code_comparision_results= [], []
        gpt4_dev_patch_comp_results, gpt3_5_dev_patch_comp_results= [], []
        final_results, all_prompts= [], []
        for file_path in threat_files:
            with open(file_path, 'r') as file:
                content = file.read()
                id= id+1
                llm_prompt_dict, llm_result_dict= {}, {"gpt4": {}, "gpt3_5": {}, "llama2": {}}  
                file_name= file_path.split('/')[-1]
                llm_result_dict["id"]= id                              
                llm_result_dict["vulnerabe_filename"]= file_name 

                # threat_scanning using gpt4            
                prompt, question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[0]['mode'], "gpt4")
                llm_result= self.run_llm(prompt, question, "gpt4")  
                import pdb;pdb.set_trace()          
                llm_result= json.loads(llm_result.strip()) # It creates new object 
                llm_result["id"]= id                 
                gpt4_vul_scan_results.append(llm_result)  
                llm_result_dict["gpt4"]["gpt4_threat_scanning_result"]= llm_result
                self.file_writing("gpt4_"+file_name, llm_result["fixed_source_code"])
                code_build_result= self.code_build("gpt4_"+file_name)
                llm_result_dict["gpt4"]["gpt4_code_build_result"]= code_build_result

                

                # threat_scanning using gpt3.5            
                prompt, question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[0]['mode'], "gpt3_5")
                llm_result= self.run_llm(prompt, question, "gpt3.5")                
                llm_result= json.loads(llm_result.strip()) # It creates new object
                llm_result["id"]= id               
                gpt3_5_vul_scan_results.append(llm_result)
                llm_result_dict["gpt3_5"]["gpt3_5_threat_scanning_result"]= llm_result
                self.file_writing("gpt3_5_"+file_name, llm_result["fixed_source_code"])
                code_build_result=self.code_build("gpt3_5_"+file_name)
                llm_result_dict["gpt3_5"]["gpt3_5_code_build_result"]= code_build_result

                # threat_scanning using llama2           
                # prompt, question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[0]['mode'], "gpt3_5")
                # llm_result= self.run_llm(prompt, question, "gpt3.5")                
                # llm_result= json.loads(llm_result.strip()) # It creates new object
                # llm_result["id"]= id               
                # gpt3_5_vul_scan_results.append(llm_result)
                # llm_result_dict["gpt3_5"]["gpt3_5_threat_scanning_result"]= llm_result
                # self.file_writing("gpt3_5_"+file_name, llm_result["fixed_source_code"])
                # code_build_result=self.code_build("gpt3_5_"+file_name)
                # llm_result_dict["gpt3_5"]["gpt3_5_code_build_result"]= code_build_result

                # threat_scanning using llama2 
                # llm_vul_scan_prompt, llm_vul_scan_question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[0]['mode'])
                # llm_vul_scan_result= self.run_llm(llm_vul_scan_prompt, llm_vul_scan_question, "llama2")


                # code_comparision using gpt4
                kwargs= {
                    "patched_source_code": llm_result_dict["gpt4"]["gpt4_threat_scanning_result"]["fixed_source_code"]
                }
                prompt, question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[1]['mode'], "gpt4", **kwargs)
                llm_result= self.run_llm(prompt, question, "gpt4") 
                llm_result= json.loads(llm_result.strip()) # It creates new object
                llm_result["id"]= id                 
                gpt4_code_comparision_results.append(llm_result)  
                llm_result_dict["gpt4"]["gpt4_code_comparision_result"]= llm_result    


                # code_comparision using gpt3.5
                kwargs= {
                    "patched_source_code": llm_result_dict["gpt3_5"]["gpt3_5_threat_scanning_result"]["fixed_source_code"]
                }
                prompt, question= self.build_prompt(llm_prompt_dict, content, self.prompt_mode[1]['mode'], "gpt3_5", **kwargs)
                llm_result= self.run_llm(prompt, question, "gpt3.5") 
                llm_result= json.loads(llm_result.strip()) # It creates new object
                llm_result["id"]= id                 
                gpt3_5_code_comparision_results.append(llm_result)  
                llm_result_dict["gpt3_5"]["gpt3_5_code_comparision_result"]= llm_result 

                # Developer patch and LLM patch comparision
                developer_patch_path = self.root_directory+ "developer_patch/" + file_name
                with open(developer_patch_path, 'r') as file:
                    developer_patch_content = file.read()
                    # Developer patch and LLM patch comparision using gpt4
                    gpt4_dev_patch_comp= self. gpt_to_dev_patch_comparision(llm_result_dict, llm_prompt_dict, developer_patch_content, content, "gpt4")
                    gpt4_dev_patch_comp["id"]= id 
                    gpt4_dev_patch_comp_results.append(gpt4_dev_patch_comp)

                    # Developer patch and LLM patch comparision using gpt3.5
                    gpt3_5_dev_patch_comp= self. gpt_to_dev_patch_comparision(llm_result_dict, llm_prompt_dict, developer_patch_content, content, "gpt3_5")
                    gpt3_5_dev_patch_comp["id"]= id 
                    gpt3_5_dev_patch_comp_results.append(gpt3_5_dev_patch_comp)
                
                # Developer patch and LLM patch cross comparision
                

                # import pdb;pdb.set_trace()
                # print(llm_result_dict)
                final_results.append(llm_result_dict)
                all_prompts.append(llm_prompt_dict)
                
        
        self.file_writing("gpt4_vul_scan_results.json", gpt4_vul_scan_results, "json")
        self.file_writing("gpt4_code_comparision_results.json", gpt4_code_comparision_results, "json")
        self.file_writing("gpt4_dev_patch_comp_results.json", gpt4_dev_patch_comp_results, "json")

        self.file_writing("gpt3_5_vul_scan_results.json", gpt3_5_vul_scan_results, "json")
        self.file_writing("gpt3_5_code_comparision_results.json", gpt3_5_code_comparision_results, "json")
        self.file_writing("gpt3_5_dev_patch_comp_results.json", gpt3_5_dev_patch_comp_results, "json")
                          
        self.file_writing("final_results.json", final_results, "json")
        self.file_writing("all_prompts.json", all_prompts, "json")

code_analyzer= CodeAnalyzer()
code_analyzer.analyze()