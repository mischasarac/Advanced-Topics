import replicate
import os
import json
from datetime import datetime

def extract_from_title(title, fallback_date=""):
    """
    Uses a Replicate LLM to extract ticker and date from a Binance article title.

    Args:
        title (str): The article title.
        fallback_date (str): Optional fallback date in YYYY-MM-DD format.

    Returns:
        dict: Dictionary containing extracted 'ticker' and 'date'.
    """

    # Set API token (set it securely in your environment or .env file)
    os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN", "your-token-here")

    prompt = f"""
Extract the *ticker symbol* and *date* from the following article title.
If no date is included, use {datetime.now().strftime("%Y-%m-%d")}
Return the result in JSON format with keys 'ticker' and 'date'.
Do not print anything except for the ticker and date json.

Title: "{title}" {fallback_date}
"""

    try:
        # Replace with your preferred model if needed
        output = replicate.run(
            "meta/meta-llama-3-8b-instruct",
            input={
                "prompt": prompt,
                "temperature": 0.3,
                "top_p": 1,
                "max_new_tokens": 200
            }
        )

        output_text = "".join(output)

        print("Raw model output:")
        print(output_text)

        # Try to parse a JSON response from the model output
        json_start = output_text.find('{')
        json_str = output_text[json_start:]
        result = json.loads(json_str)
        return result

    except Exception as e:
        print(f"LLM API call failed: {e}")
        return {"ticker": None, "date": ""}


# Example usage
title = "Defi App (HOME) Will Be Available on Binance Alpha and Binance Futures (2025-06-10)"
info = extract_from_title(title, fallback_date="2025-06-10")
print("Parsed result:", info)
