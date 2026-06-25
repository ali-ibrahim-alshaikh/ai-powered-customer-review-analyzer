def validate_env(
        api: str,
        model: str
) -> bool:
    if not api:
        raise ValueError('OPENAI_API_KEY is not found')
    if not model:
        raise ValueError('MODEL_NAME is not found')
    return True