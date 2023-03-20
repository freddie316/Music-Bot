"""
Author: freddie316
Date: Thu Mar 16 2023
Version: 1.4.2
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
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guild:\n')
    for guild in bot.guilds:
        print(f'{guild.name} (id: {guild.id})\n')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repeatFlag = False
        self.queue = []
        self.ctx = None
        self.filename = None
        
    @commands.command()
    async def join(self, ctx):
        self.ctx = ctx
        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.reply("Are you in voice channel?")
            return
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        self.afk_timer.start()

    @commands.command()
    async def leave(self, ctx):
        self.ctx = ctx
        try:
            if ctx.voice_client.is_playing():
                await self.stop(ctx)
            await ctx.voice_client.disconnect()
        except:
            await ctx.reply("I'm not connected to a voice channel.")
            return
        self.afk_timer.stop()

    @commands.command()
    async def play(self, ctx, url):
        self.ctx = ctx
        try:
            async with ctx.typing():
                if ctx.voice_client is None:
                    await self.join(ctx)
                if ctx.voice_client.is_playing():
                    source = ytdl.extract_info(url,download=True)
                    filename = ytdl.prepare_filename(source)
                    self.queue.append(filename)
                    await ctx.reply(f"Added to queue: {source['title']}")
                    return
                
                source = ytdl.extract_info(url,download=True)
                self.filename = ytdl.prepare_filename(source)
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.filename, **ffmpeg_options))
                ctx.voice_client.play(song,
                    after = lambda e: self.cleanup()
                )
                await ctx.reply(f"Now playing: {source['title']}")
        except Exception as e:
            await ctx.reply(f"An error occured: {e}")   

    def cleanup(self):
        print(self.repeatFlag)
        if self.repeatFlag:
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.filename, **ffmpeg_options))
            self.ctx.voice_client.play(song,
                after = lambda e: self.cleanup()
            )
        elif self.queue:
            os.remove(self.filename)
            self.afk_timer.restart()
            self.filename = self.queue.pop(0)
            song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.filename, **ffmpeg_options))
            self.ctx.voice_client.play(song,
                after = lambda e: self.cleanup()
            )
        else:
            os.remove(self.filename)
            self.afk_timer.restart()
            
    @commands.command()
    async def repeat(self,ctx):
        self.ctx = ctx
        if self.repeatFlag:
            self.repeatFlag = False
        else:
            self.repeatFlag = True
        await ctx.reply(f"Repeat mode: {self.repeatFlag}")
        
    
    @commands.command()
    async def stop(self, ctx):
        self.ctx = ctx
        if ctx.voice_client is None:
            await ctx.reply("I'm not connected to a voice channel.")  
            return
        if not ctx.voice_client.is_playing():
            await ctx.reply("I'm not playing anything.")  
            return
        if self.repeatFlag:
            self.repeatFlag = False
            print(self.repeatFlag)
            ctx.voice_client.stop()
            self.repeatFlag = True
        else:
            ctx.voice_client.stop()
        
    @commands.command()
    async def ping(self, ctx):
        self.ctx = ctx
        await ctx.reply("Pong!") 
        
    @tasks.loop(seconds = 0)
    async def afk_timer(self):
        await asyncio.sleep(300) # 5 minutes
        if not bot.voice_clients[0].is_playing():
            await bot.voice_clients[0].disconnect()
            self.afk_timer.stop()
        return

def main():
    bot.add_cog(Music(bot))
    bot.run(TOKEN)
    return

if __name__ == "__main__":
    main()
