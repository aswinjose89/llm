
from datasets import load_dataset
import json, pandas as pd, os, copy

class DataPrep:
     def __init__(self, systemArgs) -> None:
        if "llama_qa" in systemArgs:
             self.op_file_path = f'./dataset/success/dataset_under_25_years_llama_qa.csv'             
        elif "llama_tg" in systemArgs:
             self.op_file_path = f'./dataset/success/dataset_under_25_years_llama_tg.csv'
        elif "llama_chat" in systemArgs:
             self.op_file_path = f'./dataset/success/dataset_under_25_years_llama_chat.csv'
        elif "gpt" in systemArgs:
             self.op_gpt_file_path = f'./dataset/success/dataset_under_25_years_llama_qa.jsonl'
        elif "llama_tg_ner" in systemArgs:
             self.op_file_path = f'./dataset/success/dataset_under_25_years_llama_tg_ner.csv'

        if "llama_qa_split" in systemArgs:
             self.source_file_path = f'./dataset/success/dataset_under_25_years_llama_qa.csv'
        elif "llama_tg_split" in systemArgs:
             self.source_file_path = f'./dataset/success/dataset_under_25_years_llama_tg.csv'
        elif "llama_chat_split" in systemArgs:
             self.source_file_path = f'./dataset/success/dataset_under_25_years_llama_chat.csv'
        elif "llama_tg_ner_split" in systemArgs:
             self.source_file_path = f'./dataset/success/dataset_under_25_years_llama_tg_ner.csv'
     
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
     
     def prepare_llama2_dataset(self, systemArgs):
          # train_dataset, test_dataset = self.load_dataset()
          redacted_file_path = f'./dataset/success/redacted_under_25_years.jsonl'
          op_file_path = self.op_file_path
          dataset= []
          with open(redacted_file_path, 'r') as redacted_file:
               for line in redacted_file:                    
                    # Parse the JSON object in each line
                    json_object = json.loads(line)
                    print(f"processing file id {json_object['id']}")
                    temp= {
                         "id": json_object["id"], 
                         "date": json_object["date"], 
                         "title": json_object["title"], 
                         "classification": json_object["classification"], 
                         "handling": json_object["handling"], 
                         "pubdate": json_object["pubdate"], 
                         "publisher": json_object["publisher"],
                    }
                    for row in json_object["body"]:
                         temp["original_sentence"]= row['sentence']
                         if "redacted" in row and row["redacted"]:
                              if "redactionCategory" in row:
                                   redactionCategory= f"and it is classified under the category {','.join(row['redactionCategory'])}"   
                                   redactionCategoryChat= ','.join(row['redactionCategory'])
                              else:
                                   redactionCategory= f"it's doesn't have any category"
                                   redactionCategoryChat= "It doesn't have any category"
                              if "llama_qa" in systemArgs:                                   
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. Is this redactable or not?. [/INSTRUCTION] Yes. It's Redactable {redactionCategory}. </s>"
                              elif "llama_tg" in systemArgs:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. [/INSTRUCTION] [BEGIN REDACTION] {row['sentence']} [END REDACTION] {redactionCategory}. </s>"
                              elif "llama_chat" in systemArgs:
                                   messages = [
                                        {
                                             "role": "system",
                                             "content": f"Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}."
                                        },
                                        {
                                             "role": "user",
                                             "content": f"Does the sentence ```{row['sentence']}``` contain sensitive information?"
                                        },
                                        {
                                             "role": "system",
                                             "content": "Yes, displaying this sentence could cause a security breach"
                                        },
                                        {
                                             "role": "user",
                                             "content": f"What are the categories does fall into?"
                                        },
                                        {
                                             "role": "system",
                                             "content": redactionCategoryChat
                                        }
                                   ]
                                   temp["base_text"]= self.llama_v2_prompt(messages)
                              else:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is {row['sentence']}. [/INSTRUCTION] [BEGIN REDACTION] {row['sentence']} [END REDACTION] {redactionCategory}. </s>"
                              temp["is_redacted"]= True
                              temp["redaction_category"]= redactionCategory
                         elif "redacted" not in row or not row["redacted"]:
                              if "llama_qa" in systemArgs:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. Is this redactable or not?. [/INSTRUCTION] No. It's not Redactable. </s>"
                              elif "llama_tg" in systemArgs:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. [/INSTRUCTION] {row['sentence']}. </s>"
                              elif "llama_chat" in systemArgs:
                                   messages = [
                                        {
                                             "role": "system",
                                             "content": f"Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}."
                                        },
                                        {
                                             "role": "user",
                                             "content": f"Does the sentence ```{row['sentence']}``` contain sensitive information?"
                                        },
                                        {
                                             "role": "system",
                                             "content": "No, it can display it to the public."
                                        },
                                        {
                                             "role": "user",
                                             "content": f"What are the categories does fall into?"
                                        },
                                        {
                                             "role": "system",
                                             "content": "No categories found."
                                        }
                                   ]
                                   temp["base_text"]= self.llama_v2_prompt(messages)
                              else:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. [/INSTRUCTION] {row['sentence']}. </s>"                             
                              temp["is_redacted"]= False
                              temp["redaction_category"]= None
                         dataset.append(copy.deepcopy(temp))
          df = pd.DataFrame(dataset)
          df.to_csv(op_file_path, index=False)
     
     def find_word_indices(self, sentence, word):
        start_index = sentence.find(word)
        if start_index != -1:  # Word found
            end_index = start_index + len(word) - 1
            return start_index, end_index
        else:
            return -1, -1  # Word not found
        
     def prepare_llama2_ner_dataset(self, systemArgs):
          redacted_file_path = f'./dataset/success/redacted_under_25_years_ner.jsonl'
          op_file_path = self.op_file_path
          dataset= []
          with open(redacted_file_path, 'r') as redacted_file:
               for line in redacted_file:                    
                    # Parse the JSON object in each line
                    json_object = json.loads(line)
                    print(f"processing file id {json_object['id']}")
                    temp= {
                         "id": json_object["id"], 
                         "date": json_object["date"], 
                         "title": json_object["title"], 
                         "classification": json_object["classification"], 
                         "handling": json_object["handling"], 
                         "pubdate": json_object["pubdate"], 
                         "publisher": json_object["publisher"],
                    }
                    for row in json_object["body"]:
                         # if json_object["id"] == 2010090102536:
                         #      import pdb;pdb.set_trace()
                         temp["original_sentence"]= row['sentence']

                         if "entities" in row and isinstance(row["entities"], list):
                              temp["is_redacted"]= True
                              temp["redacted_sentence"]= row['sentence']
                              for entity in row["entities"]:
                                   
                                   if "category" in entity and entity["category"]:
                                        # start_index, end_index= self.find_word_indices(temp["redacted_sentence"], entity["entity_value"])
                                        # temp["redacted_sentence"][start_index:end_index+1]= [entity["category"].upper()]
                                        word_to_replace = entity["entity_value"]
                                        replacement_word = "[" + entity["category"].upper() + "]"
                                        temp["redacted_sentence"]=temp["redacted_sentence"].replace(word_to_replace, replacement_word)
                                   else:
                                        print(f"No Category found for doc id: {json_object['id']}")

                              # if "llama_qa" in systemArgs:                                   
                              #      temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. Is this redactable or not?. [/INSTRUCTION] Yes. It's Redactable {redactionCategory}. </s>"
                              if "llama_tg_ner" in systemArgs:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. [/INSTRUCTION]. {temp['redacted_sentence']}####. </s>"
                              
                         else:
                              if "llama_tg_ner" in systemArgs:
                                   temp["base_text"]= f"<s>[INSTRUCTION] Please assist in identifying sensitive text that requires redaction in the document titled {json_object['title']}. The specific sentence under consideration is ```{row['sentence']}```. [/INSTRUCTION]. {row['sentence']}####. </s>"
                              temp["is_redacted"]= False
                         dataset.append(copy.deepcopy(temp))
          df = pd.DataFrame(dataset)
          df.to_csv(op_file_path, index=False)
     
     def data_split(self, systemArgs):
          if "llama_qa_split" in systemArgs:
               root_path= "./dataset/success/llama_qa"
               train_file_name= "dataset_under_25_years_llama_qa_train.csv"
               test_file_name= "dataset_under_25_years_llama_qa_test.csv"
          elif "llama_tg_split" in systemArgs:
               root_path= "./dataset/success/llama_tg"
               train_file_name= "dataset_under_25_years_llama_tg_train.csv"
               test_file_name= "dataset_under_25_years_llama_tg_test.csv"
          elif "llama_chat_split" in systemArgs:
               root_path= "./dataset/success/llama_chat"
               train_file_name= "dataset_under_25_years_llama_chat_train.csv"
               test_file_name= "dataset_under_25_years_llama_chat_test.csv"
          elif "llama_tg_ner_split" in systemArgs:
               root_path= "./dataset/success/llama_tg_ner"
               train_file_name= "dataset_under_25_years_llama_tg_ner_train.csv"
               test_file_name= "dataset_under_25_years_llama_tg_ner_test.csv"

          train_data_percent= 0.7
          training_dataset, test_dataset= [], []
          
          df= pd.read_csv(self.source_file_path)
          unique_doc_ids= df['id'].unique()
          os.makedirs(root_path, exist_ok=True)
          for doc_id in unique_doc_ids:
               df_records= df[df['id']==doc_id]
               training_samples_cnt= round(len(df_records) * train_data_percent)
               training_samples= df_records[:training_samples_cnt]               
               test_samples= df_records[training_samples_cnt+1:]
               training_dataset.append(training_samples)
               test_dataset.append(test_samples)
          training_samples_df = pd.concat(training_dataset, ignore_index=True)
          test_samples_df = pd.concat(test_dataset, ignore_index=True)
          train_file_path=os.path.join(root_path,train_file_name)
          test_file_path=os.path.join(root_path, test_file_name)
          training_samples_df.to_csv(train_file_path, index=False)
          test_samples_df.to_csv(test_file_path, index=False)
          print("Data seperation completed")


     def save_to_jsonl(self, dataset, file_path):
        with open(file_path, 'w') as file:
            for sample in dataset:
                json_line = json.dumps(sample)
                file.write(json_line + '\n')
        print("Dataset created successfully!!")

     def gpt_turbo_prompt(self, document, document_body):
          prompt= {
               "messages": [
                    {
                         "role": "system",
                         "content": f"Please assist in identifying sensitive text that requires redaction in the document titled {document['title']}."
                    },
                    {
                         "role": "user",
                         "content": f"When did the document has been published and tell me the publisher?"
                    },
                    {
                         "role": "assistant",
                         "content": f"This document published on {document['pubdate']} and published by {document['publisher']}"
                    }
               ]
          }
          for row in document_body:
               user= {
                    "role": "user",
                    "content": f"Does the sentence ```{row['sentence']}``` have any sensitive information and list out the categories if any?"
               }
               prompt["messages"].append(user)
               if "redacted" in row and row["redacted"]:    
                    if "redactionCategory" in row:
                         redactionCategory= f"Applicable categories are {','.join(row['redactionCategory'])}" 
                    else:
                         redactionCategory= f"It doesn't have any category" 
                                      
                    assistant= {
                         "role": "assistant",
                         "content": f"Yes, displaying this sentence could cause a security breach. {redactionCategory}"
                    }
                    prompt["messages"].append(assistant)
               else:
                    assistant= {
                         "role": "assistant",
                         "content": "No, it can display it to the public. Therefore, it doesn't have any category."
                    }
                    prompt["messages"].append(assistant)
          prompt["messages"].append({"role": "user", "content": "Thanks for helping me. You've been a great help."})
          prompt["messages"].append({"role": "assistant", "content": "You're welcome! It was a pleasure to assist you and talk with you. Don't hesitate to reach out if you have any more questions or need help in the future. I'm here for you aswin to find out the text redaction."})
          return prompt
     
     def prepare_gpt_dataset(self, systemArgs):
          redacted_file_path = f'./dataset/success/redacted_under_25_years.jsonl'
          dataset= []
          with open(redacted_file_path, 'r') as redacted_file:
               for line in redacted_file:                    
                    # Parse the JSON object in each line
                    json_object = json.loads(line)
                    print(f"processing file id {json_object['id']}")
                    doc_prompt= self.gpt_turbo_prompt(json_object, json_object["body"])
                    dataset.append(doc_prompt)
               self.save_to_jsonl(dataset, self.op_gpt_file_path)
                    # for row in json_object["body"]:
                    #      temp["original_sentence"]= row['sentence']
                    #      self.gpt_turbo_prompt(json_object["body"])
          
     def run(self, systemArgs):     
          if "llama_qa_split" in systemArgs or "llama_tg_ner_split" in systemArgs:
               self.data_split(systemArgs) 
          elif "llama_qa" in systemArgs or "llama_tg" in systemArgs or "llama_chat" in systemArgs:
               self.prepare_llama2_dataset(systemArgs)
          elif "llama_tg_ner" in systemArgs:
               self.prepare_llama2_ner_dataset(systemArgs)
          elif "gpt" in systemArgs:
               self.prepare_gpt_dataset(systemArgs)
          
import sys
argumentList = sys.argv[1:]
DataPrep(argumentList).run(argumentList)


"""
Arguments
python dataprep.py llama_qa
python dataprep.py llama_qa_split
"""


# messages = [
#      {
#           "role": "system",
#           "content": "You are a helpful, respectful, and honest assistant. Always answer as helpfully as possible, while being safe. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
#      },
#      {
#           "role": "user",
#           "content": f"Tell me the sentence ```{row['sentence']}``` have sensitive information?"
#      },
#      {
#           "role": "system",
#           "content": "Yes. Displaying this sentence cause security breach."
#      },
#      {
#           "role": "user",
#           "content": f"What are the categories fall in ```{row['sentence']}``?"
#      },
#      {
#           "role": "system",
#           "content": it is classified under the category Military Affairs,Security Infrastructure Vulnerabilities
#      }
# ]