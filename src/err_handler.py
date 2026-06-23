from openai import (
    APIConnectionError,
    AuthenticationError,
)

def handle_openai_err(err:Exception) -> str:

    if isinstance(err, APIConnectionError):
        return 'Failed to connect to OpenAI serverse.'
    
    if isinstance(err, AuthenticationError):
        return 'Invalid OpenAI API key.'
    
    return f'Unexpected error: {err}.'
    