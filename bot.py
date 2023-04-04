import asyncio
import traceback

import discord, dotenv, os
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from typing import Optional, Literal

dotenv.load_dotenv()
token = str(os.getenv("DISCORD_TOKEN"))
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents, debug_guilds=[821514908327608330, 473249208699322389])


# load cogs
def load_cogs():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            #logging.info(f"Successfully loaded {filename}")

@bot.command(name="reload_cogs", description="reload cogs")
@commands.is_owner()
async def reload_cogs(ctx, cog=None):
    if not cog:
        # No cog, means we reload all cogs
        async with ctx.typing():
            embed = discord.Embed(
                title="Reloading all cogs!",
                color=0x808080,
            )
            for ext in os.listdir("./cogs/"):
                if ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        bot.unload_extension(f"cogs.{ext[:-3]}")
                        bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception as e:
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=str(e),
                            inline=False
                        )
                    await asyncio.sleep(0.5)
            await ctx.send(embed=embed)
    else:
        # reload the specific cog
        async with ctx.typing():
            embed = discord.Embed(
                title="Reloading all cogs!",
                color=0x808080,
            )
            ext = f"{cog.lower()}.py"
            if not os.path.exists(f"./cogs/{ext}"):
                # if the file does not exist
                embed.add_field(
                    name=f"Failed to reload: `{ext}`",
                    value="This cog does not exist.",
                    inline=False
                )

            elif ext.endswith(".py") and not ext.startswith("_"):
                try:
                    bot.unload_extension(f"cogs.{ext[:-3]}")
                    bot.load_extension(f"cogs.{ext[:-3]}")
                    embed.add_field(
                        name=f"Reloaded: `{ext}`",
                        value='\uFEFF',
                        inline=False
                    )
                except Exception:
                    desired_trace = traceback.format_exc()
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value=desired_trace,
                        inline=False
                    )
            await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

load_cogs()
bot.run(token)
