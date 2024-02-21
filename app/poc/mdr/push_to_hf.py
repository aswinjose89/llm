
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)




model = AutoModelForCausalLM.from_pretrained("llm_results/llama-2-7b-chat-mdr-qa")
tokenizer = AutoTokenizer.from_pretrained("llm_results/llama-2-7b-chat-mdr-qa")

#Hugging face upload
# huggingface-cli login
model.push_to_hub("aswin1906/llama-2-7b-chat-mdr-qa", use_auth_token=True)
tokenizer.push_to_hub("aswin1906/llama-2-7b-chat-mdr-qa", use_auth_token=True)