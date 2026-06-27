from pathlib import Path
import pandas as pd

from src.ai_enrichment import enrich_review
PROJECT_ROOT = Path(__file__).parent.parent

data_file_path = PROJECT_ROOT / 'data' / 'customer_review.csv'
outputs_files_path = PROJECT_ROOT / 'outputs'




def read_csv(data_path):
    df = pd.read_csv(data_path)

    if df.empty:
        raise ValueError("CSV file has columns but no rows.")
            
    df = df.head(3)
    return df

def get_output_filename():

    while True:
        name_new_file = input('Enter a name for the new file: ').strip()
        
        if not name_new_file.endswith('.csv'):
            name_new_file += '.csv'

        output_file_path = outputs_files_path / name_new_file

        if output_file_path.exists():
            print('This name already exists, try another one.')
        else:
            print(f'The {name_new_file} was created')
            return name_new_file

def analyze_review(df):

    results = []
    
    for review in df['review']:

        results.append(enrich_review(review=review))

    df['topic'] = [r.get('topic') for r in results]
    df['summary'] = [r.get('summary') for r in results]
    df['sentiment'] = [r.get('sentiment') for r in results]

    return df

def save_csv(df, output_file_name):
    df.to_csv(
        outputs_files_path / output_file_name,
        index=False
    )

