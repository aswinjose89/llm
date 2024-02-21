
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
import torch
from rich import print

class Inference:
    def __init__(self, systemArgs) -> None:
        if "llama7b" in systemArgs:
            # print("Running llama7b...")
            if "qa" in systemArgs:
                self.ft_model = "llama_results/llama-2-7b-chat-mdr-qa"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_qa.csv"   
            elif "tg" in systemArgs:
                self.ft_model = "llama_results/llama-2-7b-chat-mdr-tg"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv" 
            elif "chat" in systemArgs:
                self.ft_model = "llama_results/llama-2-7b-chat-mdr-chat"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv" 
            elif "tg_ner" in systemArgs:
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg-ner-v1.0"
                self.ds_file_path= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_train.csv"  
            elif "tg_universal_ner" in systemArgs:
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg-universalner-v1.0"
                self.ds_file_path= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_train.csv" 
        elif "llama13b" in systemArgs:
            print("Running llama13b...")
            if "qa" in systemArgs:
                self.ft_model = "llama_results/llama-2-13b-chat-mdr-qa"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_qa.csv"   
            elif "tg" in systemArgs:
                self.ft_model = "llama_results/llama-2-13b-chat-mdr-tg"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv" 
            elif "chat" in systemArgs:
                self.ft_model = "llama_results/llama-2-13b-chat-mdr-chat"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"              
        else:
            print("Running llama7b...")
            self.ft_model = "llama_results/llama-2-7b-chat-mdr"
            self.ds_file_path= "./dataset/success/dataset_under_25_years_llama.csv"        
        self.train_dataset, self.test_dataset = self.load_custom_dataset()
        self.llama_model, self.llama_tokenizer= self.load_llama2()
        self.redaction_dataset = "King-Harry/NinjaMasker-PII-Redaction-Dataset"

    def load_custom_dataset(self):
        dataset = load_dataset("csv", data_files=self.ds_file_path, split="train")
        train_dataset = dataset
        test_dataset = None
        return train_dataset, test_dataset
    
    def load_dataset(self):
        dataset= load_dataset(self.redaction_dataset)
        train_dataset = dataset['train']
        test_dataset = dataset['train']

        # Slice the datasets to get a limited number of samples
        # Replace 'num_samples' with the number of samples you want
        num_samples = 1000
        train_dataset = train_dataset.select(range(num_samples))
        test_dataset = test_dataset.select(range(num_samples))
        return train_dataset, test_dataset

    def load_llama2(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.ft_model,
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(self.ft_model)
        return model, tokenizer
    
    def llama_v2_prompt(self, messages):
          B_INST, E_INST = "[INST]", "[/INST]"
          B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
          BOS, EOS = "<s>", "</s>"
          DEFAULT_SYSTEM_PROMPT = f"""You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""

          if messages[0]["role"] != "system":
               messages = [
                    {
                         "role": "system",
                         "content": DEFAULT_SYSTEM_PROMPT,
                    }
               ] + messages
          messages = [
               {
                    "role": messages[1]["role"],
                    "content": B_SYS + messages[0]["content"] + E_SYS + messages[1]["content"],
               }
          ] + messages[2:]

          messages_list = [
               f"{BOS}{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} {EOS}"
               for prompt, answer in zip(messages[::2], messages[1::2])
          ]
          messages_list.append(f"{BOS}{B_INST} {(messages[-1]['content']).strip()} {E_INST}")

          return "".join(messages_list)
    
    def llama2_instruction_template(self, json_object, systemArgs): 
        if "qa" in systemArgs:
            instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{json_object['original_sentence']}```. Is this redactable or not?.
            """
        elif "tg" in systemArgs:
            instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{json_object['original_sentence']}```.
            """
        elif "chat" in systemArgs:
            instruction= f"""
            Does the sentence ```{json_object['original_sentence']}``` contain sensitive information?
            """
        elif "tg_ner" in systemArgs:
            instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{json_object['original_sentence']}```.
            """
        elif "tg_universal_ner" in systemArgs:
            instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{json_object['original_sentence']}```.
            """
        return instruction
    
    def get_llama2_response(self, row, systemArgs):
        # print(f"{row['base_text']}")
        instruction= self.llama2_instruction_template(row, systemArgs)
        pipe = pipeline(task="text-generation", model=self.llama_model, 
                        tokenizer=self.llama_tokenizer, 
                        temperature = 0.2,
                        # eos_token_id=self.llama7b_tokenizer.eos_token_id,   
                        max_length=400)
        print('*' * 20 + ' Started Inference '+ '*'*20)
        result = pipe(f"<s>[INSTRUCTION] {instruction} [/INSTRUCTION]")
        import pdb;pdb.set_trace()
        response= result[0]['generated_text']
        print(response)
        print('*' * 20 + ' Ended Inference '+ '*'*20)
    
    def get_llama2_chat_response(self, row, systemArgs, instruction):        
        pipe = pipeline(task="text-generation", model=self.llama_model, 
                        tokenizer=self.llama_tokenizer, 
                        temperature = 0.2,
                        # eos_token_id=self.llama7b_tokenizer.eos_token_id,   
                        max_length=400)
        print('*' * 20 + ' Started Inference '+ '*'*20)
        result = pipe(f"<s>[INST] {instruction} [/INST]")
        # import pdb;pdb.set_trace()
        response= result[0]['generated_text']
        print(response)
        print('*' * 20 + ' Ended Inference '+ '*'*20)
    

    def get_llama2_response_for_ui(self, row, systemArgs, instruction):
        # print(f"{row['base_text']}")
        # instruction= self.llama2_instruction_template(row, systemArgs)
        pipe = pipeline(task="text-generation", model=self.llama_model, 
                        tokenizer=self.llama_tokenizer, 
                        temperature = 0.2,
                        # eos_token_id=self.llama7b_tokenizer.eos_token_id,   
                        max_length=1000)
        # print('*' * 20 + ' Started Inference '+ '*'*20)
        result = pipe(f"<s>[INSTRUCTION] {instruction} [/INSTRUCTION]")
        # import pdb;pdb.set_trace()
        response= result[0]['generated_text']
        # response= response.split('INSTRUCTION]')[-1].split('####')[0]
        response= response.split('INSTRUCTION]')[-1].split('####')[0]
        # print(response)
        # print('*' * 20 + ' Ended Inference '+ '*'*20)
        return response

    def run(self, systemArgs, prompt_input= None):
        # train_dataset= self.train_dataset.filter(lambda row:row['is_redacted']==False)   
        # import pdb;pdb.set_trace()
        if prompt_input:
            prompt_input= prompt_input.split('"')[1] 
        row = self.train_dataset[0]
        if "llama7b" in systemArgs or "llama13b" in systemArgs or len(systemArgs)==0:
            if "chat" in systemArgs:
                print(f"{row['base_text']}")
                instruction1= f"""
                <<SYS>>\nPlease assist in identifying sensitive text that requires redaction in the document titled {row['title']}.\n<</SYS>>\n\n
                Does the sentence ```{row['original_sentence']}``` contain sensitive information?
                """
                instruction2= f"""
                <<SYS>>\nPlease assist in identifying sensitive text that requires redaction in the document titled {row['title']}.\n<</SYS>>\n\n
                What are the categories does fall into?
                """
                import pdb;pdb.set_trace()
                # instruction= self.llama2_instruction_template(row, systemArgs, instruction1)
                self.get_llama2_chat_response(row, systemArgs, instruction1)
            elif "llama7b" in systemArgs and "tg_ner" in systemArgs:
                instruction= f"""
                Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{prompt_input}```.
                """
                response= self.get_llama2_response_for_ui(row, systemArgs, instruction)
                return response
            elif "llama7b" in systemArgs and "tg_universal_ner" in systemArgs:
                instruction= f"""
                Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{prompt_input}```.
                """
                response= self.get_llama2_response_for_ui(row, systemArgs, instruction)
                return response
            else:
                self.get_llama2_response(row, systemArgs)
    
import sys
argumentList = sys.argv[1:]
# Inference(argumentList).run(argumentList)



# argumentList=["llama7b", "tg_ner"]
inf= Inference(argumentList)

print(f"[purple4] ------------------------------Info--------------------------")
print(f"[medium_spring_green] Text Redaction Using llama2 Model")
print(f"[purple4] -------------------------------------------------------------------")
while True:
    # prompt = 'What position does the player who played for butler cc (ks) play?'
    print("[bold blue]#Human: [bold green]", end="")
    user = input()
    print('[bold blue]#Response: [bold green]', inf.run(argumentList, user))