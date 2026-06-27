import pandas as pd
from pandas.errors import EmptyDataError

from src.error_handler import check_csv_file

from src.env_validator import validate_env

from src.csv_processor import (
    data_file_path,
    analyze_review,
    get_output_filename,
    read_csv,
    save_csv
)

from src.load_env import (
    api_key,
    model_name
)

def main():

    try:
        validate_env(api_key, model_name)

        check_csv_file(data_file_path)

        df = read_csv(data_file_path)


        analyze_review(
            df=df
        )
        
        new_file_name = get_output_filename()

        save_csv(
            df=df,
            output_file_name=new_file_name
        )
    except FileNotFoundError as e:
        print(e)
        return
    except EmptyDataError as e:
        print(e)
        return

    except pd.errors.ParserError:
        print("The csv file format is invalid or corrupted.")
        return

    except ValueError as e:
        print(e)
        return

    except Exception as e:
        print(f"Unexpected error: {e}")
        return

if __name__ == '__main__':
    main()