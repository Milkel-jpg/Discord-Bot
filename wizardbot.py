# ------------------------------------------------------------
# A bot programmed by Michael Davis in Discord.py 2024 - 2026
# ------------------------------------------------------------

# import all libraries
import urllib.parse, urllib.request, re, json, asyncio, yt_dlp, discord, os
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB = {
    "hof_DB": BASE_DIR / 'hofmsg.json',
    "server_DB": BASE_DIR / 'serverlist.json'
}

def run_client():
    # load envrionment and define command prefix
    load_dotenv()
    TOKEN = os.getenv('bot_token')
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    client = commands.Bot(command_prefix='!', intents = intents)
    # define some database paths into an array so we can call the one we need for the needed context.

    """db_hofMessage = '.\hofmsg.json'
    db_quoteMessage = '.\serverlist.json'
    db_roleMessage = '.\rolemsg.json'"""

    # write data to json databases.
    def store_data(filename: Path, new_data: dict):
        if not filename.exists():
            filename.write_text("[]", encoding="utf-8")

        with filename.open('r+', encoding="utf-8") as file:
            file_data = json.load(file)
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent = 4)
            file.truncate()

    # establish a command to send a message and establish a simple react role giver.
    @client.command(name="seteventrole")
    async def set_role_msg(ctx):
        react_channel_id = client.get_channel(1121928444255666287)
        react_msg = await react_channel_id.send(f"Please react to this message to get the 'event' role.")
        await react_msg.add_reaction('✅')

    # Handle reactions on messages, instead of an event we've used on_raw_reaction_add which triggers when a reaction is added and looks at all messages, 
    # this is because it will check any messages for reactions which is what I want.
    @client.event
    async def on_raw_reaction_add(payload):
        if payload.emoji.name == '⭐':
            print('reaction recieved')
            hofChannel = client.get_channel(1236811026691788870)
            channel_id = payload.channel_id
            message_id = payload.message_id

            channel = client.get_channel(channel_id)
            message = await channel.fetch_message(message_id)

            reaction = get(message.reactions, emoji='⭐')

            if reaction and reaction.count >= 1:
                print('reaction limit met')
                chosendb = DB["hof_DB"]
                data_check = json.loads(chosendb.read_text(encoding="utf-8"))

                for i in data_check:
                    if i['id'] == message_id:
                        print("Message ID already found")
                        return
                    
                print("Attempting to post attachment")

                try:
                    print("Attachment found, posted")
                    await hofChannel.send(f"`{message.author}` has just peaked:\n\n{message.content}\n{message.attachments[0]}\n\nOriginal Post:{message.jump_url}")
                except:
                    print("Failed, posting message without attachment")
                    await hofChannel.send(f"`{message.author}` has just peaked!\n\n{message.content}\n\nOriginal Post:{message.jump_url}")

                store_data(chosendb, {"id": message.id})

                print("Message stored in {chosendb.name}")

        if payload.emoji.name == 'RedditGold':
            print('reaction get')

            hofChannel = client.get_channel(1236811026691788870)
            channel_id = payload.channel_id
            message_id = payload.message_id

            channel = client.get_channel(channel_id)
            message = await channel.fetch_message(message_id)

            reaction = get(message.reactions, emoji=payload.emoji)

            print(reaction)

            if reaction and reaction.count >= 2:
                chosendb = DB["hof_DB"]
                data_check = json.loads(chosendb.read_text(encoding="utf-8"))

                for i in data_check:
                    if i['id'] == message_id:
                        print("Message ID already found")
                        return
                    
                print("Attempting to post attachment")

                try:
                    print("Attachment found, posted")
                    await hofChannel.send(f"Holy hecking chungus! `{message.author}` (OP) just unlocked humour:\n\n{message.content}\n{message.attachments[0]}\n\nOriginal Post:{message.jump_url}")
                except:
                    print("Failed, posting message without attachment")
                    await hofChannel.send(f"Holy hecking chungus! `{message.author}` has just unlocked humour:\n\n{message.content}\n\nOriginal Post:{message.jump_url}")

                store_data(chosendb, {"id": message.id})

                print("Message stored in {chosendb.name}")

        elif payload.emoji.name == '✅' and payload.message_id == 1244337053982920815:
            guild_id = payload.guild_id
            guild = client.get_guild(guild_id)
            role = get(payload.member.guild.roles, name='rolenamehere')
            await payload.member.add_roles(role)
            return

    client.run(TOKEN)