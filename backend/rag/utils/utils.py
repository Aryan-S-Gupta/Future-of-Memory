import re


def sanitise_string(text: str) -> str:
    """Replaces any number of consecutive whitespace characters with a single dash, keeps only 
    alphanumeric characters, and removes everything else. Used for converting text to a valid 
    filename.

    Args:
        text (str): text to sanitise

    Returns:
        str: sanitised string
    """
    
    # Step 1: Replace non-alphanumeric, non-whitespace with nothing
    cleaned = re.sub(r"[^\w\s]", "", text)

    # Step 2: Replace consecutive whitespace with a single underscore
    cleaned = re.sub(r"\s+", "_", cleaned.strip())

    return cleaned
