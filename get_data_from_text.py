import os
import re
import pandas as pd
from tqdm import tqdm

def get_files(directory):
    """
    Get all files in a directory and output a list of file names.
    """
    files = []
    for root, dirs, file_names in os.walk(directory):
        for file in file_names:
            files.append(os.path.join(root, file))
    return files

def remove_special_chars(text):
    """
    Remove special characters from the text.
    """
    return re.sub(r'[^\w\s]', '', text)

def remove_spaces(text):
    """
    Remove extra spaces from the text between paragraphs.
    """
    return re.sub(r'\n\s*\n', '\n', text)

def extract_quantitative_data(text):
    """
    Extract quantitative and qualitative data from the text.
    """
    quantitative_data = {}

    # Regex patterns to extract various data
    patterns = {
        "Project Name": r"Projets à financer\s*\|\s*(.*)",  # Capture the project name
        "Category of Activity": r"Partager ce projet\s*:\s*([\w\s-]+)\s+-",  # Extract category of activity
        "Location": r"- ([\w\s'-]+)\s+\((\d{2})\)",  # Capture city and department
        "Project Description": r"\|\s*([^|]+)\n",  # Capture the brief project description
        "Montant remboursé": r"([\d\s,.]+)\s*€\s*/\s*([\d\s,.]+)\s*€",  # Left: amount paid; Right: amount expected
        "Taux d’intérêt annuel": r"TAUX PAR AN\s*([\d,.]+)\s*%",  # Extract annual interest rate
        "Niveau de risque": r"NIVEAU DE RISQUE\*\s*([A-D]+.?)",  # Extract risk level
        "Durée": r"DURÉE\s*(\d+)\s*(mois|ans)",  # Extract loan duration and unit
        "Durée de financement": r"FINANCÉ EN\s*([\d\s,.]+)\s*(heures|minutes|jours)",  # Extract financing duration and unit
        "Chiffre d'affaires": r"Chiffre d'affaires\s*\((\d{4})\)\s*:\s*([\d\s,.]+)\s*€",  # Extract turnover and the year
        "Date de création": r"Date de création\s*:\s*(\d{4})",  # Extract creation date
        "Nombre de salariés": r"Nombre de salariés\s*:\s*(\d+)",  # Extract number of employees
        "Nombre de preteurs": r"([\d\s]+)\s+prêteurs",  # Extract number of lenders
    }


    # Apply each regex pattern and store the matches
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "Montant remboursé":  # Separate the paid and expected amounts
                quantitative_data["Montant Levé"] = match.group(1).replace(" ", "").replace(",", ".")
                quantitative_data["Montant Demandé"] = match.group(2).replace(" ", "").replace(",", ".")
            elif key == "Taux d’intérêt annuel":  # Convert the interest rate to a decimal
                quantitative_data[key] = float(match.group(1).replace(",", ".")) / 100
            elif key == "Durée" or key == "Durée de financement":  # Split duration into value and unit
                quantitative_data[key + " (value)"] = match.group(1).replace(" ", "")
                quantitative_data[key + " (unit)"] = match.group(2)
            elif key == "Location":  # Split the location into city and department
                quantitative_data["City"] = match.group(1).strip()
                quantitative_data["Department"] = match.group(2)
            elif key == "Project Name":  # Ensure spaces are retained in the project name
                quantitative_data[key] = match.group(1).strip()
            elif key == "Project Description":  # Capture the specific description between the project name and the amount
                quantitative_data[key] = match.group(1).strip().split("\n")[4] # Extract the 5th line as the description (0-indexed)
            elif key == "Chiffre d'affaires":  # Split the turnover into value and year
                quantitative_data[key + " (year)"] = match.group(1)
                quantitative_data[key + " (value)"] = match.group(2).replace(" ", "").replace(",", ".")
            elif key == "Date de création":  # Store the creation date as an integer
                quantitative_data[key] = int(match.group(1))
            elif key == "Nombre de salariés":  # Store the number of employees as an integer
                quantitative_data[key] = int(match.group(1).replace(" ", "").replace(",", "."))  # Remove spaces and commas
            elif key == "Nombre de preteurs":  # Store the number of lenders as an integer
                quantitative_data[key] = int(match.group(1).replace(" ", "").replace(",", "."))
            else:
                quantitative_data[key] = match.group(1).strip()

    return quantitative_data

