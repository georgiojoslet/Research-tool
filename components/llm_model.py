import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import streamlit as st

@st.cache_resource
def load_llm():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5", cache_dir="./local_models")
    model = AutoModelForCausalLM.from_pretrained("microsoft/phi-1_5", cache_dir="./local_models").to("cpu")
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model

if __name__ == "__main__":
    print("Loading LLM...")
    tokenizer, model = load_llm()
    print("✅ Model and tokenizer loaded and cached.")