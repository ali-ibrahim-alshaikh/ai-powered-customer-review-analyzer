from prompt_load import system_prompt
from llm_client import ask_llm
from validate_env import validate_env
from load_env import api_key, model_name

def get_input():
    return input('I\'m OpenAI. Give me a review, and I\'ll summarize it: ')

def main():
    
    user_input = get_input()

    validate_env(api_key, model_name)

    response = ask_llm(system=system_prompt, user=user_input)
    print(response)

if __name__ == '__main__':
    main()