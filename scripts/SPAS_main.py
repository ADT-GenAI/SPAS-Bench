import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import ollama
import anthropic
import google.generativeai as genai
from openai import OpenAI as XAI
from tqdm import tqdm

# 載入模型 key 和 ID
load_dotenv(dotenv_path=r"C:\Users\DT25006\OneDrive - AUO DIGITECH PTE LTD\QIA Team\SPAS腳本\SPAS.env")

OLLAMA_MODEL_MAP = json.loads(os.getenv("OLLAMA_MODEL_MAPPING", "{}"))

MODEL_ID_MAP = {
    "GPT-4o": "gpt-4o",
    "gpt-4.5-preview": "gpt-4.5-preview",
    "Claude 3.5": "claude-3-5-sonnet-20241022",
    "Claude 3.5 Haiku": "claude-3-5-haiku-20240307", 
    "Claude 3.7": "claude-3-7-sonnet-20250219",
    "Gemini": "gemini-2.0-flash",
    "Grok 2": "grok-2-latest"
}

OPEN_SOURCE = ["Gemma 27B", "LLaMA Taiwan 70B", "LLaMA Taide", "LLaMA 3", "Mixtral 8x22B"]
CLOSED_SOURCE = ["GPT-4o", "gpt-4.5-preview", "Claude 3.5", "Claude 3.5 Haiku", "Claude 3.7", "Gemini", "Grok 2"]

# 統一 prompt 
def format_prompt(question: str) -> str:
    return f"""你是一個專業的製造業AI助理，請根據以下選擇題回答最適合的選項，並只輸出選項代號（例如 A、B、C、D）：

        {question}

        請直接回覆：A、B、C 或 D
    """

# 載入模型
def call_model(model_name: str, prompt: str) -> str:
    prompt = format_prompt(prompt)
    
    try:
        # ollama 模型
        if model_name in OPEN_SOURCE:
            model_id = OLLAMA_MODEL_MAP.get(model_name, model_name.lower().replace(" ", ""))
            return ollama.chat(model=model_id, messages=[{"role": "user", "content": prompt}])['message']['content']
        
        # GPT
        elif model_name in ["gpt-4.5-preview", "GPT-4o"]:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("需要在 .env 重新設定 OPENAI_API_KEY")     
            model_id = MODEL_ID_MAP.get(model_name, model_name.lower().replace(" ", ""))
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        # Claude
        elif model_name.startswith("Claude 3.5 Haiku"):
            api_key = os.getenv("CLAUDE_API_KEY")
            if not api_key:
                raise ValueError("需要在 .env 重新設定 CLAUDE_API_KEY")
            model_id = MODEL_ID_MAP.get(model_name, "claude-3-5-haiku-20240307")
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model_id,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        # Grok
        elif model_name == "Grok 2":
            api_key = os.getenv("XAI_API_KEY")
            if not api_key:
                raise ValueError("需要在 .env 重新設定 XAI_API_KEY")

            client = XAI(api_key=api_key, base_url="https://api.x.ai/v1/")
            response = client.chat.completions.create(
                model="grok-2-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        # Gemini
        elif model_name == "Gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("需要在 .env 重新設定 GEMINI_API_KEY")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name="gemini-2.0-flash")
            response = model.generate_content(prompt)
            return response.text
        
        else:
            return f"不支援的模型: {model_name}"   
    except Exception as e:
        return f"錯誤: {str(e)}"

# 載入題庫
def load_questions(filepath: str, limit: int = None) -> pd.DataFrame:
    df = pd.read_excel(filepath)
    df = df[['題目序號', '一級類別', '二級類別', '題目', '解答']]
    df.dropna(subset=['題目', '解答'], inplace=True)
    if limit:
        df = df.head(limit)
    return df

# 對答案
def evaluate_answer(pred: str, answer: str) -> bool:
    pred_clean = ''.join(c for c in pred if c.isalpha() or c.isspace()).strip().upper()
    return pred_clean.startswith(str(answer).strip().upper())

def run_evaluation(df: pd.DataFrame, models: List[str]) -> pd.DataFrame:
    results = []
    for model in models:
        print(f"[INFO] 測試模型: {model}")
        for _, row in tqdm(df.iterrows(), total=len(df)):
            try:
                pred = call_model(model, row['題目'])
                correct = evaluate_answer(pred, row['解答'])
                results.append({
                    '題目序號': row['題目序號'],
                    '模型': model,
                    '一級類別': row['一級類別'],
                    '二級類別': row['二級類別'],
                    '題目': row['題目'],
                    '解答': row['解答'],
                    '模型回答': pred,
                    '正確': correct
                })
            except Exception as e:
                print(f"[ERROR] {model} 回答題目 {row['題目序號']} 時發生錯誤: {e}")
                results.append({
                    '題目序號': row['題目序號'],
                    '模型': model,
                    '一級類別': row['一級類別'],
                    '二級類別': row['二級類別'],
                    '題目': row['題目'],
                    '解答': row['解答'],
                    '模型回答': f"[錯誤] {e}",
                    '正確': False
                })
    return pd.DataFrame(results)

# 存結果
def save_results_to_csv(results: pd.DataFrame, filename: str = "SPAS_results_llama3.3.csv"):
    results.to_csv(filename, index=False, encoding="utf-8-sig") 
    print(f"[INFO] 結果已儲存至 {filename}")


# main
if __name__ == "__main__":
    FILEPATH = r"C:\Users\DT25006\OneDrive - AUO DIGITECH PTE LTD\QIA Team\SPAS腳本\MQSA-Bench.xlsx"  # 題庫路徑
    # 可以測試多個模型
    MODELS = ["Claude 3.5 Haiku"]  # 調用模型名称  
    LIMIT = None  # 如果要限制測試題數，LIMIT = 10

    # 載入題庫
    df = load_questions(FILEPATH, LIMIT)
    print(f"[INFO] 載入 {len(df)} 道題目")
    
    # 執行評估
    results = run_evaluation(df, MODELS)
    
    # 儲存結果
    save_results_to_csv(results)
    print(f"[INFO] 評估結果已儲存至 results.csv")