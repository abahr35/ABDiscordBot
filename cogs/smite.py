import os
from datetime import datetime
import discord
import pyrez
from discord.ext import commands

import smite_utilities
from smite_utilities import SmiteTracker
import pyrez.enumerations
import pyrez.models
import pyrez.api


class smite(commands.Cog):

    # TODO
    # - redo stats
    # - edit msgs
    # - figure out why its 0% W/L
    # - throw no player found error when using trackme and change tagline
    # - make emoji for parties
    # - implement emojis for items (ugh)

    def __init__(self, bot):
        self.bot = bot
        self.id = int(os.getenv("DEV_ID"))
        self.key = os.getenv("AUTH_KEY")
        self.Smite = SmiteTracker(self.id, self.key)
        self.emojis = {}
        self.tracked_users = {}

    def sortByParty(self, playerList: list[smite_utilities.CompletePlayer]):
        return playerList.sort(key=lambda player: player.PartyId)

    def compileTeamCompleteStats(self, InGameName) -> list[smite_utilities.CompletePlayer]:
        compiledMatch = []
        match = self.getRecentMatch(InGameName)
        for player in match:
            match_dict = player.__kwargs__
            try:
                player_dict = self.smite.getPlayer(player.playerId).__kwargs__
            except pyrez.exceptions.PlayerNotFound:
                player_dict = pyrez.models.Smite.Player

            combined_data = {}
            combined_data.update(match_dict)
            combined_data.update(player_dict)

            compiledMatch.append(smite_utilities.CompletePlayer(**combined_data))

        return compiledMatch

    def createEndOfMatchEmbed(self, ign: str):
        match = self.Smite.createCompleteStats(ign)
        print(match[0])
        sortedMatch = match
        gameType = self.Smite.getMatchType(sortedMatch[0].CompletePlayerList[0].match_queue_id)
        gameLength = sortedMatch[0].CompletePlayerList[0].Time_In_Match_Seconds / 60

        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gameType} | {int(gameLength)} Minutes")

        # set god emojis
        for player in sortedMatch[0].CompletePlayerList:
            player.emoji = self.emojis[str(player.godName).replace(" ", "")]

        for player in sortedMatch[1].CompletePlayerList:
            player.emoji = self.emojis[str(player.godName).replace(" ", "")]

        t1, t2 = sortedMatch[0], sortedMatch[1]

        # create first line
        if t1.Win_Status == "Winner":
            embed.add_field(name=f":trophy:{t1.Win_Status}:trophy:",
                            value=f"\n:crossed_swords:KDA:{t1.kda}\n:dagger:Damage:{t1.totalDamage}", inline=True)
        else:
            embed.add_field(name=f":red_circle:{t1.Win_Status}:red_circle:",
                            value=f"\n:crossed_swords:KDA:{t1.kda}\n:dagger:Damage:{t1.totalDamage}", inline=True)
        embed.add_field(name=f"", value=f"\n ", inline=True)
        if t2.Win_Status == "Winner":
            embed.add_field(name=f":trophy:{t2.Win_Status}:trophy:",
                        value=f"\n:crossed_swords:KDA:{t2.kda}\n:dagger:Damage:{t2.totalDamage}", inline=True)
        else:
            embed.add_field(name=f":red_circle:{t2.Win_Status}:red_circle:",
                            value=f"\n:crossed_swords:KDA:{t2.kda}\n:dagger:Damage:{t2.totalDamage}", inline=True)

        for i in range(len(t1.CompletePlayerList)):
            embed.add_field(name=f"{t1.CompletePlayerList[i].getEmoji()} {t1.CompletePlayerList[i].playerName}",
                            value=f"\n--items_placeholder--\n:crossed_swords:KDA:{t1.CompletePlayerList[i].matchKDA}\n:dagger:Damage:{t1.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t1.CompletePlayerList[i].Gold_Earned}",
                            inline=True)
            embed.add_field(name=f"{t1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {t2.CompletePlayerList[i].accountLevel:3d}",
                            value=f"\n{t1.CompletePlayerList[i].partyNumber} :black_large_square: {t2.CompletePlayerList[i].partyNumber}", inline=True)
            embed.add_field(name=f"{t2.CompletePlayerList[i].getEmoji()} {t2.CompletePlayerList[i].playerName}",
                            value=f"\n--items_placeholder--\n:crossed_swords:KDA:{t2.CompletePlayerList[i].matchKDA}\n:dagger:Damage:{t2.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t2.CompletePlayerList[i].Gold_Earned}",
                            inline=True)

        embed.set_footer(text=f"{t1.Match_Id}", icon_url="")

        return embed

    def createLiveMatchEmbed(self, ign):
        match = self.Smite.createCompleteStats(ign)
        sortedMatch = match
        gameType = self.Smite.getMatchType(sortedMatch[0].CompletePlayerList[0].match_queue_id)

        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gameType} | Live Match")

        # set god emojis
        for player in sortedMatch[0].CompletePlayerList:
            player.emoji = self.emojis[str(player.godName).replace(" ", "")]

        for player in sortedMatch[1].CompletePlayerList:
            player.emoji = self.emojis[str(player.godName).replace(" ", "")]

        t1, t2 = sortedMatch[0], sortedMatch[1]

        for i in range(len(t1.CompletePlayerList)):
            embed.add_field(name=f"{t1.CompletePlayerList[i].getEmoji()} {t1.CompletePlayerList[i].playerName}",
                            value=f"\n{t1.CompletePlayerList[i].matchKDA()}\n:crossed_swords:KDA:{t1.CompletePlayerList[i].matchKDA}\n:dagger:Damage:{t1.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t1.CompletePlayerList[i].Gold_Earned}",
                            inline=True)
            embed.add_field(name=f"{t1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {t2.CompletePlayerList[i].accountLevel:3d}",
                            value=f"\n{t1.CompletePlayerList[i].partyNumber} :black_large_square: {t2.CompletePlayerList[i].partyNumber}", inline=True)
            embed.add_field(name=f"{t2.CompletePlayerList[i].getEmoji()} {t2.CompletePlayerList[i].playerName}",
                            value=f"\n--items_placeholder--\n:crossed_swords:KDA:{t2.CompletePlayerList[i].matchKDA()}\n:dagger:Damage:{t2.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t2.CompletePlayerList[i].Gold_Earned}",
                            inline=True)

        embed.set_footer(text=f"{t1.Match_Id}", icon_url="")

        return embed


    @commands.Cog.listener()
    async def on_ready(self):
        guilds = [await self.bot.fetch_guild(959898607841075210), await self.bot.fetch_guild(821514908327608330),
                  await self.bot.fetch_guild(1093656432278245558)]
        for guild in guilds:
            for emoji in guild.emojis:
                self.emojis[str(emoji.name)] = emoji
        print("Emojis Loaded")
        print("Smite Cog Ready")

    @discord.slash_command(name="livematchtest", description="Query stats for a test match")
    async def livematchtest(self, ctx, ign):
        embed = self.createEndOfMatchEmbed(ign)
        tracked_channel = ctx.channel
        msg = await ctx.respond("Match:")
        await tracked_channel.send(embed=embed)

    @discord.slash_command(name="stats", description="Query stats for a specific player")
    async def stats(self, ctx, ign):
        try:
            statQuery = self.Smite.getPlayerStats(ign)
            embed = discord.Embed(
                title=f"Query for {statQuery.hzPlayerName}",
                color=discord.Colour.dark_orange()
            )

            embed.add_field(name=f"Account Level: {statQuery.accountLevel}", value="", inline=False)
            embed.add_field(name=f"Last Seen: {statQuery.last_login} ago", value="", inline=False)
            embed.add_field(name=f"W/L: {statQuery.winratio}", value="", inline=False)
            embed.add_field(name=f"Leaves: {statQuery.leaves}", value="", inline=False)
            embed.add_field(name=f"Conquest-MMR: {statQuery.rankedConquest.rankStat}", value="", inline=False)
            embed.add_field(name=f"Joust-MMR: {statQuery.rankedJoust.rankStat}", value="", inline=False)
            embed.add_field(name=f"Duel-MMR: {statQuery.rankedDuel.rankStat}", value="", inline=False)

            embed.set_footer(text=f"Generated by {ctx.author}!")  # footers can have icons too
            embed.set_author(name=f"{self.bot.user}")
            embed.set_thumbnail(url=f"{statQuery.avatarURL}")

            await ctx.respond(embed=embed)
        except Exception as playerPrivate:
            embed = discord.Embed(
                title=f"Error: {ign} is private",
                color=discord.Colour.dark_red()
            )
            embed.add_field(name="Private Profile", value="\'What a Baby\'", inline=False)
            await ctx.respond(embed=embed)

    # noinspection PyUnresolvedReferences
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):  # for live tracking of smite game
        before_smite_status = None
        after_smite_status = None
        msg = None
        acceptable_prefixes = ["Playing", "Streaming"]

        for activity in before.activities:
            if activity.name == "SMITE":
                before_smite_status = activity.state

        for activity in after.activities:
            if activity.name == "SMITE":
                after_smite_status = activity.state

        user_id = str(before.id)
        if user_id in self.tracked_users:
            tracked_info = self.tracked_users[user_id]
            tracked_guild_id = tracked_info["guild"]
            tracked_channel = tracked_info["channel"]
            player_name = tracked_info["player"]

            print(
                f"successfully seen {user_id} change presence from {before_smite_status} to {after_smite_status} in {tracked_guild_id}")
            if msg is None:
                # todo play test
                if acceptable_prefixes[0] in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createLiveMatchEmbed(player_name)  # "In Queue -> Playing Smite"
                    msg = await tracked_channel.send(embed=embed)

                if acceptable_prefixes[1] in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createLiveMatchEmbed(player_name)  # "In Queue -> Streaming Smite"
                    msg = await tracked_channel.send(embed=embed)

                if acceptable_prefixes[0] in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createLiveMatchEmbed(player_name)  # "In Lobby -> Playing Smite"
                    msg = await tracked_channel.send(embed=embed)

                if acceptable_prefixes[1] in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createLiveMatchEmbed(player_name)  # "In Lobby -> Streaming Smite"
                    msg = await tracked_channel.send(embed=embed)

            else:

                if acceptable_prefixes[0] in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createEndOfMatchEmbed(player_name)  # "In Queue -> Playing Smite"
                    await msg.edit(embed=embed)
                    msg = None

                if acceptable_prefixes[1] in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createEndOfMatchEmbed(player_name)  # "In Queue -> Streaming Smite"
                    await msg.edit(embed=embed)
                    msg = None

                if acceptable_prefixes[0] in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createEndOfMatchEmbed(player_name)  # "In Lobby -> Playing Smite"
                    await msg.edit(embed=embed)
                    msg = None
                if acceptable_prefixes[1] in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createEndOfMatchEmbed(player_name)  # "In Lobby -> Streaming Smite"
                    await msg.edit(embed=embed)
                    msg = None
    @commands.slash_command(name="trackme", description="Query live match")
    async def trackme(self, ctx, playername):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        tracked_info = {"guild": guild_id, "channel": ctx.channel, "player": playername}
        self.tracked_users[user_id] = tracked_info
        print("set tracker:", user_id, guild_id)
        await ctx.respond("Started Tracking...")


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(smite(bot))  # add the cog to the bot
