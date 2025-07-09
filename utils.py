import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def get_env_variable(var_name: str) -> str:
    """
    Retrieves an environment variable or raises an error if it's not set.
    """
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"The environment variable {var_name} is not set.")
    return value
