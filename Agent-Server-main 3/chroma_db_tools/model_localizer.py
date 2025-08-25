import os

from transformers import AutoTokenizer, AutoModel

def download_model_to_local(local_path="./text2vec-base-chinese"):
    """将shibing624/text2vec-base-chinese模型下载到本地路径"""
    if not os.path.exists(local_path):
        print("开始下载模型...")
        tokenizer = AutoTokenizer.from_pretrained("shibing624/text2vec-base-chinese")
        model = AutoModel.from_pretrained("shibing624/text2vec-base-chinese")
        tokenizer.save_pretrained(local_path)
        model.save_pretrained(local_path)
        print(f"模型已成功下载到: {local_path}")
    else:
        print(f"使用已存在的本地模型: {local_path}")
    return local_path