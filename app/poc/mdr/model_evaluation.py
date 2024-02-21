from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
import torch, json, pandas as pd


class modelEvaluation:
    def __init__(self, systemArgs) -> None:
        if "llama7b" in systemArgs:
            print("Running llama7b...")
            if "qa" in systemArgs:
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-qa"
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
                self.llm_op_file_path= "./dataset/success/dataset_under_25_years_llama7b_qa_test_response.csv" 
            elif "tg" in systemArgs:
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-tg"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv" 
            elif "chat" in systemArgs:
                self.ft_model = "llm_results/llama-2-7b-chat-mdr-chat"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv" 
        elif "llama13b" in systemArgs:
            print("Running llama13b...")
            if "qa" in systemArgs:
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-qa"
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
                self.llm_op_file_path= "./dataset/success/dataset_under_25_years_llama13b_qa_test_response.csv"   
            elif "tg" in systemArgs:
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-tg"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv" 
            elif "chat" in systemArgs:
                self.ft_model = "llm_results/llama-2-13b-chat-mdr-chat"
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"   
        elif "mistral7b" in systemArgs:
            self.mistral_base_model = "mistralai/Mistral-7B-Instruct-v0.1"            
            if "qa" in systemArgs:      
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-qa"      
                self.ds_file_path_train= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_train.csv"
                self.ds_file_path_test= "./dataset/success/llama_qa/dataset_under_25_years_llama_qa_test.csv"
                self.llm_op_file_path= "./dataset/success/dataset_under_25_years_mistral7b_qa_test_response.csv" 
            if "tg" in systemArgs:    
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-tg" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_tg.csv"
            if "chat" in systemArgs:    
                self.ft_model = "llm_results/Mistral-7B-Instruct-v0.1-mdr-chat" 
                self.ds_file_path= "./dataset/success/dataset_under_25_years_llama_chat.csv"
        else:
            print("Running llama7b...")
            self.ft_model = "llm_results/llama-2-7b-chat-mdr"
            self.ds_file_path= "./dataset/success/dataset_under_25_years_llama.csv"        
        self.train_dataset, self.test_dataset = self.load_custom_dataset()
        self.llama_model, self.llama_tokenizer= self.load_llama2()

    def load_custom_dataset(self):
        train_dataset = load_dataset("csv", data_files=self.ds_file_path_train, split="train")
        test_dataset = load_dataset("csv", data_files=self.ds_file_path_test, split="train")
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
        return instruction
    
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
        return response
    
    def save_to_jsonl(self, dataset, file_path):
        with open(file_path, 'w') as file:
            for sample in dataset:
                json_line = json.dumps(sample)
                file.write(json_line + '\n')
        print("Dataset created successfully!!")
    
    def evaluate_llama(self, systemArgs):
        data_report= []
        test_dataset= self.test_dataset
        # train_dataset= self.train_dataset.filter(lambda row:row['is_redacted']==False) 
        # train_dataset = train_dataset[:2]
        
        for index in range(len(test_dataset)):  
            row= test_dataset[index] 
            instruction= self.llama2_instruction_template(row, systemArgs)
            response= self.get_llama2_chat_response(row, systemArgs, instruction)
            row["llm_respone"]= response
            answer= response.split("[/INST]")[-1].lower()
            if 'no' in answer:
                row["is_redacted_by_llm_model"]=  False
            elif 'yes' in answer:
                row["is_redacted_by_llm_model"]=  True
            else:
                row["is_redacted_by_llm_model"]=  None
            data_report.append(row)
        
        df= pd.DataFrame(data_report)
        df.to_csv(self.llm_op_file_path, index=False)

    def calculate_perplexity(self):
        model_name = self.ft_model  # Replace with the actual model ID
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        test_dataset= self.test_dataset.filter(lambda row:row['is_redacted']==True)    
        row = test_dataset[20]
        # text = "Your sample text here."
        instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{row['original_sentence']}```. Is this redactable or not?.
            """
        inputs = tokenizer(instruction, return_tensors="pt")
        # Get log likelihood from model output
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            log_likelihood = outputs.loss
        # Calculate perplexity
        perplexity = torch.exp(log_likelihood)
        perplexity = perplexity.item()
        return perplexity
    
    def all_sample_perplexity(self):
        model_name = self.ft_model  # Replace with the actual model ID
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        llm_op_test_dataset= load_dataset("csv", data_files=self.llm_op_file_path, split="train")
        # llm_model_response= llm_model_response.filter(lambda row:row['is_redacted']==True)

        dataset= []
        for index in range(llm_op_test_dataset.shape[0]):            
            row = llm_op_test_dataset[index]
            # text = "Your sample text here."
            instruction= f"""
                Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{row['original_sentence']}```. Is this redactable or not?.
                """
            inputs = tokenizer(instruction, return_tensors="pt")
            # Get log likelihood from model output
            with torch.no_grad():
                outputs = model(**inputs, labels=inputs["input_ids"])
                log_likelihood = outputs.loss
            # Calculate perplexity
            perplexity = torch.exp(log_likelihood)
            perplexity = perplexity.item()
            row["perplexity"]= perplexity
            dataset.append(row)
        df1 = pd.DataFrame(dataset)
        df1.to_csv(self.llm_op_file_path, index=False)

    
    def rouge_score(self, systemArgs):
        from rouge_score import rouge_scorer

        test_dataset= self.test_dataset.filter(lambda row:row['is_redacted']==True)    
        row = test_dataset[20]
        # text = "Your sample text here."
        instruction= f"""
            Please assist in identifying sensitive text that requires redaction in the document titled {row['title']}. The specific sentence under consideration is ```{row['original_sentence']}```. Is this redactable or not?.
            """
        # Corresponding reference summary
        reference_summary = instruction
        response= self.get_llama2_chat_response(row, systemArgs, instruction)

        # Example generated summary
        generated_summary = response

        # Initialize the ROUGE scorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

        # Calculate ROUGE scores
        scores = scorer.score(reference_summary, generated_summary)

        # Display the scores
        for score_type, score_values in scores.items():
            print(f"{score_type}:")
            print(f"  Precision: {score_values.precision:.4f}")
            print(f"  Recall: {score_values.recall:.4f}")
            print(f"  F1: {score_values.fmeasure:.4f}\n")
    
    def all_sample_rouge_score(self, systemArgs):
        from rouge_score import rouge_scorer

        llm_op_test_dataset= load_dataset("csv", data_files=self.llm_op_file_path, split="train")

        # llm_model_response= llm_model_response.filter(lambda row:row['is_redacted']==True)

        dataset= []
        for index in range(llm_op_test_dataset.shape[0]):            
            row = llm_op_test_dataset[index]
            x_test= row['base_text'].split('[/INSTRUCTION]')[-1].split('</s>')[0]            
            # Corresponding reference summary
            reference_summary = x_test
            y_test= row['llm_respone'].split('[/INST]')[-1].split('\n\n')[0]
            # Example generated summary
            generated_summary = y_test

            # Initialize the ROUGE scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

            # Calculate ROUGE scores
            scores = scorer.score(reference_summary, generated_summary)

            # Display the scores
            for score_type, score_values in scores.items():
                row[score_type+ "_precision"]= score_values.precision
                row[score_type+ "_recall"]= score_values.recall
                row[score_type+ "_f1_score"]= score_values.fmeasure
            dataset.append(row)
        df1 = pd.DataFrame(dataset)
        df1.to_csv(self.llm_op_file_path, index=False)
        
    
    def run(self, systemArgs):
        if ("llama7b" in systemArgs or "llama13b" in systemArgs or "mistral7b" in systemArgs) and "perplexity" in systemArgs:
            perplexity= self.calculate_perplexity()
            print(f"Perplexity: {perplexity:.2f}")
        elif ("llama7b" in systemArgs or "llama13b" in systemArgs or "mistral7b" in systemArgs) and "allsampleperplexity" in systemArgs:
            self.all_sample_perplexity()
        elif ("llama7b" in systemArgs or "llama13b" in systemArgs or "mistral7b" in systemArgs) and "rouge" in systemArgs:
            self.rouge_score(systemArgs)
        elif ("llama7b" in systemArgs or "llama13b" in systemArgs or "mistral7b" in systemArgs) and "allsamplerouge" in systemArgs:
            self.all_sample_rouge_score(systemArgs)
        elif "llama7b" in systemArgs or "llama13b" in systemArgs or "mistral7b" in systemArgs:
            self.evaluate_llama(systemArgs)


import sys
argumentList = sys.argv[1:]
modelEvaluation(argumentList).run(argumentList)

