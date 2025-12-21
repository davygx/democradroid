"""democradroid.py

Python discord bot for interacting with democracyonline.io
"""

import discord
from discord import app_commands
import database as db
import dofuncs as do
import random as r

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

reprole_id = 1452114980366450845
senrole_id = 1452114652191391784
presrole_id = 1452114857846636637


@tree.command(
    name="commandname",
    description="My first application Command",
)
async def first_command(interaction):
    await interaction.response.send_message("Hello!")


@tree.command(
    name="verify",
    description="Verify your DemocracyOnline account with your Discord account",
)
async def verify(interaction, user_id: str):
    # Get the Discord user ID
    discord_user_id = str(interaction.user.id)

    # Get the name of the Discord user
    discord_user_name = str(interaction.user)

    # Get the DemocracyOnline user info from the user ID
    do_user_info = do.fetch_user(user_id)
    if do_user_info is None:
        await interaction.response.send_message(
            "Could not find a DemocracyOnline user with that ID. Please check and try again."
        )
        return

    record = db.get_user_by_discord_id(discord_user_id)
    if record is None:
        # No record found, create a new one
        db.add_user(
            user_id=str(r.randint(10000000, 99999999)),
            discord_id=discord_user_id,
            democracyonline_id=user_id,
        )
        record = db.get_user_by_discord_id(discord_user_id)

    if record[3] == 1:
        await interaction.response.send_message(
            "Your DemocracyOnline account is already verified."
        )
        return

    if record[4] is not None:
        print("Checking for verification code in bio...")
        print(f"Verification code: {record[4]}")
        print(f"User bio: {do_user_info['bio']}")
        if record[4] in do_user_info["bio"]:  # type: ignore
            # Verified
            db.set_user_verified(record[0])
            await interaction.response.send_message(
                f"Your DemocracyOnline account (ID: {user_id}) has been successfully verified and linked to your Discord account ({discord_user_name})."
            )
            return

    # Generate a verification code
    vcode = r.randint(1000000000, 9999999999)
    db.add_verification_code(record[0], str(vcode))

    await interaction.response.send_message(
        f"To verify your DemocracyOnline account (ID: {user_id}), please add the following verification code to your DemocracyOnline bio: `{vcode}`. After updating your bio, please run the /verify command again."
    )


@tree.command(
    name="whoami",
    description="Get your linked DemocracyOnline account information",
)
async def whoami(interaction):
    discord_user_id = str(interaction.user.id)
    user = db.get_user_by_discord_id(discord_user_id)

    if user is None:
        await interaction.response.send_message(
            "You have not linked your DemocracyOnline account yet. Use /verify to link your account."
        )
        return

    if user[3] == 0:
        await interaction.response.send_message(
            "Your DemocracyOnline account is not verified yet. Please complete the verification process using /verify."
        )
        return
    else:
        do_user_info = do.fetch_user(user[2])
        if do_user_info is None:
            await interaction.response.send_message(
                "Could not retrieve your DemocracyOnline account information. Please try again later."
            )
            return

        embed = discord.Embed(
            title="Your DemocracyOnline Account Information",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Username", value=do_user_info["username"], inline=False)  # type: ignore
        embed.add_field(name="User ID", value=do_user_info["id"], inline=False)  # type: ignore
        embed.add_field(name="Bio", value=do_user_info["bio"], inline=False)  # type: ignore
        embed.add_field(
            name="Account Created",
            value=do_user_info["created_at"],  # type: ignore
            inline=False,
        )

        await interaction.response.send_message(embed=embed)


@client.event
async def on_ready():
    # Check if db exists, if not create
    db.init_db()
    await tree.sync()
    print("Ready!")


with open(".token", "r") as f:
    token = f.read().strip()
client.run(token)
