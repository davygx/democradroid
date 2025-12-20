"""dofuncs.py

This module contains helper functions for the Democradroid bot.
"""

import requests

base_url = "https://democracyonline.io/api/"


def fetch_user(user_id):
    """Fetches the description of a user from democracyonline.io.

    Args:
        user_id (str): The ID of the user.
    Returns:
        requests.json: The data of the user.
    """

    url = f"{base_url}get-user-without-email"
    response = requests.post(url, json={"userId": user_id})
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error fetching user description."


if __name__ == "__main__":
    # Example usage
    user_id = "2"
    description = fetch_user(user_id)
    print(f"User Description: {description}")
