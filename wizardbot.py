import discord
from discord.ext import commands
from discord.utils import get
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import urllib.parse, urllib.request, re
import json

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('bot_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix='!', intents = intents)

    # \\START MUSIC BOT
    
    queues = {}
    voice_clients = {}
    youtube_base_url = 'https://www.youtube.com/'
    youtube_results_url = youtube_base_url + 'results?'
    youtube_watch_url = youtube_base_url + 'watch?v='
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is up and running!')

    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link=link)
    
    @client.command(name="play")
    async def play(ctx, *, link):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:

            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({
                    'search_query': link
                })

                content = urllib.request.urlopen(
                    youtube_results_url + query_string
                )

                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

                link = youtube_watch_url + search_results[0]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        except Exception as e:
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(link)
            await ctx.send("Added to the list of shit to play")
            print(e)

    @client.command(name="clear")
    async def clear_queue(ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send("There is no queue to clear")

    @client.command(name="pause")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

    @client.command(name="resume")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    @client.command(name="dc")
    async def stop(ctx):
        try:
            if ctx.guild.id in queues:
                queues[ctx.guild.id].clear()
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
        except Exception as e:
            print(e)

    @client.command(name="add")
    async def queue(ctx, *, url):
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(url)
        await ctx.send("Added to queue!")
    
    @client.command(name="skip")
    async def skip(ctx):
        voice_clients[ctx.guild.id].stop()
        await play_next(ctx)
        
    # //END MUSIC BOT
    
    # \\START HOF BOT
    
    path = './'

    database = "hofmsg.json"

    
    def write_json(new_data, filename=database):
        with open(filename,'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)

            # Join new_data with file_data inside message_id
            file_data.append(new_data)

            # Sets file's current position at offset.
            file.seek(0)

            # convert back to json.
            json.dump(file_data, file, indent = 4)
            
    @client.event
    async def on_raw_reaction_add(payload):
        if payload.emoji.name == '⭐':
            # Get hall of fame channel
            hofChannel = client.get_channel(1236811026691788870)
            # Get related channel ids
            channel_id = payload.channel_id
            message_id = payload.message_id

            # Declare what and where the message is
            channel = client.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            # Set what reaction should be used
            reaction = get(message.reactions, emoji='⭐')

            if reaction and reaction.count >= 2:
                
                print(reaction.count)

                # Load the database
                data_check = json.loads(open(database).read())

                    # Check if the id already exists
                for i in data_check:
                    if i['id'] == message_id:
                        print("Message ID already found")
                        # If the id is found return
                        return

                # If there isn't an ID post the message
                try:
                    print("Attmepting to post attachment")
                    await hofChannel.send(f"`{message.author}` has just peaked:\n\n{message.content}\n{message.attachments[0]}\n\nOriginal Post:{message.jump_url}")
                except:
                    print("Failed, posting message without attachment")
                    await hofChannel.send(f"`{message.author}` has just peaked:\n\n{message.content}\n\nOriginal Post:{message.jump_url}")

                send_data = {"id":message.id}
                write_json(send_data)
                    
        elif payload.emoji.name == '✅' and payload.message_id == 1244337053982920815:
                guild_id = payload.guild_id
                guild = client.get_guild(guild_id) 
                role = get(payload.member.guild.roles, name='Role1')
                await payload.member.add_roles(role)
                return
    
    # //END HOF BOT
    
    # \\START OF ROLE BOT
    @client.command(name="seteventrole")
    async def eventset(ctx):
        react_channel_id = client.get_channel(1121928444255666287)
        react_msg = await react_channel_id.send(f"If you're seeing this mikel has sadly brought me back alive prepare for some autism and ramblings about me (he has no fucking clue what hes doing)")
        await react_msg.add_reaction('✅') 

    client.run(TOKEN)
