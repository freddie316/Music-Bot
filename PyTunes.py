"""
Author: freddie316
Date: Thu Mar 16 2023
"""

version = "1.5.1"

import os
import sys
import traceback
import asyncio
import yt_dlp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

ytdl_format_options = {
    "format": "m4a/bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "no-playlist": True, 
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
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guild:\n')
    for guild in bot.guilds:
        print(f'{guild.name} (id: {guild.id})\n')
        
@bot.event
async def on_error(event, *args, **kwargs):
    print(event)

@bot.event
async def on_command_error(ctx,error):
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@bot.command()
async def ping(self, ctx):
    """Pong!"""
    await ctx.reply("Pong!") 

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    """Bot owner only, closes the bots connection with discord"""
    print("Beginning shutdown.")
    await ctx.reply("Shutting down.")
    if not ctx.voice_client.is_playing():
        await bot.stop(ctx)
    await bot.close()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeatFlag = False
        self.queue = []
        
    @commands.command()
    async def join(self, ctx):
        """Joins your current voice channel"""
        #print("Join command")
        try:
            channel = ctx.author.voice.channel
            #print("Found author channel")
        except:
            #print("Failed to find author channel")
            await ctx.reply("Are you in voice channel?")
            return
        if ctx.voice_client is not None:
            #print("Moving channels")
            await ctx.voice_client.move_to(channel)
            #print("Restarting AFK timer")
            self.afk_timer.restart()
            return
        #print("Connecting")
        try:
            await channel.connect(timeout=15.0,reconnect=True)
        except Exception as e:
            print(e)
        #print("Initiating AFK timer")
        self.afk_timer.start()

    @commands.command()
    async def leave(self, ctx):
        """Exits the current voice channel"""
        #print("Leave command")
        try:
            if ctx.voice_client.is_playing():
                #print("Stopping audio")
                await self.stop(ctx)
            #print("Disconnecting from voice")
            await ctx.voice_client.disconnect()
        except:
            #print("Not connected")
            await ctx.reply("I'm not connected to a voice channel.")
            return
        #print("Stopping AFK timer")
        self.afk_timer.stop()

    @commands.command()
    async def play(self, ctx, url):
        """Plays the audio from the provided youtube link"""
        #print("Play command")
        try:
            async with ctx.typing():
                #print("Checking voice status")
                if ctx.voice_client is None:
                    await self.join(ctx)
                #print("Checking play status")
                if ctx.voice_client.is_playing():
                    #print("Downloading song")
                    source = ytdl.extract_info(url,download=True)
                    #print("Getting filename")
                    filename = ytdl.prepare_filename(source)
                    #print("Adding to queue")
                    self.queue.append(filename)
                    await ctx.reply(f"Added to queue: {source['title']}")
                    return
                
                #print("Downloading song")
                source = ytdl.extract_info(url,download=True)
                #print("Getting filename")
                filename = ytdl.prepare_filename(source)
                #print("Preparing audio")
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
                #print("Playing song")
                ctx.voice_client.play(song,
                    after = lambda e: self.clean_up(ctx, filename)
                )
            await ctx.reply(f"Now playing: {source['title']}")
        except Exception as e:
            await ctx.reply(f"An error occured: {e}")   

    def clean_up(self, ctx, filename):
        """Function for handling the aftermath of playing a song"""
        #print(self.repeatFlag)
        if self.repeatFlag:
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
            ctx.voice_client.play(song,
                after = lambda e: self.clean_up(ctx,filename)
            )
        elif self.queue:
            os.remove(filename)
            self.afk_timer.restart()
            filename = self.queue.pop(0)
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
            ctx.voice_client.play(song,
                after = lambda e: self.clean_up(ctx,filename)
            )
        else:
            os.remove(filename)
            self.afk_timer.restart()
            
    @commands.command()
    async def repeat(self, ctx):
        """Turns on repeat for the current song"""
        if self.repeatFlag:
            self.repeatFlag = False
        else:
            self.repeatFlag = True
        await ctx.reply(f"Repeat mode: {self.repeatFlag}")
        
    
    @commands.command()
    async def stop(self, ctx):
        """Stops playing the current song"""
        if ctx.voice_client is None:
            await ctx.reply("I'm not connected to a voice channel.")  
            return
        if not ctx.voice_client.is_playing():
            await ctx.reply("I'm not playing anything.")  
            return
        if self.repeatFlag:
            self.repeatFlag = False
            #print(self.repeatFlag)
            ctx.voice_client.stop()
        else:
            ctx.voice_client.stop()
        print(f"Disconnected from {ctx.voice_client.channel}")
        
    @tasks.loop(seconds = 0)
    async def afk_timer(self):
        await asyncio.sleep(300) # 5 minutes
        #print("Timer tick")
        for vc in self.bot.voice_clients:
            if not vc.is_playing():
                await vc.disconnect()
                print(f"Disconnected from {vc.channel}")
                self.afk_timer.stop()
        return

def main():
    bot.add_cog(Music(bot))
    bot.run(TOKEN)
    return

if __name__ == "__main__":
    main()
