import os

def load_token():
    """Load API token from a file, relative to the project root."""
    base_path = os.path.dirname(os.path.dirname(__file__))  # Go up from tools/ to project root
    token_path = os.path.join(base_path, "token.txt")

    with open(token_path, "r") as f:
        token = f.read().strip()
    return token
