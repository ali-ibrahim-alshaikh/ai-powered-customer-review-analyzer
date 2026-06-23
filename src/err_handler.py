from openai import (
    APIConnectionError,
    AuthenticationError,
)

import pandas as pd
from pandas.errors import (
    EmptyDataError,
    ParserError
)
from pathlib import Path

def handle_openai_err(err:Exception) -> str:

    if isinstance(err, APIConnectionError):
        return 'Failed to connect to OpenAI serverse.'
    
    if isinstance(err, AuthenticationError):
        return 'Invalid OpenAI API key.'
    
    return f'Unexpected error: {err}.'
    
def check_csv_file(file_path):
    file_path = Path(file_path)

    try:
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}.')
        
        if file_path.stat().st_size == 0:
            raise EmptyDataError('csv file is completely empty.')
    
    except FileNotFoundError as e:
        print(e)

    except EmptyDataError:
        print("The CSV file is empty or has no readable data")

    except ParserError:
        print("The CSV file format is invalid or corrupted.")

    except Exception as e:
        print(f"Unexpected error: {e}")