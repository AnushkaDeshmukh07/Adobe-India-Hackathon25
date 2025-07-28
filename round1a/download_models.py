import os
from transformers import AutoTokenizer, AutoModel
import torch

def download_models():
    model_dir = "./models"
    os.makedirs(model_dir, exist_ok=True)
    
    # Download lightweight BERT model for text analysis
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Save models locally
    tokenizer.save_pretrained(f"{model_dir}/tokenizer")
    model.save_pretrained(f"{model_dir}/model")
    
    print("Models downloaded successfully!")

if __name__ == "__main__":
    download_models()