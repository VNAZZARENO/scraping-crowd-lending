from transformers import pipeline
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
import ast
from nltk.corpus import stopwords


def preprocess_text(text, translation_model):
    """
    Preprocess the text (if needed, you can add more preprocessing steps like stopword removal)
    """
    if translation_model:    
        stopword = stopwords.words('english')
    else:
        stopword = stopwords.words('french')
    text = re.sub(r'\s+', ' ', text.strip())  
    text = re.sub(r'\n', ' ', text)  
    text = ' '.join([word for word in text.split() if word.lower() not in stopword])

    return text


def translate_text(text, translation_model, max_token_length=512):
    """
    Translate French text to English using Hugging Face transformers.
    Handles long text by splitting it into smaller chunks.
    """
    translation_pipeline = pipeline("translation", model=translation_model)

    text_chunks = [text[i:i + max_token_length] for i in range(0, len(text), max_token_length)]
    translated_chunks = []
    for chunk in text_chunks:
        translation = translation_pipeline(chunk, max_length=max_token_length)[0]['translation_text']
        translated_chunks.append(translation)

    return ' '.join(translated_chunks)




def huggingface_analysis(text, task_type, model, max_token_length):
    """
    Perform analysis using Hugging Face transformers.
    Handles long texts by splitting them into smaller chunks if needed.
    """
    analysis_pipeline = pipeline(task_type, model=model)

    text_chunks = [text[i:i + max_token_length] for i in range(0, len(text), max_token_length)]
    results = []
    for chunk in text_chunks:
        result = analysis_pipeline(chunk)
        results.append(result[0]) 

    return aggregate_results(results, task_type)


def aggregate_results(results, task_type):
    """
    Aggregate results from multiple chunks.
    """
    if task_type == 'sentiment-analysis':
        labels = [res['label'] for res in results]
        most_common_label = max(set(labels), key=labels.count)
        scores = [res['score'] for res in results]
        avg_score = sum(scores) / len(scores)
        return {"label": most_common_label, "score": avg_score}

    elif task_type == 'text-classification':
        labels = [res['label'] for res in results]
        most_common_label = max(set(labels), key=labels.count)
        return {"label": most_common_label}

    return {"label": None, "score": 0}


def perform_nlp_analysis(text, task_type, model, max_token_length, translation_model=None):
    """
    Combine TextBlob and Hugging Face transformer-based analysis.
    Supports optional translation from French to English.
    """
    preprocessed_text = preprocess_text(text, translation_model)
    translated_text = preprocessed_text 
    if translation_model:
        translated_text = translate_text(preprocessed_text, translation_model, max_token_length)
    huggingface_result = huggingface_analysis(translated_text, task_type, model, max_token_length)
    return translated_text, huggingface_result


def create_nlp_features(df, task_type, model, max_token_length, text_columns, translation_model=None):
    """
    Create NLP features for each text column in the DataFrame and store translated text.
    """
    for col in text_columns:
        translated_texts = []
        sentiment_labels = []

        for row in tqdm(range(df.shape[0])):
            text = df.loc[row, col]
            translated_text, analysis_results = perform_nlp_analysis(text, task_type, model, max_token_length, translation_model)
            translated_texts.append(translated_text)
            sentiment_labels.append(analysis_results['label'])
        df[f'{col}_translated'] = translated_texts
        df[f'{col}_sentiment_label'] = sentiment_labels
    return df



try:
    df = pd.read_csv('project_data.csv', sep=';', encoding='utf-8', on_bad_lines='skip')
except pd.errors.ParserError as e:
    print(f"Error while parsing the file: {e}")
    exit(1)

task_type_sentiment = 'sentiment-analysis'
model_sentiment = 'nlptown/bert-base-multilingual-uncased-sentiment'
task_type_classification = 'text-classification'
model_classification = 'mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis'
translation_model = 'Helsinki-NLP/opus-mt-fr-en'
# summary_model = "facebook/bart-large-cnn"  
text_generation_model = ""
max_token_length = 512
text_columns = ['A propos', 'Project Description']
# df = create_nlp_features(df.sample(10, random_state=42).reset_index(drop=True), task_type_sentiment, model_sentiment, max_token_length, text_columns, translation_model)
df_nlp = create_nlp_features(df, task_type_classification, model_classification, max_token_length, text_columns, translation_model)
df_nlp.to_csv('project_data_class_eng.csv', index=False, sep=';', decimal='.', encoding='utf-8')
print("NLP features with translation added and saved to 'project_data_class_eng.csv'")