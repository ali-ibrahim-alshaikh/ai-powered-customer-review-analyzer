from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / 'prompts'


def prompt_load(prompt_type:str, prompt_file_name:str) -> str:
    try:
        with open(PROMPTS_DIR / prompt_type / prompt_file_name, 'r', encoding='utf-8') as f:
            file_content = f.read()

        if not file_content.strip():
            raise ValueError(f'{prompt_file_name} is empty')
        return file_content
    except FileNotFoundError:
        raise FileNotFoundError(f'{prompt_file_name} is not found')
    
