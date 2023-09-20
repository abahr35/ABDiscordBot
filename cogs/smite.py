import os
import time
from datetime import datetime
import discord
import pyrez
from discord.ext import commands
from smite_utilities import SmiteTracker
from enum import Enum

# def getQueueTypeByMapName(mapName):
#     queue_map = {
#         Conquest_5v5 = 423,
#         Novice_Queue = 424,
#         Conquest = 426,
#         Practice = 427,
#         Custom_Conquest = 429,  # Conquest_Challenge=429#Conquest_Ranked=430
#         Domination = 433,
#         MOTD = 434,
#         Arena_Queue = 435,
#         Basic_Tutorial = 436,
#         Custom_Arena = 438,
#         # Arena_Challenge = 438,
#         Domination_Challenge = 439,
#         Joust_1v1_Ranked_Keyboard = 440,
#         Custom_Joust = 441,
#         # Joust_Challenge = 441
#         Arena_Practice_Easy = 443,
#         Jungle_Practice = 444,
#         Assault = 445,
#         Custom_Assault = 446,
#         # Assault_Challenge = 446,
#         Joust_Queue_3v3 = 448,
#         Joust_3v3_Ranked_Keyboard = 450,
#         Conquest_Ranked_Keyboard = 451,  # ConquestLeague
#         Arena_League = 452,
#         Assault_vs_AI_Medium = 454,
#         Joust_vs_AI_Medium = 456,
#         Arena_vs_AI_Easy = 457,
#         Conquest_Practice_Easy = 458,
#         Siege_4v4 = 459,
#         Custom_Siege = 460,
#         # Siege_Challenge = 460,
#         Conquest_vs_AI_Medium = 461,
#         Arena_Tutorial = 462,
#         Conquest_Tutorial = 463,
#         Joust_Practice_Easy = 464,
#         Clash = 466,
#         Custom_Clash = 467,
#         # Clash_Challenge = 467,
#         Arena_vs_AI_Medium = 468,
#         Clash_vs_AI_Medium = 469,
#         Clash_Practice_Easy = 470,
#         Clash_Tutorial = 471,
#         Arena_Practice_Medium = 472,
#         Joust_Practice_Medium = 473,
#         Joust_vs_AI_Easy = 474,
#         Conquest_Practice_Medium = 475,
#         Conquest_vs_AI_Easy = 476,
#         Clash_Practice_Medium = 477,
#         Clash_vs_AI_Easy = 478,
#         Assault_Practice_Easy = 479,
#         Assault_Practice_Medium = 480,
#         Assault_vs_AI_Easy = 481,
#         Joust_3v3_Training = 482,
#         Arena_Training = 483,
#         Adventure_Horde = 495,
#         Jungle_Practice_Presele_ = 496,
#         Adventure_Joust = 499,
#         Adventure_CH10 = 500,
#         Loki_Dungeon = 501,
#         Joust_1v1_Ranked_GamePad = 502,
#         Joust_3v3_Ranked_GamePad = 503,
#         Conquest_Ranked_GamePad = 504,
#     }
class QueueType(Enum):
    Conquest = 426
    # Conquest = 423
    Novice_Queue = 424
    Practice = 427
    Custom_Conquest = 429
    Domination = 433
    MOTD = 434
    Arena = 435
    Basic_Tutorial = 436
    Custom_Arena = 438
    Ranked_Duel = 440
    Custom_Joust = 441
    Arena_Practice_Easy = 443
    Jungle_Practice = 444
    Assault = 445
    Custom_Assault = 446
    Joust = 448
    Ranked_Joust = 450
    Ranked_Conquest = 451
    Arena_League = 452
    Assault_AI_Medium = 454
    Joust_AI_Medium = 456
    Arena_AI_Easy = 457
    Conquest_Practice_Easy = 458
    Siege = 459
    Custom_Siege = 460
    Conquest_AI_Medium = 461
    Arena_Tutorial = 462
    Conquest_Tutorial = 463
    Joust_Practice_Easy = 464
    Clash = 466
    Custom_Clash = 467
    Arena_AI_Medium = 468
    Clash_AI_Medium = 469
    Clash_Practice_Easy = 470
    Clash_Tutorial = 471
    Arena_Practice_Medium = 472
    Joust_Practice_Medium = 473
    Joust_AI_Easy = 474
    Conquest_Practice_Medium = 475
    Conquest_AI_Easy = 476
    Clash_Practice_Medium = 477
    Clash_AI_Easy = 478
    Assault_Practice_Easy = 479
    Assault_Practice_Medium = 480
    Assault_AI_Easy = 481
    Joust_Training = 482
    Arena_Training = 483
    Ranked_Duel_GamePad = 502
    Ranked_Joust_GamePad = 503
    Conquest_Ranked_GamePad = 504
    Slash = 10189


