from openai import OpenAI
from load_env import model_name, api_key

client = OpenAI(api_key=api_key)


def ask_llm(
    user: str,
    system: str,
    model: str = model_name,
    temperature: float = 0.1,
    max_tokens: int = 2000,


) -> str:
    completions = client.chat.completions.create(
        model = model,
        temperature=temperature,
        max_completion_tokens=max_tokens,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user}
        ]
    )

    return completions.choices[0].message.content