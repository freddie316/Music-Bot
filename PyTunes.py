"""
Author: Frederick Rice
Date: Thu Mar 16 2023

"""

import os
import asyncio
import youtube_dl
import discord
from discord.ext import commands
from dotenv import load_dotenv

ytdl = youtube_dl.YoutubeDL()

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source: discord.AudioSource, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # Takes the first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename), data=data)

def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!',intents=intents)
    
    @bot.event
    async def on_ready():
        print(f'{bot.user} is connected to the following guild:\n')
        for guild in bot.guilds:
            print(f'{guild.name} (id: {guild.id})\n')
            #if guild.name == GUILD:
            #   break
        
    @bot.command()
    async def join(ctx):
        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.reply("Are you in voice channel?")  
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
    
    @bot.command()
    async def leave(ctx):
        try:
            if ctx.voice_client.is_playing():
                await stop(ctx)
            await ctx.voice_client.disconnect()
        except:
            await ctx.reply("I'm not connected to a voice channel.")
    
    @bot.command()
    async def play(ctx, url):
        try:
            if ctx.voice_client is None:
                await join(ctx)
            async with ctx.typing():
                source = await YTDLSource.from_url(url)
                ctx.voice_client.play(source)
            await ctx.reply('Now playing: {source.title}')
        except:
            await ctx.reply("An error occured.")   
            
    @bot.command()
    async def stop(ctx):
        if ctx.voice_client is None:
            await ctx.reply("I'm not connected to a voice channel.")  
            return
        if not ctx.voice_client.is_playing():
            await ctx.reply("I'm not playing anything.")  
            return
        ctx.voice_client.stop()

    bot.run(TOKEN)
    return

if __name__ == "__main__":
    main()