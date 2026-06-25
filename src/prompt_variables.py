from src.prompt_loader import prompt_load

user_prompt_folder = 'user'
system_prompt_folder = 'system'

summarize_reviews_file = 'summarize_reviews.txt'
sentiment_analysis_file = 'sentiment_analysis.txt'
topic_extraction_file = 'topic_extraction.txt'
user_review_file = 'review.txt'


summarize_reviews_prompt = prompt_load(system_prompt_folder, summarize_reviews_file)
sentiment_analysis_prompt = prompt_load(system_prompt_folder, sentiment_analysis_file)
topic_extraction_prompt = prompt_load(system_prompt_folder, topic_extraction_file)

user_template = prompt_load(user_prompt_folder, user_review_file)
