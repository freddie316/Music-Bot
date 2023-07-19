"""
Author: freddie316
Date: Sun Mar 26 2023
"""

import os
import validators
import asyncio
import yt_dlp
import discord
from discord.ext import commands, tasks

ytdl_format_options = {
    "format": "m4a/bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "noplaylist": True,
    "default_search": "ytsearch3", 
    "postprocessors": [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a'
    }],
}

ffmpeg_options = {"options": "-vn"}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.repeatFlag = False
        self.queue = []
        
    @commands.command()
    async def join(self, ctx):
        """Joins your current voice channel"""
        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.reply("Are you in voice channel?")
            return
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
            self.afk_timer.restart()
            return
        try:
            await channel.connect(timeout=15.0,reconnect=True)
            print(f"Connected to {channel}")

        except Exception as e:
            print("Failed to connect.")
            print(e)
        else:
            self.afk_timer.start() 

    @commands.command()
    async def leave(self, ctx):
        """Exits the current voice channel"""
        try:
            if ctx.voice_client.is_playing():
                await self.stop(ctx)
            print(f"Disconnected from {ctx.voice_client.channel}")
            await ctx.voice_client.disconnect()
        except:
            await ctx.reply("I'm not connected to a voice channel.")
            return
        self.afk_timer.stop()

    @commands.command()
    async def play(self, ctx, query):
        """Plays the audio from the provided youtube link or searches youtube for the provided song title"""
        try:
            async with ctx.typing():
                if ctx.voice_client is None:
                    await self.join(ctx)
                if validators.url(query): # true if input is an actual url
                    await self.prepare_song(ctx,query)
                else:
                    # Begin search for video
                    source = ytdl.extract_info(query,download=False)
                    guesses = []
                    for entry in source['entries']:
                        guesses.append(entry['title'])
                    msg = await ctx.reply(
                        f'''I've found three songs that match your search. Please pick one:\n
                        1. {guesses[0]}\n
                        2. {guesses[1]}\n
                        3. {guesses[2]}\n'''
                    )
                    reactions = ['1️⃣','2️⃣','3️⃣','❌']
                    for emoji in reactions:
                        await msg.add_reaction(emoji)
                    def check(react,user):
                        return react.emoji in reactions and user == ctx.author
                    response = await self.bot.wait_for(
                        "reaction_add",
                        check=check
                    )
                    reaction = response[0].emoji
                    if reaction == '❌':
                        await ctx.reply(f"Canceling.")
                        return
                    choice = source['entries'][reactions.index(reaction)]['webpage_url']
                    await self.prepare_song(ctx,choice)
        except Exception as e:
            await ctx.reply(f"An error occured: {e}")   

    async def prepare_song(self,ctx,query):
        if ctx.voice_client.is_playing():
            source = ytdl.extract_info(query,download=True)
            filename = ytdl.prepare_filename(source)
            self.queue.append(filename)
            await ctx.reply(f"Added to queue: {source['title']}")
            return
        source = ytdl.extract_info(query,download=True)
        filename = ytdl.prepare_filename(source)
        song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
        ctx.voice_client.play(song,
            after = lambda e: self.clean_up(ctx, filename)
        )
        await ctx.reply(f"Now playing: {source['title']}")

    def clean_up(self, ctx, filename):
        """Function for handling the aftermath of playing a song"""
        if self.repeatFlag:
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, **ffmpeg_options))
            ctx.voice_client.play(song,
                after = lambda e: self.clean_up(ctx,filename)
            )
        elif self.queue:
            os.remove(filename)
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
        """Turns on/off repeat for the current song"""
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
            ctx.voice_client.stop()
        else:
            ctx.voice_client.stop()
        
    @tasks.loop(seconds = 0)
    async def afk_timer(self):
        await asyncio.sleep(300) # 5 minutes
        for vc in self.bot.voice_clients:
            if not vc.is_playing():
                print(f"Disconnected from {vc.channel}")
                await vc.disconnect()
                self.afk_timer.stop()
        return

def main():

    return

if __name__ == "__main__":
    main()