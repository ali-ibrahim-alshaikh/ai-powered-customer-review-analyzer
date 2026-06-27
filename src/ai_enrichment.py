from src.llm_client import ask_llm
from src.prompt_variables import (
        user_template,
        topic_extraction_prompt,
        summarize_reviews_prompt,
        sentiment_analysis_prompt
)


build_prompt = lambda review: user_template.format(review=review)

def add_topics(need_topics, prompt):
    if not need_topics:
        return None

    return ask_llm(
        user_content=prompt,
        system_content=topic_extraction_prompt
    )
                
def add_summaries(need_summaries, prompt):
    if not need_summaries:
        return None
        
    return ask_llm(
        user_content=prompt,
        system_content=summarize_reviews_prompt
    )
def add_sentiments(need_sentiment, prompt):
    if not need_sentiment:
        return None
    
    return ask_llm(
        user_content=prompt,
        system_content=sentiment_analysis_prompt
    )


def enrich_review(review):
    prompt = build_prompt(review)

    return {
        "topic": add_topics(True, prompt),
        "summary": add_summaries(True, prompt),
        "sentiment": add_sentiments(True, prompt),
        
    }