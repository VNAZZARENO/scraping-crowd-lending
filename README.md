# NLP-Powered Project Analysis

## Project Overview

This project leverages **Natural Language Processing (NLP)** techniques to extract key insights from text data, specifically targeting project descriptions and overviews in the context of business or investment analysis. By combining powerful machine learning models from Hugging Face, this tool automates the process of text translation, sentiment analysis, and question-based feature extraction to assist in evaluating the potential success and risks of various projects.

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

1. **Prepare your data:** Ensure that your project data is in a CSV file format with relevant columns such as `A propos` or `Project Description`. This is where the text-based analysis will be performed.

2. **Run the NLP pipeline:**
   After setting up your environment and placing your data in the proper format, you can run the main analysis pipeline with the following command:

   ```bash
   python question_from_analysis.py

This will process the dataset, performing translation, sentiment analysis, and generating answers to predefined questions about each project.

    Outputs: The pipeline will add new columns to your dataset, including:
        Translated text for non-English columns
        Sentiment analysis scores
        Answers to key questions about the project

    Access Results: The results will be saved to a new CSV file named project_data_with_responses.csv.

## Example Questions for Feature Extraction

Here are some of the example questions the project attempts to answer for each project:

    What is the target market for this project?
    What are the key milestones for this project?
    What is the revenue model for this project?
    What are the growth projections for this project?
    What is the project's unique selling point?
    What potential risks might hinder the success of this project?
    What are the key strengths of this project?
    How scalable is the project in the current market?

These questions help analyze key components and insights related to the project's success.

## Model Usage

The project uses the following models from Hugging Face:

    Sentiment Analysis Model: nlptown/bert-base-multilingual-uncased-sentiment
    Text Translation Model: Helsinki-NLP/opus-mt-fr-en
    Text Generation Model: facebook/bart-large-cnn

