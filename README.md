# Quantitative and NLP Crowd Lending Analysis

## Project Overview

This project leverages **Natural Language Processing (NLP)** techniques to extract key insights from text data, specifically targeting project descriptions and overviews in the context of business or investment analysis. By combining machine learning models from Hugging Face, this tool automates the process of text translation, sentiment analysis, and question-based feature extraction to assist in evaluating the potential success and risks of various projects.

Scraping is done using the library Selenium on a Firefox browser, regex is used to extract data that follows a clear structure, and NLP is for unformated text data. Finally, topics are generated using TfidfVectorizer from sklearn.feature_extraction.text.

## Key Features

- **Sentiment Analysis:**
  - Perform sentiment analysis on project descriptions and overviews to gauge the tone and confidence behind the provided information.

- **Text Translation:**
  - Automatically translate non-English text (e.g., French) into English using state-of-the-art translation models, facilitating seamless international project evaluations.

- **Question-Based Feature Extraction:**
  - Extract critical information by generating and answering key questions such as:
    - What is the target market for this project?
    - How scalable is the project in the current market?
    - What is the project's unique selling point?
    - What are the key risks and strengths of this project?

- **Automated Workflow:**
  - Provide an efficient and automated pipeline to process large datasets of project descriptions, allowing users to quickly assess multiple projects and make informed decisions.

## Installation

To run this project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nlp-powered-project-analysis.git

2. Navigate to the project directory:
   ```bash
   cd scraping-crowd-lending

3. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate # On Windows: 'env\Scripts\activate

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

## Usage

After setting up your environment and modifying the email adress and password variables you are ready to follow these steps.

1. **Prepare your data:** Ensure that your project data is in a CSV file format with relevant columns such as `A propos` or `Project Description`. This is where the text-based analysis will be performed. To do so, run:
   ```bash
   python main.py

2. **Create de main dataframe**
  You should have a folder with 1 text file of each urls scraped from `main.py`, to create the main dataframe run: 
   ```bash
   python perform_analysis.py

This will process the text files with regex, translate the open text fields, perform sentiment analysis, and output `project_data_class_eng.csv`. 

3. **Run the NLP pipeline:**
  After checking that `project_data_class_eng.csv` is indeed generated, you can perform the NLP analysis by running:

   ```bash
   python question_from_analysis.py

   Outputs: The pipeline will add new columns to your dataset, including:
        Translated text for non-English columns
        Sentiment analysis scores

This will take for input the `project_data_class_eng.csv`, and generate answers to predefined questions about each project. The list

    Outputs: The pipeline will add new columns to your dataset, including:
        Answers to key questions about the project

    Access Results: The results will be saved to a new CSV file named project_data_with_responses.csv.

## Example Questions for Feature Extraction

Here are some of the example questions the project attempts to answer for each project:

    What is the core objective or mission of this project?
    What resources (financial, human, or technological) are required for the successful execution of this project?
    What market demand or customer need does this project address?
    What risks or challenges could affect the successful completion of this project?
    What is the expected timeline or schedule for the completion of this project?
    What are the key benefits or financial outcomes expected from this project?

These questions help analyze key components and insights related to the project's success.

## Model Usage

The project uses the following models from Hugging Face:

    Sentiment Analysis Model: nlptown/bert-base-multilingual-uncased-sentiment
    Text Classification Model: mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis
    Text Translation Model: Helsinki-NLP/opus-mt-fr-en
    Text Question-Answering Model: deepset/roberta-base-squad2

