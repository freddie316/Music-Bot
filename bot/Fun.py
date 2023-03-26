"""
Author: freddie316
Date: Sun Mar 26 2023
"""

import os
import discord
from discord.ext import commands
from pathlib import Path

class Fun(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.picPath = Path('.').resolve().parent / 'Pictures'
    @commands.command()
    async def cringe(self,ctx):
        """Cringes"""
        with open(self.picPath / 'cringe.png', 'rb') as f:
            picture = discord.File(f)
            await ctx.reply(file=picture)

def main():

    return

if __name__ == "__main__":
    main()