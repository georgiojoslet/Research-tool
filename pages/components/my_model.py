# components/my_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class TinyLlamaSummarizer:
    def __init__(self, model_path: str = "qlora-finetuned-tinyllama"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_summary(self, prompt: str, max_new_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
