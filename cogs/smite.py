import os
import time
from datetime import datetime
import discord
import logging
from helpers import embedHelper, smiteHelper, smiteEnums, emojiVerifier
from discord.ext import commands
from smite_utilities import SmiteTracker


class smite(commands.Cog):

    # TODO
    # - redo stats
    # - throw no player found error when using trackme and change tagline

    def __init__(self, bot):

        self.bot = bot
        self.id = int(os.getenv("DEV_ID"))
        self.key = os.getenv("AUTH_KEY")
        self.Smite = SmiteTracker(self.id, self.key)
        self.emojis = {}
        self.tracked_users = {}
        # emojiVerifier.VerifyGods(self.Smite, self.emojis)
        # emojiVerifier.VerifyItems()

    def createEndOfMatchEmbed(self, ign: str):
        """
        takes the player name provided and looks up their stats and most recent match
        to show them on an embed.

        does this multiple times to show up to 10 people per game

        :param ign: PlayerName
        :return: Embed
        """

        sortedTeams = self.Smite.createCompleteMatchStats(ign)  # returns tuple of teams
        smiteHelper.calculateParties(sortedTeams)  # calculate Party Numbers
        smiteHelper.batchSetEmoji(sortedTeams)  # Set emojis for items and gods for both teams
        embed = embedHelper.CreateSettings(sortedTeams)  # Start the creation of an Embed

        # Make Variable Easier to Read
        team1, team2 = sortedTeams[0], sortedTeams[1]

        # Make the calling User on the Left
        for player in team2.CompletePlayerList:
            if player.playerName.lower() == ign.lower():  # if name = provided name
                team1, team2 = team2, team1  # ensure its on the left side

        embed = embedHelper.CreateHeader(embed, team1, team2)
        embed = embedHelper.CreateBody(embed, team1, team2)

        # Set bottom of Embed to useful info
        embed.set_footer(text=f"{team1.Match_Id}", icon_url="")

        return embed

    def createLiveMatchEmbed(self, ign: str):
        """
        takes the player name provided and looks up their stats and current match
        to show them on an embed.

        does this multiple times to show up to 10 people per game

        :param ign: PlayerName
        :return: Embed
        """
        sortedTeams = self.Smite.createCompleteStatsLive(ign)
        smiteHelper.calculateParties(sortedTeams)  # calculate Party Numbers
        smiteHelper.batchSetEmoji(sortedTeams)  # Set emojis for items and gods for both teams
        embed = embedHelper.CreateSettings(sortedTeams, isLive=True)  # Start the creation of an Embed

        # Make Variable Easier to Read
        team1, team2 = sortedTeams[0], sortedTeams[1]
        # Make the calling User on the Left
        for player in team2.CompletePlayerList:
            if player.playerName.lower() == ign.lower():  # if name = provided name
                team1, team2 = team2, team1  # ensure its on the left side

        embed = embedHelper.CreateHeader(embed, team1, team2, isLive=True)
        embed = embedHelper.CreateBody(embed, team1, team2, isLive=True)
        # Set bottom of Embed to useful info
        embed.set_footer(text=f"{team1.Match_Id}", icon_url="")
        return embed

    @commands.Cog.listener()
    async def on_ready(self):
        print("Emojis Loading...")
        guilds = [await self.bot.fetch_guild(959898607841075210),
                  await self.bot.fetch_guild(821514908327608330),
                  await self.bot.fetch_guild(1093656432278245558),
                  await self.bot.fetch_guild(1130872173058334800),
                  await self.bot.fetch_guild(1130888627807862899),
                  await self.bot.fetch_guild(1130890719821824132),
                  await self.bot.fetch_guild(1130891492748165261),
                  await self.bot.fetch_guild(1130924062097547424),
                  await self.bot.fetch_guild(1130944721250943059),
                  await self.bot.fetch_guild(1130996774484586587),
                  await self.bot.fetch_guild(1131252199645794365)]
        for guild in guilds:
            for emoji in guild.emojis:
                self.emojis[str(emoji.name)] = emoji
        print("Emojis Loaded")
        print("Smite Cog Ready")

    @discord.slash_command(name="livematchtest", description="Query stats for a test match")
    async def livematchtest(self, ctx, ign):
        await ctx.defer()
        embed = self.createLiveMatchEmbed(ign)
        await ctx.followup.send(embed=embed)

    @discord.slash_command(name="endmatchtest", description="Query stats for a test match")
    async def endmatchtest(self, ctx, ign):
        await ctx.defer()
        embed = self.createEndOfMatchEmbed(ign)
        await ctx.followup.send(embed=embed)

    @discord.slash_command(name="stats", description="Query stats for a specific player")
    async def stats(self, ctx, ign):

        player = self.Smite.getPlayerStats(ign)
        embed = discord.Embed(
            title=f"Query for {player.hzPlayerName}",
            color=discord.Colour.blurple()
        )
        embed.add_field(name=f":computer:Last Seen:", value="", inline=True)
        embed.add_field(name=f"<t:{int(time.mktime(player.lastLoginDatetime.timetuple()))}:R>", value=f"", inline=True)
        embed.add_field(name=f"", value=f"", inline=True)

        embed.add_field(name=f"<:level:1093664230928023603>Level", value=f":small_orange_diamond:{player.accountLevel}",
                        inline=True)
        embed.add_field(name=f"<:mastery:1131690327728721951>Mastery Level",
                        value=f":small_orange_diamond:{player.MasteryLevel}", inline=True)
        embed.add_field(name=f"<:wp:1131691182448197744>Total Worshipers",
                        value=f":small_orange_diamond:{player.totalXP}", inline=True)

        embed.add_field(name=f":trophy:Wins[{player.winratio}]", value=f":small_orange_diamond:{player.wins}",
                        inline=True)
        embed.add_field(name=f":flag_white:Losses", value=f":small_orange_diamond:{player.losses}", inline=True)
        embed.add_field(name=f":runner:Leaves", value=f":small_orange_diamond:{player.leaves}", inline=True)

        embed.set_footer(text=f"Generated by {ctx.author}!")  # footers can have icons too
        embed.set_author(name=f"{self.bot.user}")
        embed.set_thumbnail(url=f"{player.avatarURL}")
        await ctx.respond(embed=embed)

    # noinspection PyUnresolvedReferences
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):  # for live tracking of smite game
        before_smite_status = None
        after_smite_status = None

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
            tracked_presence = tracked_info["old_presence"]

            print(f"{datetime.now()} {(before_smite_status, after_smite_status)} and {tracked_presence}")
            if (
                    before_smite_status,
                    after_smite_status) != tracked_presence:  # Check if the status has actually changed
                print(
                    f"successfully seen {before.name}:{user_id} change presence from {before_smite_status} to {after_smite_status} in {tracked_guild_id}")
                self.tracked_users[user_id]["old_presence"] = (before_smite_status, after_smite_status)
                if self.tracked_users[user_id]["msg"] is None:
                    if "Playing" in after_smite_status and before_smite_status in ["In Queue", "In Lobby"]:
                        embed = self.createLiveMatchEmbed(player_name)
                        self.tracked_users[user_id]["msg"] = await tracked_channel.send(embed=embed)

                    if "Streaming" in after_smite_status and before_smite_status in ["In Queue", "In Lobby"]:
                        embed = self.createLiveMatchEmbed(player_name)
                        self.tracked_users[user_id]["msg"] = await tracked_channel.send(embed=embed)

                else:
                    if "Playing" in before_smite_status and after_smite_status == "In Lobby":
                        embed = self.createEndOfMatchEmbed(player_name)
                        await self.tracked_users[user_id]["msg"].edit(embed=embed)
                        self.tracked_users[user_id]["msg"] = None

                    if "Streaming" in before_smite_status and after_smite_status == "In Lobby":
                        embed = self.createEndOfMatchEmbed(player_name)
                        await self.tracked_users[user_id]["msg"].edit(embed=embed)
                        self.tracked_users[user_id]["msg"] = None
            else:
                pass

    @commands.slash_command(name="trackme", description="Query live match")
    async def trackme(self, ctx, playername):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        tracked_info = {"guild": guild_id, "channel": ctx.channel, "player": playername, "old_presence": None,
                        "msg": None}
        self.tracked_users[user_id] = tracked_info
        print("set tracker:", user_id, guild_id)
        await ctx.respond("Started Tracking...")


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(smite(bot))  # add the cog to the bot
