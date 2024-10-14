from transformers import pipeline
import pandas as pd
from tqdm import tqdm

def generate_responses(text, qa_model, questions):
    """
    Generate responses to a set of predefined questions using a QA model.
    """
    qa_pipeline = pipeline("question-answering", model=qa_model)
    
    responses = {}
    for question in questions:
        # print(f"\nGenerating response for question: '{question}'")
        try:
            # Use the question-answering pipeline for each question
            generated_response = qa_pipeline(question=question, context=text)['answer']
            responses[question] = generated_response
        except Exception as e:
            # print(f"Error generating response for question '{question}': {e}")
            responses[question] = "Error"

    return responses

def create_question_based_features(df, text_columns, qa_model, questions):
    """
    Create new features based on the generated responses to predefined questions.
    """
    for col in text_columns:
        # Initialize new columns for each question
        for question in questions:
            col_name = f"{col}_answer_{question.replace(' ', '_').replace('?', '')}"
            df[col_name] = ''

        # Iterate through the rows of the DataFrame
        for row in tqdm(range(df.shape[0])):
            text = df.loc[row, col]
            if pd.isna(text) or text.strip() == '':
                # print(f"Row {row} is empty, skipping...")
                continue

            # Generate responses to the questions
            responses = generate_responses(text, qa_model, questions)

            # Store the generated responses in new columns
            for question in questions:
                col_name = f"{col}_answer_{question.replace(' ', '_').replace('?', '')}"
                df.at[row, col_name] = responses[question]

    return df


questions = [
        "What is the core objective or mission of this project?",
        "What resources (financial, human, or technological) are required for the successful execution of this project?",
        "What market demand or customer need does this project address?",
        "What risks or challenges could affect the successful completion of this project?",
        "What is the expected timeline or schedule for the completion of this project?",
        "What are the key benefits or financial outcomes expected from this project?"
        ]


qa_model = "deepset/roberta-base-squad2"  # You can change this to any QA model

# max_token_length = 1028
# max_answer_length = 256

# Load the dataset
df = pd.read_csv('project_data_class_eng.csv', sep=';', encoding='utf-8', on_bad_lines='skip')
print(f"Loaded DataFrame with shape: {df.shape}")

# Define the columns to ask questions about (e.g., "A propos" and "Project Description")
text_columns = ['A propos_translated']

# Generate responses for each question and add them as new features
df_with_responses = create_question_based_features(df, text_columns, qa_model, questions)

# Save the DataFrame with new features to a CSV
df_with_responses.to_csv('project_data_with_responses.csv', index=False, sep=';', decimal='.', encoding='utf-8')
print("New question-based features added and saved to 'project_data_with_responses.csv'")


