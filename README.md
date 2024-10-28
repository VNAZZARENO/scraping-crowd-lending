
# Data Extraction and Analysis from Pretup.fr Projects

Automation of scraping from Pretup.fr, extracts quantitative and qualitative information, and does a language model-based analysis. This should fetch information on crowd-lending projects and append them with generated insights from an LLM, to derive further model on counterparty risk.

## Table of Contents

- [Description](#description)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Scraping Project Data](#1-scraping-project-data)
  - [2. Extracting Data from Text Files](#2-extracting-data-from-text-files)
  - [3. Analyzing Information with the LLM](#3-analyzing-information-with-the-llm)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Notes](#notes)
- [License](#license)

## Description

The major components involved in the project are:

1. **Web Scraping** (`main.py`): Connect to Pretup.fr, browse through the projects and scrape off the textual content of the project(s).
2. **Data Extraction** (`get_data_from_text.py`): Takes the scraped text files (.txt) and extracts quantitative and qualitative data based on regular expressions.
3. **LLM-based Analysis** (`perform_analysis_llm.py`): With this, the llm does a deep dive into the project description by using a language model and further develops the dataset to derive new information.

## Prerequisites

- **Python 3.x**
- **Mozilla Firefox Browser**
- **GeckoDriver**: For Selenium to interact with Firefox.
- **LM Studio API or other LLM API**: Used to support analysis based on the language model.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/VNAZZARENO/scraping-crowd-lending.git
   cd scraping-crowd-lending
   ```

2. **Set Up a Virtual Environment** (Optional but Recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\\Scripts\\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download and Set Up GeckoDriver**

   - Download GeckoDriver from [Mozilla's GitHub Repository](https://github.com/mozilla/geckodriver/releases).
   - Place the `geckodriver` executable in your project directory or ensure it's in your system PATH.

5. **Configure Login Credentials**

   - In `main.py`, define your login credentials with Pretup.fr:

     ```python
     # main.py

     # Find the email input field and populate the field with your email
     email_input.send_keys("your_email@example.com")  # Replace with your actual email

     # Locate the password field and fill in your password
     password_input.send_keys("your_password")  # Replace with your actual password
     ```

## Usage

### 1. Scraping Project Data

Run `main.py` to log into Pretup.fr, scrape project pages, and save the text data.

```bash
python main.py
```

This script will:

- Log in to your account on Pretup.fr.
- Open the projects page and load all available projects.
- List URLs of all projects and save them to `project_urls.txt`.
- Scrape the text content of each project and save it in the `project_txt_files` directory.

### 2. Extracting Data from Text Files

Run `get_data_from_text.py` to process the text files and extract quantitative and qualitative data.

```bash
python get_data_from_text.py
```

This script will:

- Read all text files from the `project_txt_files` directory.
- Use regular expressions for data extraction, such as project name, category, amount, interest rate, duration, etc.
- Save the extracted data in a file called `project_data.csv`.

### 3. Checking with LLM

Run `perform_analysis_llm.py` to perform analysis using the language model:

```bash
python perform_analysis_llm.py
```

This script will:

- Read `project_data.csv`.
- For each project description, make a call to an LLM API to extract qualitative features.
- Store the augmented data in `df_augmented.csv`.

**Note**: Ensure the LLM API is up, running, and reachable at the specified endpoint in the script.

## Project Structure

```
yourprojectname/
├── main.py
├── get_data_from_text.py
├── perform_analysis_llm.py
├── requirements.txt
├── project_urls.txt
├── project_txt_files/
│   ├── project_1.txt
│   ├── project_2.txt
│   └── ...
├── fici_pdf/
│   ├── fici_project_1.pdf
│   ├── fici_project_2.pdf
│   └── ...
├── project_data.csv
├── df_augmented.csv
└── README.md
```

## Dependencies

- **Selenium**: For web scraping.
- **Requests**: For making HTTP requests.
- **pandas**: For data manipulation and analysis.
- **tqdm**: For progress bars in loops.
- **re**: For regular expressions.
- **Transformers**: For interacting with language models.
- **nltk**: For natural language processing tasks.
- **LM Studio API**: Or any other LLM API you are using.

## Notes

- **Ethical Considerations**: Ensure you have permission to scrape data from Pretup.fr and comply with their terms of service.
- **Error Handling**: Basic error handling is included, but additional effort might be required for production readiness.
- **Custom Paths**: Adjust file paths in the scripts if needed.
- **Environment Variables**: Consider using environment variables for sensitive information like login credentials.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Legal Disclaimer**: This project is for educational purposes only. The author is not responsible for any misuse of the scripts. Always follow legal and ethical guidelines when scraping data.
