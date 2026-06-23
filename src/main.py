from llm_client import ask_llm
from env_validate import validate_env
from csv_processes import create_customer_reviews_analyzed_file

from load_env import (
    api_key,
    model_name
)

def main():
    
    validate_env(api_key, model_name)

    create_customer_reviews_analyzed_file(need_summaries=True, need_sentiment=True, need_topics=True)
    
if __name__ == '__main__':
    main()