def extract_qualitative_data(text):
    """
    Extract qualitative data such as 'A propos' text, 'Gouvernance' details, and 'Dirigeant' information.
    """
    qualitative_data = {}

    # Extract the text after "A propos" for NLP analysis
    about_match = re.search(r"A propos de(.*?)(?:Gouvernance|Dirigeants)", text, re.DOTALL)
    if about_match:
        about_lines = about_match.group(1).strip().split("\n")
        # The first line becomes "Dirigeant", the rest is joined back with '\n'
        qualitative_data["Entreprise"] = about_lines[0].strip()  # First line
        qualitative_data["A propos"] = "\n".join(line.strip() for line in about_lines[1:])  # Rest of the lines joined back

    return qualitative_data

def convert_columns_to_numeric(df):
    # Iterate through each column in the DataFrame
    for column in df.columns:
        try:
            # Attempt to convert the column to numeric, errors='ignore' keeps the original data for non-convertible columns
            df[column] = pd.to_numeric(df[column], errors='ignore')
        except Exception as e:
            print(f"Could not convert column {column} due to {str(e)}")
    
    return df



def extract_text_from_folder(folder_txt, limit=None):
    files = get_files(folder_txt)
    if limit:
        files = files[:limit]
    data = []
    
    for data_file in tqdm(files):
        with open(data_file, 'r', encoding='utf-8') as f:
            text = f.read()

        text = remove_spaces(text)

        # Extract quantitative data from the text
        quantitative_data = extract_quantitative_data(text)
    
        # Extract qualitative data from the text for NLP
        qualitative_data = extract_qualitative_data(text)
        
        # Combine quantitative and qualitative data into a single dictionary
        combined_data = {**quantitative_data, **qualitative_data}
        combined_data['file_name'] = os.path.basename(data_file)
        data.append(combined_data)
        df = pd.DataFrame(data).reset_index()
        df['Niveau de risque'] = df['Niveau de risque'].fillna('NC')
        df = df.fillna('N/A')
        df = convert_columns_to_numeric(df)
    return df

def main():
    folder_txt = "project_txt_files"  # Adjust the folder as needed
    data = extract_text_from_folder(folder_txt, limit=None)  # Limit the number of files to read
    
    data.loc[data['Durée (unit)'].isna(),'Durée (unit)'] = 'mois' # Default to months
    data.loc[data['Durée (value)'].isna(),'Durée (value)'].fillna(0, inplace=True) # Fill missing values with 0
    data['Durée (value)'] = data['Durée (value)'].replace('N/A', 0)


    data.loc[data['Durée de financement (unit)'].isna(),'Durée de financement (unit)'] = 'nc' # Default to 'nc' for missing values
    data.loc[data['Durée de financement (value)'].isna(),'Durée de financement (value)'] = -1 # Default to -1 for missing values
    data['Durée de financement (value)'] = data['Durée de financement (value)'].replace('N/A', -1)


    # Transform all of the duration values to total months
    data.loc[data['Durée (unit)'] == 'ans', 'Durée (value)'] *= 12  # Convert years to months
    # data.loc[data['Durée (unit)'] == 'mois', 'Durée (value)'] *= 1  # Convert months to months
    # Drop the original columns
    data = data.drop(columns=['Durée (unit)'])
    # data['Durée (mois)'] = data['Durée (value)']
    # data = data.drop(columns=['Durée (value)'])  # Drop the original column name

    # Transform all of the financing duration values to total minutes
    data['Durée de financement (value)'] = data['Durée de financement (value)'].astype(float)

    data.loc[data['Durée de financement (unit)'] == 'jours', 'Durée de financement (value)'] *= 24 * 60 # Convert days to hours
    data.loc[data['Durée de financement (unit)'] == 'minutes', 'Durée de financement (value)'] *= 1  # Convert minutes to hours
    data.loc[data['Durée de financement (unit)'] == 'heures', 'Durée de financement (value)'] *= 60  # Convert hours to hours
    # Drop the original columns
    data = data.drop(columns=['Durée de financement (unit)'])
    # data['Durée de financement (min)'] = data['Durée de financement (value)']
    # data = data.drop(columns=['Durée de financement (value)']) # Drop the original column name

    data = data.drop(columns=['index'])

    # Save the dataframe to a CSV file
    file_name = 'project_data.csv'
    data.to_csv(file_name, index=False, sep=';')
    print(f"Data saved to '{file_name}'")

if __name__ == "__main__":
    main()
