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


def fetch_party(party_id):
    """Fetches the info of a party from democracyonline.io.
    Args:
        party_id (str): The ID of the party.
    Returns:
        requests.json: The data of the party.
    """

    url = f"{base_url}/get-party-by-id?partyId={party_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error fetching party info."


if __name__ == "__main__":
    # Example usage
    user_id = "159"
    description = fetch_user(user_id)
    print(f"User Description: {description}")
    party_id = description.get("party_id")  # type: ignore
    if party_id:
        party_info = fetch_party(party_id)
        print(f"Party Info: {party_info}")
    else:
        print("User is not affiliated with any party.")
