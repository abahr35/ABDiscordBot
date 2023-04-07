import asyncio

import discord
from discord.ext import commands, tasks
import json

class Greetings(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot
        self.member_updated = 0
        self.emojis = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("greetings cog ready")


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(Greetings(bot))  # add the cog to the bot


