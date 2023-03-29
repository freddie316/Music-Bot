"""
Author: freddie316
Date: Thu Mar 16 2023
"""

version = "1.7.1"

# Module Imports
import os
import sys
import traceback
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cog Imports
import Music
import Fun

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
    """Bot owner only, closes the bot's connection with discord"""
    print("Beginning shutdown.")
    await ctx.reply("Shutting down.")
    try:
        if ctx.voice_client.is_playing():
            await bot.stop(ctx)
    finally:
        for vc in bot.voice_clients:
            await vc.disconnect()
            print(f"Disconnected from {vc.channel}")
        await bot.close()

def main():
    bot.add_cog(Music.Music(bot))
    bot.add_cog(Fun.Fun(bot))
    bot.run(TOKEN)
    return

if __name__ == "__main__":
    main()
