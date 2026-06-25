from openai import (
    APIConnectionError,
    AuthenticationError,
)

from pandas.errors import (
    EmptyDataError
)

from pathlib import Path

def handle_openai_err(err:Exception) -> str:

    if isinstance(err, APIConnectionError):
        return 'Failed to connect to OpenAI serverse.'
    
    if isinstance(err, AuthenticationError):
        return 'Invalid OpenAI API key.'
    
    return f'Unexpected error: {err}.'
    

def check_csv_file(file_path: str | Path) -> None:
  
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.stat().st_size == 0:
        raise EmptyDataError("The csv file is completely empty.")