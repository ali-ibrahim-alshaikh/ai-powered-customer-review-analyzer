from load_env import api_key, model_name

def validate_env(
        api: str,
        model: str
) -> ValueError:
    if not api:
        raise ValueError('OPENAI_API_KEY is not found')
    if not model:
        raise ValueError('MODEL_NAME is not found')
    return True