from pathlib import Path

prompt_file = 'summarize_reviews.txt'
PROMPTS_DIR = Path(__file__).parent.parent / 'prompts'


def prompt_load(prompt_file_name):
    try:
        with open(PROMPTS_DIR / prompt_file_name, 'r', encoding='utf-8') as f:
            file_content = f.read()

        if not file_content.strip():
            raise ValueError(f'{prompt_file_name} is empty')
        return file_content
    except FileNotFoundError:
        raise FileNotFoundError(f'{prompt_file_name} is not found')
    
system_prompt = prompt_load(prompt_file)
