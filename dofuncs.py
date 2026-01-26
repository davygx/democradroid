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

    url = f"{base_url}bot?endpoint=users&id={user_id}"
    response = requests.get(url)
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

    url = f"{base_url}/bot?endpoint=parties&id={party_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error fetching party info."


def fetch_game_state_data_old() -> dict:
    """Fetches the game state data from democracyonline.io.
    Returns:
        requests.json: The game state data.
    """

    response = {}

    # Get senate election status
    url = f"{base_url}/election-info?election=Senate"
    senate_response = requests.get(url)
    if senate_response.status_code == 200:
        response["senate_election"] = senate_response.json().get("status")
        daysleft = senate_response.json().get("days_left", 0)
        if response["senate_election"] == "Candidate":
            response["senate_election"] = (
                f"Nominations are open! Stand as a candidate now! {daysleft} day(s) left until voting begins."
            )
        elif response["senate_election"] == "Voting":
            response["senate_election"] = (
                f"Senate elections are currently ongoing! {daysleft} day(s) left until elections conclude."
            )
        elif response["senate_election"] == "Concluded":
            response["senate_election"] = (
                f"Senate elections have concluded. {daysleft} day(s) until the next senate elections."
            )
    else:
        response["senate_election"] = "Error fetching senate election status."

    # Get president election status
    url = f"{base_url}/election-info?election=President"
    president_response = requests.get(url)
    if president_response.status_code == 200:
        response["president_election"] = president_response.json().get("status")
        daysleft = president_response.json().get("days_left", 0)
        if response["president_election"] == "Candidate":
            response["president_election"] = (
                f"Nominations are open! Stand as a candidate now! {daysleft} day(s) left until voting begins."
            )
        elif response["president_election"] == "Voting":
            response["president_election"] = (
                f"Presidential elections are currently ongoing! {daysleft} day(s) left until elections conclude."
            )
        elif response["president_election"] == "Concluded":
            response["president_election"] = (
                f"Presidential elections have concluded. {daysleft} day(s) until the next presidential elections."
            )
    else:
        response["president_election"] = "Error fetching president election status."

    # Get current house bills
    url = f"{base_url}/bills-get-voting?stage=House"
    house_bills_response = requests.get(url)
    if house_bills_response.status_code == 200:
        bills = house_bills_response.json().get("bills", [])
        response["current_house_bills"] = [
            ("#" + str(bill["id"]) + " - " + str(bill["title"])) for bill in bills
        ]
    else:
        response["current_house_bills"] = "Error fetching current house bills."

    # Get current senate bills
    url = f"{base_url}/bills-get-voting?stage=Senate"
    senate_bills_response = requests.get(url)
    if senate_bills_response.status_code == 200:
        bills = senate_bills_response.json().get("bills", [])
        response["current_senate_bills"] = [
            ("#" + str(bill["id"]) + " - " + str(bill["title"])) for bill in bills
        ]
    else:
        response["current_senate_bills"] = "Error fetching current senate bills."

    # Get current president bills
    url = f"{base_url}/bills-get-voting?stage=Presidential"
    president_bills_response = requests.get(url)
    if president_bills_response.status_code == 200:
        bills = president_bills_response.json().get("bills", [])
        response["current_presidential_bills"] = [
            ("#" + str(bill["id"]) + " - " + str(bill["title"])) for bill in bills
        ]
    else:
        response["current_presidential_bills"] = (
            "Error fetching current president bills."
        )

    return response


def fetch_game_state_data() -> dict:
    """Fetches the game state data from democracyonline.io.
    Returns:
        requests.json: The game state data.
    """

    url = f"{base_url}/bot?endpoint=game-state"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return {"error": "Error fetching game state data."}

    data = response.json()
    presdata = data[0]
    senatedata = data[1]

    returndata = {
        "president_election": presdata.get("status", "Unknown"),
        "senate_election": senatedata.get("status", "Unknown"),
        "current_presidential_bills": presdata.get(
            "bills_voting", ["Bill data coming soon."]
        ),
        "current_senate_bills": senatedata.get(
            "bills_voting", ["Bill data coming soon."]
        ),
        "current_house_bills": senatedata.get(
            "house_bills_voting", ["Bill data coming soon."]
        ),
    }

    if returndata["president_election"] == "Candidate":
        daysleft = presdata.get("daysLeft", 0)
        returndata["president_election"] = (
            f"Nominations are open! Stand as a candidate now! {daysleft} day(s) left until voting begins."
        )
    elif returndata["president_election"] == "Voting":
        daysleft = presdata.get("daysLeft", 0)
        returndata["president_election"] = (
            f"Presidential elections are currently ongoing! {daysleft} day(s) left until elections conclude."
        )
    elif returndata["president_election"] == "Concluded":
        daysleft = presdata.get("daysLeft", 0)
        returndata["president_election"] = (
            f"Presidential elections have concluded. {daysleft} day(s) until the next presidential elections."
        )
    if returndata["senate_election"] == "Candidate":
        daysleft = senatedata.get("daysLeft", 0)
        returndata["senate_election"] = (
            f"Nominations are open! Stand as a candidate now! {daysleft} day(s) left until voting begins."
        )
    elif returndata["senate_election"] == "Voting":
        daysleft = senatedata.get("daysLeft", 0)
        returndata["senate_election"] = (
            f"Senate elections are currently ongoing! {daysleft} day(s) left until elections conclude."
        )
    elif returndata["senate_election"] == "Concluded":
        daysleft = senatedata.get("daysLeft", 0)
        returndata["senate_election"] = (
            f"Senate elections have concluded. {daysleft} day(s) until the next senate elections."
        )

    return returndata


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