def calculateParties(teamList1, teamList2):
    party_map = {}  # Dictionary to map party IDs to lists of players in each party
    party_counter = 0  # Counter to track the current party number

    teamList = teamList1.CompletePlayerList + teamList2.CompletePlayerList
    # First pass: build the party map
    for player in teamList:
        party_id = player.PartyId

        if party_id in party_map:
            party_map[party_id].append(player)
        else:
            party_map[party_id] = [player]

    # Second pass: assign party numbers, setting to -1 for solo players
    for party_id, players in party_map.items():
        if len(players) == 1:
            # Solo player
            players[0].setParty(-1)
            players[0].setPartyEmoji()
        else:
            # Players in party
            party_counter += 1
            for player in players:
                player.setParty(party_counter)
                player.setPartyEmoji()


class smite(commands.Cog):

    # TODO
    # - redo stats
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

    def createEndOfMatchEmbed(self, ign: str):
        """
        takes the player name provided and looks up their stats and most recent match
        to show them on an embed.

        does this multiple times to show up to 10 people per game

        :param ign: PlayerName
        :return: Embed
        """
        match = self.Smite.createCompleteMatchStats(ign)
        sortedMatch = match
        calculateParties(sortedMatch[0], sortedMatch[1])

        # Match Type and Length for Embed
        gameType = QueueType(int(sortedMatch[0].CompletePlayerList[0].match_queue_id)).name.replace('_', ' ')
        gameLength = sortedMatch[0].CompletePlayerList[0].Time_In_Match_Seconds / 60
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gameType} | {int(gameLength)} Minutes")

        # Get and Set all God Emojis for each team
        for player in sortedMatch[0].CompletePlayerList:
            try:
                player.godEmoji = self.emojis[str(player.godName).replace(" ", "")]
            except KeyError:
                player.godEmoji = " "
            try:
                player.item1 = self.emojis[str(player.Item_Purch_1).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item1 = self.emojis["noitem"]
            try:
                player.item2 = self.emojis[str(player.Item_Purch_2).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item2 = self.emojis["noitem"]
            try:
                player.item3 = self.emojis[str(player.Item_Purch_3).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item3 = self.emojis["noitem"]
            try:
                player.item4 = self.emojis[str(player.Item_Purch_4).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item4 = self.emojis["noitem"]
            try:
                player.item5 = self.emojis[str(player.Item_Purch_5).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item5 = self.emojis["noitem"]
            try:
                player.item6 = self.emojis[str(player.Item_Purch_6).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item6 = self.emojis["noitem"]

            player.itemEmojis = player.gatherItemEmojis()

        for player in sortedMatch[1].CompletePlayerList:
            try:
                player.godEmoji = self.emojis[str(player.godName).replace(" ", "")]
            except KeyError:
                player.godEmoji = " "

            try:
                player.item1 = self.emojis[str(player.Item_Purch_1).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item1 = self.emojis["noitem"]
            try:
                player.item2 = self.emojis[str(player.Item_Purch_2).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item2 = self.emojis["noitem"]
            try:
                player.item3 = self.emojis[str(player.Item_Purch_3).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item3 = self.emojis["noitem"]
            try:
                player.item4 = self.emojis[str(player.Item_Purch_4).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item4 = self.emojis["noitem"]
            try:
                player.item5 = self.emojis[str(player.Item_Purch_5).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item5 = self.emojis["noitem"]
            try:
                player.item6 = self.emojis[str(player.Item_Purch_6).replace(" ", "").replace("'", "")]
            except KeyError:
                player.item6 = self.emojis["noitem"]

            player.itemEmojis = player.gatherItemEmojis()

        # Make Variable Easier to Read
        t1, t2 = sortedMatch[0], sortedMatch[1]

        # Make the User on the Left
        for player in t2.CompletePlayerList:
            if player.playerName.lower() == ign.lower():
                # swap
                t1, t2 = t2, t1

        # First Embed Line
        # Determine Winner and Loser, Calculate Team Damage, Calculate Team KDA
        if t1.Win_Status == "Winner":
            embed.add_field(name=f":trophy:{t1.Win_Status}:trophy:",
                            value=f"\n:crossed_swords:KDA:{t1.team_kda}\n:dagger:Damage:{t1.totalDamage}", inline=True)
        else:
            embed.add_field(name=f":red_circle:{t1.Win_Status}:red_circle:",
                            value=f"\n:crossed_swords:KDA:{t1.team_kda}\n:dagger:Damage:{t1.totalDamage}", inline=True)
        embed.add_field(name=f"", value=f"\n ", inline=True)
        if t2.Win_Status == "Winner":
            embed.add_field(name=f":trophy:{t2.Win_Status}:trophy:",
                            value=f"\n:crossed_swords:KDA:{t2.team_kda}\n:dagger:Damage:{t2.totalDamage}", inline=True)
        else:
            embed.add_field(name=f":red_circle:{t2.Win_Status}:red_circle:",
                            value=f"\n:crossed_swords:KDA:{t2.team_kda}\n:dagger:Damage:{t2.totalDamage}", inline=True)

        # List PLayers and stats as follows:
        # Name
        # KDA Ratio
        # Platform
        # Level
        # Party Number
        for i in range(len(t1.CompletePlayerList)):
            embed.add_field(name=f"{t1.CompletePlayerList[i].getGodEmoji()} {t1.CompletePlayerList[i].playerName}",
                            value=f"\n{t1.CompletePlayerList[i].itemEmojis}\n:crossed_swords:KDA:{t1.CompletePlayerList[i].currentMatchKDA}\n:dagger:Damage:{t1.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t1.CompletePlayerList[i].Gold_Earned}",
                            inline=True)
            embed.add_field(
                name=f"{t1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {t2.CompletePlayerList[i].accountLevel:3d}",
                value=f"\n{t1.CompletePlayerList[i].partyEmoji} <:blank:1131261670153527346> {t2.CompletePlayerList[i].partyEmoji}\n{t1.CompletePlayerList[i].platformEmoji} <:blank:1131261670153527346> {t2.CompletePlayerList[i].platformEmoji}",
                inline=True)

            embed.add_field(name=f"{t2.CompletePlayerList[i].getGodEmoji()} {t2.CompletePlayerList[i].playerName}",
                            value=f"\n{t2.CompletePlayerList[i].itemEmojis}\n:crossed_swords:KDA:{t2.CompletePlayerList[i].currentMatchKDA}\n:dagger:Damage:{t2.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{t2.CompletePlayerList[i].Gold_Earned}",
                            inline=True)

        # Set bottom of Embed to useful info
        embed.set_footer(text=f"{t1.Match_Id}", icon_url="")

        return embed

    def createLiveMatchEmbed(self, ign):
        match = self.Smite.createCompleteStatsLive(ign)
        sortedMatch = match
        calculateParties(sortedMatch[0], sortedMatch[1])

        # Match Type and Length for Embed
        gameType = QueueType(int(sortedMatch[0].CompletePlayerList[0].queue)).name
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gameType} | Live Match")

        # Get and Set all God Emojis for each team
        for player in sortedMatch[0].CompletePlayerList:
            try:
                player.godEmoji = self.emojis[str(player.godName).replace(" ", "")]
            except KeyError:
                player.godEmoji = " "
        for player in sortedMatch[1].CompletePlayerList:
            try:
                player.godEmoji = self.emojis[str(player.godName).replace(" ", "")]
            except KeyError:
                player.godEmoji = " "

        # Make Variable Easier to Read
        t1, t2 = sortedMatch[0], sortedMatch[1]

        # Make the User on the Left
        for player in t2.CompletePlayerList:
            if player.playerName.lower() == ign.lower():
                # swap
                t1, t2 = t2, t1

        print(t1.CompletePlayerList[0])

        # Compute a score for each team
        # (weight(importance) * value)
        # t1Scores = [0.4 * player.win_ratio + 0.5 * player.kdr + 0.001 * player.playtime for player in
        #             t1.CompletePlayerList]
        # t2Scores = [0.4 * player.win_ratio + 0.5 * player.kdr + 0.001 * player.playtime for player in
        #             t2.CompletePlayerList]
        #
        # t1.AvgScore = sum(t1Scores) / len(t1Scores)
        # t2.AvgScore = sum(t2Scores) / len(t2Scores)
        #
        # # Make a prediction based on the average scores
        # if t1.AvgScore > t2.AvgScore:
        #     t1.prediction = True
        #     t2.prediction = False
        # elif t1.AvgScore < t2.AvgScore:
        #     t1.prediction = False
        #     t2.prediction = True
        # else:
        #     t1.prediction = None
        #     t2.prediction = None

        # List PLayers and stats as follows:
        # Name
        # KDA Ratio
        # Platform
        # Level
        # Party Number
        # embed.add_field(name="Match Prediction:", value="", inline=True)
        # embed.add_field(name="", value="", inline=True)
        # embed.add_field(name="", value="", inline=True)
        #
        # if t1.prediction is True and t2.prediction is False:
        #     embed.add_field(name=f":trophy:Winner:trophy:",
        #                     value=f"\n:crossed_swords:Score:{t1.AvgScore}", inline=True)
        #     embed.add_field(name="", value="", inline=True)
        #     embed.add_field(name=f":red_circle:Loser:red_circle:",
        #                     value=f"\n:crossed_swords:Score:{t2.AvgScore}", inline=True)
        # if t1.prediction is False and t2.prediction is True:
        #     embed.add_field(name=f":trophy:Winner:trophy:",
        #                     value=f"\n:crossed_swords:Score:{t1.AvgScore}", inline=True)
        #     embed.add_field(name="", value="", inline=True)
        #     embed.add_field(name=f":red_circle:Loser:red_circle:",
        #                     value=f"\n:crossed_swords:Score:{t2.AvgScore}", inline=True)

        for i in range(len(t1.CompletePlayerList)):
            embed.add_field(name=f"{t1.CompletePlayerList[i].getGodEmoji()} {t1.CompletePlayerList[i].playerName}",
                            value=f"\n:crossed_swords:KDA: {t1.CompletePlayerList[i].kdr}\n:small_orange_diamond:WR: {int(t1.CompletePlayerList[i].winratio)}%",
                            inline=True)

            embed.add_field(
                name=f"{t1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {t2.CompletePlayerList[i].accountLevel:3d}",
                value=f"\n{t1.CompletePlayerList[i].platformEmoji} <:blank:1131261670153527346> {t2.CompletePlayerList[i].platformEmoji}",
                inline=True)

            embed.add_field(name=f"{t2.CompletePlayerList[i].getGodEmoji()} {t2.CompletePlayerList[i].playerName}",
                            value=f"\n:crossed_swords:KDA: {t2.CompletePlayerList[i].kdr}\n:small_orange_diamond:WR: {int(t2.CompletePlayerList[i].winratio)}%",
                            inline=True)

        # Set bottom of Embed to useful info
        embed.set_footer(text=f"{t1.Match_Id}", icon_url="")

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
        msg = None

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
            if (before_smite_status, after_smite_status) != tracked_presence:  # Check if the status has actually changed
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
