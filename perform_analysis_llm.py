from transformers import pipeline
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
import requests

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def call_lmstudio_api(messages, temperature, max_tokens):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        'model': 'qwen2.5-coder-7b-instruct'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with LM Studio: {e}")
        raise e

def create_features(processed_text, quantitative_data):
    qualitative_template = """
    <div class="project">
        <div class="title">{title}</div>
        <div class="risk">{risk}</div>
        <div class="risk_scale">{risk_scale}</div>
        <div class="challenges">{challenges}</div>
        <div class="challenges_scale">{challenges_scale}</div>
        <div class="core_objective">{core_objective}</div>
        <div class="core_objective_scale">{core_objective_scale}</div>
        <div class="resources">{resources}</div>
        <div class="resources_scale">{resources_scale}</div>
        <div class="expected_timeline">{expected_timeline}</div>
        <div class="expected_timeline_scale">{expected_timeline_scale}</div>
        <div class="market_demand">{market_demand}</div>
        <div class="market_demand_scale">{market_demand_scale}</div>
    </div>
    """

    prompt = f"""
    Description du projet:
    {processed_text}

    Variables quantitatives:
    {quantitative_data}

    Output HTML template:
    {qualitative_template}
    
    Instructions:

    - **Replace the placeholders with actual values.**
    - **Fill in qualitative features based on the project description and quantitative data.**
    - **The final output should be a well-formed HTML snippet.**
    - **Wrap the entire content with delimiters: <ANSWER> and </ANSWER>**
    """

    messages = [
        {"role": "assistant", "content": """You are a data scientist working on a project analysis task."""},
        {"role": "user", "content": prompt}
    ]

    chat_completion = call_lmstudio_api(
        messages=messages,
        temperature=0.5,
        max_tokens=3200
    )

    try:
        response_text = chat_completion['choices'][0]['message']['content'].strip()
        return response_text
    except (KeyError, IndexError) as e:
        print(f"Error extracting response: {e}")
        return "Error"

try:
    df = pd.read_csv('project_data.csv', sep=';', encoding='utf-8', on_bad_lines='skip')
except pd.errors.ParserError as e:
    print(f"Error while parsing the file: {e}")
    exit(1)

text_columns = ['A propos']
quantitative_columns = [
    'Department', 'Montant Demandé', 'Taux d’intérêt annuel', 'Durée (value)',
    'Durée de financement (value)', "Chiffre d'affaires (year)", "Chiffre d'affaires (value)",
    'Date de création', 'Nombre de salariés'
]

answers = {}
for col in text_columns:
    for row in tqdm(range(df.shape[0])):
        text = df.loc[row, col]
        if pd.isna(text) or text.strip() == '':
            continue

        processed_text = preprocess_text(text)
        quantitative_data = df.loc[row, quantitative_columns].to_dict()
        quantitative_data = str(quantitative_data)
        qualitative_data = create_features(processed_text, quantitative_data)

        try:
            processed_answers = qualitative_data.split("<ANSWER>")[1].split("</ANSWER>")[0].strip()
        except IndexError:
            processed_answers = "Error"
            print("Error extracting qualitative features for row:", row)

        answers[(row, col)] = processed_answers
        df.at[row, f"{col}_features"] = processed_answers

df.to_csv('df_augmented.csv', index=False, sep=';', decimal='.', encoding='utf-8')
print("Updated DataFrame saved to 'df_augmented.csv'.")
