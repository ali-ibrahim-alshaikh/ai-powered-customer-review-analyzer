from src.prompt_variables import *
from pathlib import Path
from src.llm_client import ask_llm
import pandas as pd


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

def analyze_review(
        need_topics:bool,
        need_summaries:bool,
        need_sentiment:bool,
        df
        
):

    topics = []
    summaries = []
    sentiments = []

    for review in df['review']:

        user_prompt = user_template.format(review=review)
        if need_topics:
            topic = ask_llm(
                user_content=user_prompt,
                system_content=topic_extraction_prompt
            )
            topics.append(topic)
            

        if need_summaries:
            summary = ask_llm(
                user_content=user_prompt,
                system_content=summarize_reviews_prompt
            )
            summaries.append(summary)

        if need_sentiment:
            sentiment = ask_llm(
                user_content=user_prompt,
                system_content=sentiment_analysis_prompt
            )
            sentiments.append(sentiment)
        
    if need_topics:
        df['topic'] = topics

    if need_summaries:
        df['summary'] = summaries
        
    if need_sentiment:
        df['sentiment'] = sentiments

def save_csv(df, output_file_name):
    df.to_csv(
        outputs_files_path / output_file_name,
        index=False
    )

