# ------------------------------------------------------------
# A bot programmed by Michael Davis in Discord.py 2024 - 2026
# ------------------------------------------------------------

# import all libraries
import urllib.parse, urllib.request, re, json, asyncio, yt_dlp, discord, os
from discord.ext import commands, has_permissions, CheckFailure
from discord.utils import get
from dotenv import load_dotenv

def run_client():
    # load envrionment and define command prefix
    load_dotenv()
    TOKEN = os.getenv('bot_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)

    # define some database paths into an array so we can call the one we need for the needed context.
    dblist = ['.\hofmsg.json', '.\serverlist.json', '.\rolemsg.json']
    chosendb = dblist[0]

    """db_hofMessage = '.\hofmsg.json'
    db_quoteMessage = '.\serverlist.json'
    db_roleMessage = '.\rolemsg.json'"""

    # write data to json databases.
    def store_data(new_data, filename=chosendb):
        with open(filename, 'r+') as file:

            file_data = json.load(file)
            file_data.append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent = 4)

    # establish a command to send a message and establish a simple react role giver.
    @client.command(name="seteventrole")
    async def set_role_msg(ctx):
        react_channel_id = client.get_channel(1121928444255666287)
        react_msg = await react_channel_id.send(f"Please react to this message to get the 'event' role.")
        await react_msg.add_reaction('✅')

    # TODO store ids into database and reference them later.
    @client.command(name="sethofChannel")
    @has_permissions(administrator=True)
    async def set_hall_channel(ctx):
        hofChannel_id = ctx.message.channel.id
        guild_id = ctx.message.guild.id

        dblist[0] = 'serverlist.json'

        print("IDs collected storing to " + dblist[0])
    
    @set_hall_channel.error
    async def set_hall_channel_error(error, ctx):
        if isinstance(error, CheckFailure):
            print("A user has attempted to use this command without admin permissions.")
    
    # this is a joke command
    @client.command(name="saia")
    async def saia_meme(ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/565998482880725004/1235392826049564742/saia.png?ex=697022ba&is=696ed13a&hm=389f2d28fdf986e208a0331fb746d81bb2e8a8264520d33062bb1afd13959650&")

    # Handle reactions on messages, instead of an event we've used on_raw_reaction_add which triggers when a reaction is added and looks at all messages, 
    # this is because it will check any messages for reactions which is what I want.
    @client.event
    async def on_raw_reaction_add(payload):
        if payload.emoji.name == '⭐':
            hofChannel = client.get_channel(1236811026691788870)
            channel_id = payload.channel_id
            message_id = payload.message_id

            channel = client.get_channel(channel_id)
            message = await channel.fetch_message(message_id)

            reaction = get(message.reactions, emoji='⭐')

            if reaction and reaction.count >= 2:
                # print(reaction.count)

                dblist[0] = '.\hofmsg.json'

                data_check = json.loads(open(chosendb).read())

                for i in data_check:
                    if i['id'] == message_id:
                        print("Message ID already found")
                        return
                    
            print("Attempting to post attachment")

            try:
                print("Attachment found, posted")
                await hofChannel.send(f"'{message.author}' has just peaked:\n\n{message.content}\n{message.attachments[0]}\n\nOriginal Post:{message.jump_url}")
            except:
                print("Failed, posting message without attachment")
                await hofChannel.send(f"'{message.author}' has just peaked!\n\n{message.content}\n\nOriginal Post:{message.jump_url}")

            send_data = {"id":message.id}
            store_data(send_data)

            print("Message stored in" + dblist[0])

        elif payload.emoji.name == '✅' and payload.message_id == 1244337053982920815:
            guild_id = payload.guild_id
            guild = client.get_guild(guild_id)
            role = get(payload.member.guild.roles, name='rolenamehere')
            await payload.member.add_roles(role)
            return

    client.run(TOKEN)