from openai import OpenAI
from load_env import model_name, api_key
from err_handler import handle_openai_err

client = OpenAI(api_key=api_key)


def ask_llm(
    user_content: str,
    system_content: str,
    model: str = model_name,
    temperature: float = 0.1,
    max_tokens: int = 2000,


) -> str:
    try:

        completions = client.chat.completions.create(
            model = model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            messages=[
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': user_content}
            ]
        )

        return completions.choices[0].message.content
    
    except Exception as e:
        return handle_openai_err(e)