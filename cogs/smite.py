import os
from datetime import datetime
import discord
import pyrez
from discord.ext import commands
from smite_utilities import SmiteTracker
import pyrez.enumerations
import pyrez.models
import pyrez.api


class CompletePlayer(pyrez.models.Smite.Player, pyrez.models.LiveMatch):
    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.LiveMatch.__init__(self, **kwargs)


class smite(commands.Cog):

    # TODO
    # - edit msgs
    # - emojis
    # - figure out why its 0% W/L
    # - no player found when using trackme
    # - streaming breaks loop

    def __init__(self, bot):
        self.bot = bot
        self.id = int(os.getenv("DEV_ID"))
        self.key = os.getenv("AUTH_KEY")
        self.Smite = SmiteTracker(self.id, self.key)
        self.emojis = {}
        self.tracked_users = {}

    def sortByParty(self, playerList: list[CompletePlayer]):
        return playerList.sort(key=lambda player: player.PartyId)

    def createCompleteStats(self, InGameName) -> list[CompletePlayer]:
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

            compiledMatch.append(CompletePlayer(**combined_data))

        return compiledMatch

    def createEndOfMatchEmbed(self, matchId: int):
        match = self.Smite.getMatchByID(matchId)
        gameType = self.Smite.getMatchType(match[0].matchQueueId)
        embed = discord.Embed(colour=0x00b0f4, timestamp=datetime.now())
        embed.set_author(name=f"{gameType}")

        teamOne, teamTwo = [], []

        for player in match:
            (teamOne, teamTwo)[player.taskForce == 1].append(
                player)  # if taskforce == 1 append teamOne else team 2

        godEmojiTeam1, godEmojiTeam2 = [], []
        for i in range(len(teamOne)):
            for y in range(len(self.emojis)):
                if int(self.emojis[y].name) == int(teamOne[i].liveMatchObject.godId):
                    godEmojiTeam1.append(self.emojis[y])
                    break

            for y in range(len(self.emojis)):
                if int(self.emojis[y].name) == int(teamTwo[i].liveMatchObject.godId):
                    godEmojiTeam2.append(self.emojis[y])
                    break

        for i in range(len(teamOne)):
            embed.add_field(name=f"{godEmojiTeam1[i]} {teamOne[i].liveMatchObject.playerName}", value=f"\n W/L: {teamOne[i].playerStats.winratio}%", inline=True)

            #todo party


    def testCreateLiveMatchEmbed(self, ign):
        pass
    #     todo test CompletePlayer
    def createLiveMatchEmbed(self, ign):

        #
        #         Traceback (most recent call last):
        #   File "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\discord\client.py", line 378, in _run_event
        #     await coro(*args, **kwargs)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\cogs\smite.py", line 293, in on_presence_update
        #     embed = self.tempCreateEmbedEmoji(self.playerName)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\cogs\smite.py", line 163, in tempCreateEmbedEmoji
        #     completeStats = self.createCompleteStats(ign)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\cogs\smite.py", line 108, in createCompleteStats
        #     stats.append(self.Smite.getPlayerStats(str(player.playerName)))
        #   File "C:\ProgrammingRepo\Python\DiscordBot\smite_utilities.py", line 27, in getPlayerStats
        #     return self.smite.getPlayer(inGameName)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\pyrez\api\SmiteAPI.py", line 191, in getPlayer
        #     _ = BaseSmitePaladins.getPlayer(self, player, portalId)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\pyrez\api\API.py", line 558, in getPlayer
        #     _ = self.makeRequest("getplayer", [player, portalId] if portalId else [player])
        #   File "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\pyrez\api\API.py", line 211, in makeRequest
        #     self._checkErrorMsg(hasError.errorMsg)
        #   File "C:\ProgrammingRepo\Python\DiscordBot\venv\lib\site-packages\pyrez\api\API.py", line 147, in _checkErrorMsg
        #     raise PrivatePlayer(errorMsg)
        # pyrez.exceptions.PrivatePlayer.PrivatePlayer: Player Privacy Flag set for: playerIdStr=WinterHuntsman; playerIdType=1; playerId=9745195
        #

        completeStats = self.createCompleteStats(ign)

        gametype = self.smite.getMatchType(completeStats[0].liveMatchObject.Queue)
        #completeStats[0].liveMatchObject.getMapName()
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gametype}")

        teamOne, teamTwo = [], []

        # for player in completeStats:
        #     (teamOne, teamTwo)[player.liveMatchObject.taskForce == 1].append(
        #         player)  # if taskforce == 1 append teamOne else team 2
        #     if player.playerStats is None:
        #         #todo issue with Private Profile
        #         player.liveMatchObject.playerName = "~~Hidden Profile~~"
        #         player.playerStats = pyrez.models.PlayerPS(winratio=0)

        for i in range(len(teamOne)):
            ej1 = self.emojis[str(teamOne[i].liveMatchObject.godName).replace(" ", "")]
            try:
                embed.add_field(name=f"{ej1} {teamOne[i].liveMatchObject.playerName}",
                                value=f"\n W/L: {teamOne[i].playerStats.winratio}%", inline=True)
            except AttributeError:
                embed.add_field(name=f"{ej1} {teamOne[i].liveMatchObject.playerName}", value=f"\n W/L: {0}%",
                                inline=True)

            embed.add_field(
                name=f"{teamOne[i].liveMatchObject.accountLevel:3d} <:level:1093664230928023603> {teamTwo[i].liveMatchObject.accountLevel:3d}",
                value="", inline=True)

            ej2 = self.emojis[str(teamTwo[i].liveMatchObject.godName).replace(" ", "")]
            try:
                embed.add_field(name=f"{ej2} {teamTwo[i].liveMatchObject.playerName}",
                                value=f"\n W/L: {teamTwo[i].playerStats.winratio}%", inline=True)
            except AttributeError:
                embed.add_field(name=f"{ej2} {teamTwo[i].liveMatchObject.playerName}", value=f"\n W/L: {0}%",
                                inline=True)

        embed.set_footer(text=f"{completeStats[0].liveMatchObject.matchId}", icon_url="")

        return embed, completeStats[0].liveMatchObject.matchId

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
        embed = self.createLiveMatchEmbed(ign)
        respondChannel = ctx.channel
        await respondChannel.send(embed=embed[0])

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
        before_smite_status = None
        after_smite_status = None
        msg = None
        acceptable_presences = ["Playing", "Streaming"]

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

            print(f"successfully seen {user_id} change presence from {before_smite_status} to {after_smite_status} in {tracked_guild_id}")
            if msg is None:
                if acceptable_presences in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createLiveMatchEmbed(player_name)
                    msg = await tracked_channel.send(embed=embed[0])

                if acceptable_presences in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createLiveMatchEmbed(player_name)
                    msg = await tracked_channel.send(embed=embed[0])
            else:
                if acceptable_presences in after_smite_status and before_smite_status == "In Queue":
                    embed = self.createLiveMatchEmbed(player_name)
                    msg.edit(await tracked_channel.send(embed=embed[0]))

                if acceptable_presences in after_smite_status and before_smite_status == "In Lobby":
                    embed = self.createLiveMatchEmbed(player_name)
                    msg.edit(await tracked_channel.send(embed=embed[0]))

                if acceptablePresences in beforeSmiteStatus and afterSmiteStatus == "In Lobby":
                    pass
                    # matchId = embed[1]
                    # updatedEmbed = createEndOfMatchEmbed()
                    # msg.edit(embed=updatedEmbed)

    @commands.slash_command(name="trackme", description="Query live match")
    async def trackme(self, ctx, playername):  # this is called when a member joins the server
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        tracked_info = {"guild": guild_id, "channel": ctx.channel, "player": playername}
        self.tracked_users[user_id] = tracked_info
        print("set tracker:", user_id, guild_id)
        await ctx.respond("Started Tracking...")


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(smite(bot))  # add the cog to the bot
