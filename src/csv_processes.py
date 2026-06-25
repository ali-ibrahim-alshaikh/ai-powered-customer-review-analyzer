from prompt_variables import *
from pathlib import Path
from err_handler import check_csv_file
from llm_client import ask_llm
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent

data_file_path = PROJECT_ROOT / 'data' / 'customer_review.csv'
outputs_files_path = PROJECT_ROOT / 'outputs'


check_csv_file(data_file_path)

df = pd.read_csv(data_file_path)

if df.empty:
    raise ValueError("CSV file has columns but no rows.")
        
df = df.head(3)

while True:
    name_new_file = input('Enter a name for the new file: ').strip()
    
    if not name_new_file.endswith('.csv'):
        name_new_file += '.csv'

    output_file_path = outputs_files_path / name_new_file

    if output_file_path.exists():
        print('This name already exists, try another one.')
    else:
        print(f'The {name_new_file} was created')
        break

def create_customer_reviews_analyzed_file(
        need_topics:bool,
        need_summaries:bool,
        need_sentiment:bool,
        file_name:str = name_new_file
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

    df.to_csv(
        outputs_files_path / file_name,
        index=False
    )

