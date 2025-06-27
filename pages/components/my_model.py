# components/my_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "qlora-finetuned-tinyllama"  # your checkpoints folder
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.float16)
tokenizer.pad_token = tokenizer.eos_token

def generate_summary(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
