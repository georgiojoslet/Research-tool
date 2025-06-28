# components/llm_model.py
import os
from pathlib import Path
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM

# Tell HF to run in offline mode (never go to the Hub)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

@st.cache_resource
def load_llm():
    # point to the exact local folder
    model_dir = Path(__file__).parent / "local_models" / "phi-1_5"

    # pass the Path object directly
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        local_files_only=True,       # no network calls
        trust_remote_code=True       # if your model has custom code
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=True
    ).to("cpu")

    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model



if __name__ == "__main__":
    print("Loading LLM...")
    tokenizer, model = load_llm()
    print("✅ Model and tokenizer loaded and cached.")