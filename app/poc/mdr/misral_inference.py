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

ds_file_path= "./dataset/success/dataset_under_25_years_llama_qa.csv" 

ft_model= "llama_results/Mixtral-8x7B-v0.1"
model = AutoModelForCausalLM.from_pretrained(
            ft_model,
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto"
        )
tokenizer = AutoTokenizer.from_pretrained(ft_model)

train_dataset = load_dataset("csv", data_files=ds_file_path, split="train")
train_dataset= train_dataset.filter(lambda row:row['is_redacted']==False)    
row = train_dataset[20]  

instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{row['original_sentence']}```. Is this redactable or not?.
            """

pipe = pipeline(task="text-generation", model=model, 
                tokenizer=tokenizer,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                temperature = 0.2,
                # eos_token_id=self.llama7b_tokenizer.eos_token_id,   
                max_length=400)

print(f"{row['base_text']}")
print('*' * 20 + ' Started Inference '+ '*'*20)
result = pipe(f"<s>[INST] {instruction} [/INST]")
# import pdb;pdb.set_trace()
response= result[0]['generated_text']
print(response)
print('*' * 20 + ' Ended Inference '+ '*'*20)