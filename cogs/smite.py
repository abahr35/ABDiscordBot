import os
from datetime import datetime

import discord
import pyrez
from discord.ext import commands
from smite_utilities import SmiteTracker

class smite(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.id = int(os.getenv("DEV_ID"))
        self.key = os.getenv("AUTH_KEY")
        self.Smite = SmiteTracker(self.id, self.key)
        self.trackedName = None
        self.trackedGuild = None
        self.respondChannel = None
        self.playerName = None

    def createdMatchEmbed(self, ign):
        # create exception catch for no live match
        players = self.Smite.getLiveMatch(ign)

        embed = discord.Embed(
            title=f"Query for Live Match:{players[0].matchId}",
            color=discord.Colour.dark_orange()
        )

        team1 = []
        team2 = []

        for i in range(len(players)):
            if players[i].taskForce == 1:
                if players[i].playerName == "":
                    players[i].playerName = "not found"
                    team1.append(players[i])
                else:
                    team1.append(players[i])

            elif players[i].taskForce == 2:
                if players[i].playerName == "":
                    players[i].playerName = "not found"
                    team2.append(players[i])
                else:
                    team2.append(players[i])
            else:
                print("not added")

        if len(team1) == len(team2):

            for i in range(len(team1)):
                embed.add_field(name=f"Name: {team1[i].playerName}", value=f"", inline=True)
                embed.add_field(name=f"God: {team1[i].godName}", value=f"", inline=True)
                embed.add_field(name=f"Account Level: {team1[i].accountLevel}", value=f"", inline=True)

            for i in range(len(team2)):
                embed.add_field(name=f"Name: {team2[i].playerName}", value="", inline=True)
                embed.add_field(name=f"God: {team2[i].godName}", value="", inline=True)
                embed.add_field(name=f"Account Level: {team2[i].accountLevel}", value="", inline=True)

        #             Ignoring
        #             exception in on_presence_update
        #             Traceback(most
        #             recent
        #             call
        #             last):
        #             File
        #             "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\discord\client.py", line
        #             378, in _run_event
        #             await coro(*args, **kwargs)
        #         File
        #         "C:\ProgrammingRepo\Python\DiscordBot\cogs\smite.py", line
        #         129, in on_presence_update
        #         if "Playing" in afterSmiteStatus and beforeSmiteStatus == "In Queue":
        #
        # TypeError: argument
        # of
        # type
        # 'NoneType' is not iterable

        return embed

    def tempCreateEmbed(self, ign):
        players = self.Smite.getLiveMatch(ign)

        gametype = players[0].getMapName()
        embed = discord.Embed(colour=0x00b0f4, timestamp=datetime.now())
        embed.set_author(name=f"{gametype}")

        t1Ratio = ''
        t2Ratio = ''

        team1 = []
        team2 = []

        for i in range(len(players)):
            if players[i].taskForce == 1:
                if players[i].playerName == "":
                    players[i].playerName = "~~Hidden Profile~~"
                    team1.append(players[i])
                else:
                    team1.append(players[i])

            elif players[i].taskForce == 2:
                if players[i].playerName == "":
                    players[i].playerName = "~~Hidden Profile~~"
                    team2.append(players[i])
                else:
                    team2.append(players[i])
            else:
                print("not added")

        if len(team1) == len(team2):
            for i in range(len(team1)):

                embed.add_field(name=f"{team1[i].playerName}", value=f"\n{t1Ratio}", inline=True)
                embed.add_field(name=f"{team1[i].accountLevel:3d} || {team2[i].accountLevel:3d}", value="", inline=True)
                embed.add_field(name=f"{team2[i].playerName}",value=f"\n{t2Ratio}", inline=True)

            embed.set_footer(text=f"{players[0].matchId}", icon_url="")

            return embed

    @commands.Cog.listener()
    async def on_ready(self):
        print("smite cog ready")

    @discord.slash_command(name="matchtest", description="Query stats for a test match")
    async def matchtest(self, ctx, ign):
        """
        {
          "Account_Gods_Played": 27,
          "Account_Level": 68,
          "GodId": 2051,
          "GodLevel": 2,
          "GodName": "Medusa",
          "Mastery_Level": 2,
          "Match": 1299615775,
          "Queue": "435",
          "Rank_Stat": 0,
          "SkinId": 17620,
          "Tier": 0,
          "mapGame": "Arena_V3",
          "playerCreated": "9/15/2020 9:12:58 PM",
          "playerId": "712749710",
          "playerName": "BushSlayer1172",
          "playerRegion": "North America",
          "ret_msg": null,
          "taskForce": 1,
          "tierLosses": 0,
          "tierPoints": 0,
          "tierWins": 0
        }
        """
        embed = self.tempCreateEmbed(ign)
        await ctx.respond(embed=embed)

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

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):  # for live tracking of smite game
        beforeSmiteStatus = None
        afterSmiteStatus = None
        for activity in before.activities:
            if activity.name == "SMITE":
                beforeSmiteStatus = activity.state

        for activity in after.activities:
            if activity.name == "SMITE":
                afterSmiteStatus = activity.state

        # https://github.com/iforvard/SmiteLiveMatchCheck/blob/master/SLMChek.py
        if before.id == self.trackedName and before.guild.id == self.trackedGuild:
            print(
                f"successfully seen {before.id} change presence from {beforeSmiteStatus} to {afterSmiteStatus} in {before.guild.id}")
            if "Playing" in afterSmiteStatus and beforeSmiteStatus == "In Queue":
                embed = self.tempCreateEmbed(self.playerName)
                await self.respondChannel.send(embed=embed)

            if "Playing" in afterSmiteStatus and beforeSmiteStatus == "In Lobby":
                embed = self.tempCreateEmbed(self.playerName)
                await self.respondChannel.send(embed=embed)

    @commands.slash_command(name="trackme", description="Query live match")
    async def trackme(self, ctx, playername):  # this is called when a member joins the server
        self.trackedName = ctx.author.id
        self.trackedGuild = ctx.guild.id
        self.respondChannel = ctx.channel
        self.playerName = playername
        print("set tracker:", self.trackedName, self.trackedGuild)
        await ctx.respond("Started Tracking...")


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(smite(bot))  # add the cog to the bot
