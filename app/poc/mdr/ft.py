

import os
import torch, pandas as pd
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig
from trl import SFTTrainer
import shutil

class FineTuning:
    def __init__(self, systemArgs) -> None:
        if "llama7b" in systemArgs:
            self.llama_base_model = "meta-llama/Llama-2-7b-chat-hf"
            if "qa" in systemArgs:
                print("Running llama7b qa...")
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-qa"
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
            if "tg" in systemArgs:    
                print("Running llama7b tg...")
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg"        
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv"
            if "chat" in systemArgs:    
                print("Running llama7b chat...")
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-chat"        
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"
            if "tg_ner" in systemArgs:    
                print("Running llama7b tg ner...")
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg-ner-v1.0"        
                self.ds_file_path_train= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_test.csv"
            if "tg_universal_ner" in systemArgs:    
                print("Running llama7b tg_universal_ner...")
                self.llama_base_model = "Universal-NER/UniNER-7B-all"
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg-universalner-v1.0"        
                self.ds_file_path_train= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_tg_ner/dataset_under_25_years_llama_tg_ner_test.csv"
        elif "llama13b" in systemArgs:
            self.llama_base_model = "meta-llama/Llama-2-13b-chat-hf"            
            if "qa" in systemArgs:      
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-qa"      
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
            if "tg" in systemArgs:    
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-tg" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv"
            if "chat" in systemArgs:    
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-chat" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"
        elif "mistral7b" in systemArgs:
            self.mistral_base_model = "mistralai/Mistral-7B-Instruct-v0.1"            
            if "qa" in systemArgs:      
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-qa"      
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
            if "tg" in systemArgs:    
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-tg" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv"
            if "chat" in systemArgs:    
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-chat" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"
        else:
            self.llama_base_model = "meta-llama/Llama-2-7b-chat-hf"
            self.ft_model = "llm_results/llama-2-7b-chat-mdr"
            self.ds_file_path= "./dataset/success/dataset_under_25_years_llama.csv"
        # self.mistral_base_model = "mistralai/Mistral-7B-Instruct-v0.1"
        self.redaction_dataset = "King-Harry/NinjaMasker-PII-Redaction-Dataset"
        self.train_dataset, self.test_dataset = self.load_custom_dataset()
        if hasattr(self, "llama_base_model"):
            self.llama_model, self.llama_tokenizer= self.load_llama2()
        elif hasattr(self, "mistral_base_model"):
            self.mistral_model, self.mistral_tokenizer= self.load_mistral()
    
    def load_custom_dataset(self):
        train_dataset = load_dataset("csv", data_files=self.ds_file_path_train, split="train")
        test_dataset = load_dataset("csv", data_files=self.ds_file_path_test, split="train")
        return train_dataset, test_dataset
    
    def quantization(self):
        compute_dtype = getattr(torch, "float16")
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=False,
        )
        return quant_config

    def load_llama2(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.llama_base_model,
            load_in_8bit=False,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        model.config.use_cache = False
        model.config.pretraining_tp = 1
        tokenizer = AutoTokenizer.from_pretrained(self.llama_base_model, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        return model, tokenizer
    
    def load_mistral(self):
        # Model to fine-tune
        model = AutoModelForCausalLM.from_pretrained(
            self.mistral_base_model,
            load_in_4bit=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        model.config.use_cache = False
        model.config.pretraining_tp = 1        
        tokenizer = AutoTokenizer.from_pretrained(self.mistral_base_model)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        return model, tokenizer

    def text_classification(self):
        pass

    def text_generation(self):
        pass

    def delete_all_folders_in_directory(self, directory):
        # Iterate over all the entries in the directory
        for entry in os.listdir(directory):
            # Create full path
            full_path = os.path.join(directory, entry)
            # Check if it's a directory
            if os.path.isdir(full_path):
                # Remove the directory and all its contents
                shutil.rmtree(full_path)
                print(f"Removed folder: {full_path}")

    def run_llama2(self, systemArgs):
        checkpoint_dir= "./llm_results/checkpoints/"+ '/'.join(systemArgs)
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.delete_all_folders_in_directory(checkpoint_dir)

        logs_dir= "./llm_results/logs/"+ '/'.join(systemArgs)
        os.makedirs(logs_dir, exist_ok=True)
        self.delete_all_folders_in_directory(logs_dir)
        peft_params = LoraConfig(
            lora_alpha=16,
            lora_dropout=0.1,
            r=64,
            bias="none",
            task_type="CAUSAL_LM",
        )
        training_params = TrainingArguments(
            output_dir=checkpoint_dir,
            logging_dir=logs_dir,
            num_train_epochs=4,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=1,
            optim="paged_adamw_32bit",
            save_steps=25,
            logging_steps=25,
            learning_rate=2e-4,
            weight_decay=0.001,
            fp16=False,
            bf16=False,
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_ratio=0.03,
            group_by_length=True,
            lr_scheduler_type="constant"
        )
        trainer = SFTTrainer(
            model=self.llama_model,
            train_dataset=self.train_dataset,
            eval_dataset=self.test_dataset,
            peft_config=peft_params,
            dataset_text_field="base_text",
            max_seq_length=None,
            tokenizer=self.llama_tokenizer,
            args=training_params,
            packing=False,
        )
        # Train model
        trainer.train()
        # Save trained model
        trainer.model.save_pretrained(self.ft_model)
        trainer.tokenizer.save_pretrained(self.ft_model)
    
    def run_mistral(self, systemArgs):
        checkpoint_dir= "./llm_results/checkpoints/"+ '/'.join(systemArgs)
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.delete_all_folders_in_directory(checkpoint_dir)

        logs_dir= "./llm_results/logs/"+ '/'.join(systemArgs)
        os.makedirs(logs_dir, exist_ok=True)
        self.delete_all_folders_in_directory(logs_dir)
        peft_params = LoraConfig(
            lora_alpha=16,
            lora_dropout=0.1,
            r=64,
            bias="none",
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
                "lm_head",
            ],
            task_type="CAUSAL_LM",
        )
        training_params = TrainingArguments(
            output_dir=checkpoint_dir,
            logging_dir=logs_dir,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=1,
            optim="paged_adamw_32bit",
            save_steps=25,
            logging_steps=25,
            learning_rate=2e-4,
            weight_decay=0.001,
            fp16=False,
            bf16=False,
            max_grad_norm=0.3,
            max_steps=-1,
            warmup_ratio=0.03,
            group_by_length=True,
            lr_scheduler_type="constant"
        )
        trainer = SFTTrainer(
            model=self.mistral_model,
            train_dataset=self.train_dataset,
            eval_dataset=self.test_dataset,
            peft_config=peft_params,
            dataset_text_field="base_text",
            max_seq_length=None,
            tokenizer=self.mistral_tokenizer,
            args=training_params,
            packing=False,
        )
        # Train model
        trainer.train()
        # Save trained model
        trainer.model.save_pretrained(self.ft_model)
        trainer.tokenizer.save_pretrained(self.ft_model)

    def run(self, systemArgs):
        if "llama7b" in systemArgs or "llama13b" in systemArgs or len(systemArgs)==0:
            self.run_llama2(systemArgs)
        if "mistral7b" in systemArgs or "mistral13b" in systemArgs or len(systemArgs)==0:
            self.run_mistral(systemArgs)

import sys
argumentList = sys.argv[1:]
FineTuning(argumentList).run(argumentList)


#time python ft.py llama7b tg_ner