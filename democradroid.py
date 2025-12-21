"""democradroid.py

Python discord bot for interacting with democracyonline.io
"""

import discord
from discord import app_commands
import database as db
import dofuncs as do
import random as r

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

reprole_id = 1452114980366450845
senrole_id = 1452114652191391784
presrole_id = 1452114857846636637


async def role_for_party(guild, party_id):
    # Add a party role if it doesn't exist, else return existing role_for_party
    role_id = db.get_party_role(party_id)
    if role_id is not None:
        role = guild.get_role(int(role_id))
        if role is not None:
            return role
    party_info = do.fetch_party(party_id)
    if party_info is None:
        return None
    role_name = party_info["name"]  # type: ignore
    party_color = int(party_info["color"].lstrip("#"), 16)  # type: ignore
    role = await guild.create_role(name=role_name, color=discord.Color(party_color))
    db.add_party_role(party_id, str(role.id))
    return role


async def assign_party_role(guild, discord_id, democracyonline_id):
    do_user_info = do.fetch_user(democracyonline_id)
    if do_user_info is None:
        return
    party_id = do_user_info.get("party_id")  # type: ignore
    if party_id is None:
        return
    role = await role_for_party(guild, party_id)
    if role is None:
        return
    member = await guild.fetch_member(discord_id)
    if member is None:
        return
    await member.add_roles(role)


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
        print(f"User bio: {do_user_info['bio']}")  # type: ignore
        if record[4] in do_user_info["bio"]:  # type: ignore
            # Verified
            db.set_user_verified(record[0])
            await interaction.response.send_message(
                f"Your DemocracyOnline account (ID: {user_id}) has been successfully verified and linked to your Discord account ({discord_user_name})."
            )

            # Set party roles
            guild = interaction.guild
            if guild is not None:
                await assign_party_role(
                    guild, discord_user_id, record[2]
                )  # record[2] is democracyonline_id
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
    print(user)

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

        if do_user_info.get("party_id") is not None:  # type: ignore
            party_color = int(
                do.fetch_party(do_user_info["party_id"])["color"].lstrip("#"), 16  # type: ignore
            )
        else:
            party_color = 0x000000

        embed = discord.Embed(
            title="Your DemocracyOnline Account Information",
            color=discord.Color.from_rgb(
                party_color >> 16, (party_color >> 8) & 0xFF, party_color & 0xFF
            ),
        )
        embed.add_field(name="Username", value=do_user_info["username"], inline=False)  # type: ignore
        embed.add_field(name="User ID", value=do_user_info["id"], inline=False)  # type: ignore
        embed.add_field(name="Bio", value=do_user_info["bio"], inline=False)  # type: ignore
        embed.add_field(
            name="Account Created",
            value=do_user_info["created_at"],  # type: ignore
            inline=False,
        )

        # Add party role to user like wit verify
        guild = interaction.guild
        if guild is not None:
            await assign_party_role(
                guild, discord_user_id, user[2]
            )  # user[2] is democracyonline_id

        await interaction.response.send_message(embed=embed)


@tree.command(
    name="deletelink",
    description="Delete the link between your Discord account and your DemocracyOnline account",
)
async def deletelink(interaction, id: int = -1):
    if id != -1:
        if interaction.user.id != 357228102226542602:  # Replace with actual admin ID
            await interaction.response.send_message(
                "You do not have permission to delete other users' links. Message Georgie for help"
            )
            return
        user = db.get_user_by_discord_id(str(id))
        if user is None:
            await interaction.response.send_message(
                "The specified user does not have a linked DemocracyOnline account."
            )
            return
        db.delete_user(user[0])
        await interaction.response.send_message(
            f"The link between Discord user ID {id} and their DemocracyOnline account has been deleted."
        )
        return

    discord_user_id = str(interaction.user.id)
    user = db.get_user_by_discord_id(discord_user_id)

    if user is None:
        await interaction.response.send_message(
            "You do not have a linked DemocracyOnline account to delete."
        )
        return

    db.delete_user(user[0])
    await interaction.response.send_message(
        "Your link between your Discord account and your DemocracyOnline account has been deleted."
    )


@tree.command(
    name="processpartyroles",
    description="Assign party roles to all verified users based on their DemocracyOnline party affiliation",
)
async def processpartyroles(interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server."
        )
        return

    verified_users = db.get_all_verified_users()
    for user in verified_users:
        discord_user_id = user[1]
        democracyonline_id = user[2]
        do_user_info = do.fetch_user(democracyonline_id)
        if do_user_info is None:
            print(
                f"Could not fetch user info for DemocracyOnline ID {democracyonline_id}"
            )
            continue
        party_id = do_user_info.get("party_id")  # type: ignore
        if party_id is None:
            print(f"User {democracyonline_id} is not affiliated with any party.")
            continue
        role = await role_for_party(guild, party_id)
        if role is None:
            print(f"Could not create or fetch role for party ID {party_id}")
            continue
        member = await guild.fetch_member(discord_user_id)
        if member is None:
            print(f"Could not find member with Discord ID {discord_user_id}")
            continue
        await member.add_roles(role)
    await interaction.response.send_message(
        "Processed party roles for all verified users."
    )


@client.event
async def on_ready():
    # Check if db exists, if not create
    db.init_db()
    await tree.sync()
    print("Ready!")


with open(".token", "r") as f:
    token = f.read().strip()
client.run(token)
