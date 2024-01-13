
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
import json
import os
from pathlib import Path
import openai
import torch

openai.api_key ="XXX"

GOOGLE_API_KEY="XXX"
openai_api_key="XXX"

genai.configure(api_key=GOOGLE_API_KEY)

class CveEvaluator:

    def __init__(self) -> None:
        self.device = "cuda" # the device to load the model onto
        self.mistral_model, self.misral_tokenizer= self.load_mistral()
        self.llama7b_model, self.llama7b_tokenizer= self.load_llama2_7b()
        self.cwe_report= []
        # self.llm_gpt4= ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4-1106-preview", max_tokens=4000)
        # self.llm_gpt4_tpl = """Question: {question}

        # Answer: Return the modified fixed programming code without any format change or any additional details."""  
    

    def load_mistral(self):
        model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        return model, tokenizer
    
    def load_llama2_7b(self):
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
        return model, tokenizer


    def general_template(self, input):
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
        return instruction


    def gemini_response(self, instruction):
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(instruction)
        full_response= response.text
        code_fix= response.text
        return full_response, code_fix

    def misral_response(self, instruction):
        messages = [            
            {"role": "user", "content": instruction}
        ]
        encodeds = self.misral_tokenizer.apply_chat_template(messages, return_tensors="pt")
        model_inputs = encodeds.to(self.device)
        self.mistral_model.to(self.device)
        generated_ids = self.mistral_model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
        decoded = self.misral_tokenizer.batch_decode(generated_ids)
        return decoded[0]

    def gpt4_response(self, instruction):
        response = openai.ChatCompletion.create(
              model="gpt-4-1106-preview",
              messages=[{"role": "system", "content": 'you are a cybersecurity analyst to find and fix vulnerability in computer code'},
                        {"role": "user", "content": instruction}              
              ],
              max_tokens=4000)
        content= response.choices[0].message.content
        return content

    def gpt3_5_response(self, instruction):
        response = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              messages=[{"role": "system", "content": 'you are a cybersecurity analyst to find and fix vulnerability in computer code'},
                        {"role": "user", "content": instruction}              
              ])
        content= response.choices[0].message.content
        return content

    def llama2_response(self, instruction):
        pipe = pipeline(task="text-generation", model=self.llama7b_model, tokenizer=self.llama7b_tokenizer, max_length=4000)
        result = pipe(f"<s>[INST] {instruction} [/INST]")
        response= result[0]['generated_text'].split('[/INST]')[-1]
        return response
    
    # def gpt4_response(self, instruction):
    #     template_string = self.llm_tpl.format(question=instruction)
    #     # print(template_string)
    #     prompt = PromptTemplate(template=self.llm_gpt4_tpl, input_variables=["question"]) 
    #     llm_chain = LLMChain(prompt=prompt, llm=self.llm_gpt4)
    #     llm_result= llm_chain.run(instruction)
    #     return llm_result7122412

    
    def save_output(self, content, code_fix, output_dir, file_name):
        # Create an output file with the same name in the output directory
        output_file_path = os.path.join(output_dir, file_name)
        with open(output_file_path, 'w') as output_file:
            output_file.write(content)
        
        code_fix_output_file_path = os.path.join(output_dir, file_name)
        # with open(code_fix_output_file_path, 'w') as output_file:
        #     output_file.write(code_fix)
    
    def save_instruction(self, instruction, instruction_file_path):
        with open(instruction_file_path, 'w') as inst_output_file:
            inst_output_file.write(instruction)
    
    def save_csv(self, output_path, values):
        import pandas as pd
        df = pd.DataFrame.from_dict(values)
        df.to_csv(output_path, index = False, header=True)
    
    def generate_report(self, output_path):
        self.save_csv(os.path.join(output_path, "cwe_report.csv"), self.cwe_report)

    def run(self):        
        root_path = os.path.dirname(os.path.abspath(__file__))
        # Get a list of all files in the folder
        vulnerable_folder_path= os.path.join(root_path, "vulnerable_codes")        
        cwe_folder_list = os.listdir(vulnerable_folder_path)
        output_dir = os.path.join(root_path, "output")        

        # Loop through each file and read its content
        for cwe_folder_name in cwe_folder_list:
            cwe_folder_path = os.path.join(vulnerable_folder_path, cwe_folder_name)
            cve_folder_list = os.listdir(cwe_folder_path)
            for cve_folder_name in cve_folder_list:                
                cve_folder_path = os.path.join(cwe_folder_path, cve_folder_name)
                full_content=""
                cve_folder_path = Path(cve_folder_path)
                for file_path in cve_folder_path.rglob('*'):   #Pick each CWE folder path
                    if os.path.isfile(file_path):
                        file_name= str(file_path).split('/')[-1]
                        if file_name.startswith('bad'):   
                            with open(file_path, 'r') as file:                            
                                content = file.read()
                                full_content= content+ "\n\n"
                            if full_content:
                                file_extention= Path(file_name).suffix
                                
                                cve_name= cve_folder_name
                                output_filename= cve_name+file_extention
                                # You can process the content of each file here
                                print(f"Processing Output File: {output_filename}")
                                instruction= self.general_template(full_content)
                                
                                #Save Instructions
                                instruction_file_path = os.path.join(output_dir, "instructions", cve_name+".instruction.txt")
                                self.save_instruction(instruction, instruction_file_path)

                                #For Gemini
                                response, code_fix= self.gemini_response(instruction)
                                gemini_output_dir= os.path.join(output_dir, "gemini")
                                self.save_output(response, code_fix, gemini_output_dir, output_filename)
                                
                                #For Mistral
                                response= self.misral_response(instruction)
                                mistral_output_dir= os.path.join(output_dir, "mistral")
                                self.save_output(response, None, mistral_output_dir, output_filename)

                                #For GPT4
                                response= self.gpt4_response(instruction)
                                gpt4_output_dir= os.path.join(output_dir, "gpt4")
                                self.save_output(response, None, gpt4_output_dir, output_filename)

                                #For GPT3.5
                                response= self.gpt3_5_response(instruction)
                                gpt35_output_dir= os.path.join(output_dir, "gpt3.5")
                                self.save_output(response, None, gpt35_output_dir, output_filename)

                                #For llama2
                                response= self.llama2_response(instruction)
                                llama2_7b_output_dir= os.path.join(output_dir, "llama2-7b")
                                self.save_output(response, None, llama2_7b_output_dir, output_filename)

                                self.cwe_report.append({'CWE': cwe_folder_name, 'CVE': cve_folder_name, 'Gemini': 3, 'Mistral': 3})
        
        output_report_path= os.path.join(output_dir, "report")
        self.generate_report(output_report_path)
                    

CveEvaluator().run()