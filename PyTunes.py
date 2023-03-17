"""
Author: Frederick Rice
Date: Thu Mar 16 2023

"""

import os
import youtube_dl
import discord
from discord.ext import commands
from dotenv import load_dotenv

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
            await ctx.voice_client.disconnect()
        except:
            await ctx.reply("I'm not connected to a voice channel.")
    
    @bot.command()
    async def play(ctx, message):
        try:
            await join(ctx)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('Cancun.mp3'))
            ctx.voice_client.play(source)
            await ctx.reply('Playing.')
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