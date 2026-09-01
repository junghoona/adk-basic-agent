import requests
import os


# define a function to get exchange rate
def get_fx_rate(target: str):
    """
    Fetches the current exchange rate between two currencies. The base currency is USD and cannot be changed.
    
    Args:
                target: The target currency (e.g., "JPY").
    Returns:
                The exchange rate information as a json response, or None if the rate could not
                be fetched.
    """
    api_key = os.getenv("CF_API_KEY")
    api_url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}&symbols={target}"
  
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
