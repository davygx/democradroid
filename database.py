"""database.py

This module handles database interactions for the Democradroid bot.
"""

import sqlite3


def init_db(db_name="democradroid.db"):
    """Initializes the database and creates necessary tables if they don't exist.

    Args:
        db_name (str): The name of the database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create a table for users
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            discord_id TEXT,
            democracyonline_id TEXT,
            verified INTEGER DEFAULT 0,
            verification_code TEXT DEFAULT NULL
        )
    """
    )

    conn.commit()
    conn.close()


def add_user(user_id, discord_id, democracyonline_id, db_name="democradroid.db"):
    """Adds a new user to the database.

    Args:
        user_id (str): The unique ID for the user.
        discord_id (str): The Discord ID of the user.
        democracyonline_id (str): The DemocracyOnline ID of the user.
        db_name (str): The name of the database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (id, discord_id, democracyonline_id)
        VALUES (?, ?, ?)
    """,
        (user_id, discord_id, democracyonline_id),
    )

    conn.commit()
    conn.close()


def get_user(user_id, db_name="democradroid.db"):
    """Retrieves a user from the database.

    Args:
        user_id (str): The unique ID for the user.
        db_name (str): The name of the database file.
    Returns:
        tuple: The user data.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users WHERE id = ?
    """,
        (user_id,),
    )
    user = cursor.fetchone()

    conn.close()
    return user


def get_user_by_discord_id(discord_id, db_name="democradroid.db"):
    """Retrieves a user from the database by their Discord ID.

    Args:
        discord_id (str): The Discord ID of the user.
        db_name (str): The name of the database file.
    Returns:
        tuple: The user data.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users WHERE discord_id = ?
    """,
        (discord_id,),
    )
    user = cursor.fetchone()

    conn.close()
    return user


def add_verification_code(user_id, code, db_name="democradroid.db"):
    """Adds a verification code for a user.

    Args:
        user_id (str): The unique ID for the user.
        code (str): The verification code.
        db_name (str): The name of the database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users SET verification_code = ? WHERE id = ?
    """,
        (code, user_id),
    )

    conn.commit()
    conn.close()


def set_user_verified(user_id, db_name="democradroid.db"):
    """Sets a user as verified.

    Args:
        user_id (str): The unique ID for the user.
        db_name (str): The name of the database file.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users SET verified = 1 WHERE id = ?
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()
