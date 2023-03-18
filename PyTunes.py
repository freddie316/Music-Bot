"""
Author: Frederick Rice
Date: Thu Mar 16 2023

"""

import os
import asyncio
import yt_dlp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

ytdl_format_options = {
    "format": "m4a/bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "postprocessors": [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a'
    }],
}

ffmpeg_options = {"options": "-vn"}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guild:\n')
    for guild in bot.guilds:
        print(f'{guild.name} (id: {guild.id})\n')
    
@bot.command()
async def join(ctx):
    try:
        channel = ctx.author.voice.channel
    except:
        await ctx.reply("Are you in voice channel?")
        return
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()
    afk_timer.start()

@bot.command()
async def leave(ctx):
    try:
        if ctx.voice_client.is_playing():
            await stop(ctx)
        await ctx.voice_client.disconnect()
    except:
        await ctx.reply("I'm not connected to a voice channel.")
        return
    afk_timer.stop()

@bot.command()
async def play(ctx, url):
    try:
        if ctx.voice_client is None:
            await join(ctx)
        async with ctx.typing():
            source = ytdl.extract_info(url,download=True)
            filename = ytdl.prepare_filename(source)
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
            ctx.voice_client.play(song,
                after = lambda e: cleanup(filename)
            )
        await ctx.reply(f"Now playing: {source['title']}")
    except Exception as e:
        await ctx.reply(f"An error occured: {e}")   

def cleanup(filename):
    os.remove(filename)
    afk_timer.restart()
 
@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.reply("I'm not connected to a voice channel.")  
        return
    if not ctx.voice_client.is_playing():
        await ctx.reply("I'm not playing anything.")  
        return 
    ctx.voice_client.stop()
    
@bot.command()
async def ping(ctx):
    await ctx.reply("Pong!") 
    
@tasks.loop(seconds = 0)
async def afk_timer():
    await asyncio.sleep(300) # 5 minutes
    if not bot.voice_clients[0].is_playing():
        await bot.voice_clients[0].disconnect()
        afk_timer.stop()
    return

def main():
    bot.run(TOKEN)
    return

if __name__ == "__main__":
    main()