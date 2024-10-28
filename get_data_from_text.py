import os
import re
import pandas as pd
from tqdm import tqdm

def get_files(directory):
    files = []
    for root, dirs, file_names in os.walk(directory):
        for file in file_names:
            files.append(os.path.join(root, file))
    return files

def remove_special_chars(text):
    return re.sub(r'[^\w\s]', '', text)

def remove_spaces(text):
    return re.sub(r'\n\s*\n', '\n', text)

def extract_quantitative_data(text):
    quantitative_data = {}

    patterns = {
        "Project Name": r"Projets à financer\s*\|\s*(.*)",
        "Category of Activity": r"Partager ce projet\s*:\s*([\w\s-]+)\s+-",
        "Location": r"- ([\w\s'-]+)\s+\((\d{2})\)",
        "Project Description": r"\|\s*([^|]+)\n",
        "Montant remboursé": r"([\d\s,.]+)\s*€\s*/\s*([\d\s,.]+)\s*€",
        "Taux d’intérêt annuel": r"TAUX PAR AN\s*([\d,.]+)\s*%",
        "Niveau de risque": r"NIVEAU DE RISQUE\*\s*([A-D]+.?)",
        "Durée": r"DURÉE\s*(\d+)\s*(mois|ans)",
        "Durée de financement": r"FINANCÉ EN\s*([\d\s,.]+)\s*(heures|minutes|jours)",
        "Chiffre d'affaires": r"Chiffre d'affaires\s*\((\d{4})\)\s*:\s*([\d\s,.]+)\s*€",
        "Date de création": r"Date de création\s*:\s*(\d{4})",
        "Nombre de salariés": r"Nombre de salariés\s*:\s*(\d+)",
        "Nombre de preteurs": r"([\d\s]+)\s+prêteurs",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            if key == "Montant remboursé":
                quantitative_data["Montant Levé"] = match.group(1).replace(" ", "").replace(",", ".")
                quantitative_data["Montant Demandé"] = match.group(2).replace(" ", "").replace(",", ".")
            elif key == "Taux d’intérêt annuel":
                quantitative_data[key] = float(match.group(1).replace(",", ".")) / 100
            elif key == "Durée" or key == "Durée de financement":
                quantitative_data[key + " (value)"] = match.group(1).replace(" ", "")
                quantitative_data[key + " (unit)"] = match.group(2)
            elif key == "Location":
                quantitative_data["City"] = match.group(1).strip()
                quantitative_data["Department"] = match.group(2)
            elif key == "Project Name":
                quantitative_data[key] = match.group(1).strip()
            elif key == "Project Description":
                quantitative_data[key] = match.group(1).strip().split("\n")[4]
            elif key == "Chiffre d'affaires":
                quantitative_data[key + " (year)"] = match.group(1)
                quantitative_data[key + " (value)"] = match.group(2).replace(" ", "").replace(",", ".")
            elif key == "Date de création":
                quantitative_data[key] = int(match.group(1))
            elif key == "Nombre de salariés":
                quantitative_data[key] = int(match.group(1).replace(" ", "").replace(",", "."))
            elif key == "Nombre de preteurs":
                quantitative_data[key] = int(match.group(1).replace(" ", "").replace(",", "."))
            else:
                quantitative_data[key] = match.group(1).strip()

    return quantitative_data

def extract_qualitative_data(text):
    qualitative_data = {}

    about_match = re.search(r"A propos de(.*?)(?:Gouvernance|Dirigeants)", text, re.DOTALL)
    if about_match:
        about_lines = about_match.group(1).strip().split("\n")
        qualitative_data["Entreprise"] = about_lines[0].strip()
        qualitative_data["A propos"] = "\n".join(line.strip() for line in about_lines[1:])

    return qualitative_data

def convert_columns_to_numeric(df):
    for column in df.columns:
        try:
            df[column] = pd.to_numeric(df[column])
        except Exception as e:
            pass
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

        quantitative_data = extract_quantitative_data(text)
        qualitative_data = extract_qualitative_data(text)
        
        combined_data = {**quantitative_data, **qualitative_data}
        combined_data['file_name'] = os.path.basename(data_file)
        data.append(combined_data)
        df = pd.DataFrame(data).reset_index()
        df['Niveau de risque'] = df['Niveau de risque'].fillna('NC')
        df = df.fillna('N/A')
        df = convert_columns_to_numeric(df)
    return df

def main():
    folder_txt = "project_txt_files"
    data = extract_text_from_folder(folder_txt, limit=None)
    
    data.loc[data['Durée (unit)'].isna(),'Durée (unit)'] = 'mois'
    data.loc[data['Durée (value)'].isna(),'Durée (value)'].fillna(0, inplace=True)
    data['Durée (value)'] = data['Durée (value)'].replace('N/A', 0)

    data.loc[data['Durée de financement (unit)'].isna(),'Durée de financement (unit)'] = 'nc'
    data.loc[data['Durée de financement (value)'].isna(),'Durée de financement (value)'] = -1
    data['Durée de financement (value)'] = data['Durée de financement (value)'].replace('N/A', -1)

    data.loc[data['Durée (unit)'] == 'ans', 'Durée (value)'] *= 12
    data = data.drop(columns=['Durée (unit)'])

    data['Durée de financement (value)'] = data['Durée de financement (value)'].astype(float)

    data.loc[data['Durée de financement (unit)'] == 'jours', 'Durée de financement (value)'] *= 24 * 60
    data.loc[data['Durée de financement (unit)'] == 'minutes', 'Durée de financement (value)'] *= 1
    data.loc[data['Durée de financement (unit)'] == 'heures', 'Durée de financement (value)'] *= 60
    data = data.drop(columns=['Durée de financement (unit)'])
    
    data = data.drop(columns=['index'])

    file_name = 'project_data.csv'
    data.to_csv(file_name, index=False, sep=';')
    print(f"Data saved to '{file_name}'")

if __name__ == "__main__":
    main()
