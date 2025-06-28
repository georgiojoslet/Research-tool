import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Ensure HF works in offline mode
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

class TinyLlamaSummarizer:

    def __init__(self,
                 base_model_path: str = "pages/components/base_tinyllama",
                 adapter_path: str = "pages/components/qlora-finetuned-tinyllama-final"):
        
        # Convert to Path for safety
        base_model_dir = Path(base_model_path)
        adapter_dir = Path(adapter_path)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load tokenizer and base model from local path
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_dir,
            local_files_only=True,
            trust_remote_code=True
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_dir,
            local_files_only=True,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16
        ).to(self.device)


        # Load the adapter on top of base model (also offline)
        self.model = PeftModel.from_pretrained(
            base_model,
            adapter_dir,
            local_files_only=True,
            trust_remote_code=True).to(self.device)


        self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_summary(self, prompt: str, max_new_tokens: int = 256) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
