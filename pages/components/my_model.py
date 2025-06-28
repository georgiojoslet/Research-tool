# components/my_model.py
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

class TinyLlamaSummarizer:
    def __init__(self,
                 base_model_path: str = "pages/components/base_tinyllama",
                 adapter_path: str = "pages/components/qlora-finetuned-tinyllama-final"):
        
        # Load base model and tokenizer from local path
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            device_map="auto",
            torch_dtype=torch.float16
        )

        # Apply the QLoRA adapter on top of base model
        self.model = PeftModel.from_pretrained(base_model, adapter_path)

        self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_summary(self, prompt: str, max_new_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
