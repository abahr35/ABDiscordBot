import discord
from datetime import datetime

from helpers import smiteEnums
from smite_utilities import CompleteTeam


def CreateSettings(sortedTeams: tuple[CompleteTeam, CompleteTeam], isLive=False):
    """
    starts the embed process, sets all the info that is unorganized
    :param isLive:
    :param sortedTeams:
    :return: embed
    """
    # Match Type and Length for Embed
    gameType = smiteEnums.QueueType(int(sortedTeams[0].CompletePlayerList[0].match_queue_id)).name.replace('_', ' ')
    gameLength = sortedTeams[0].CompletePlayerList[0].Time_In_Match_Seconds / 60
    embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
    if isLive is False:
        embed.set_author(name=f"{gameType} | {int(gameLength)} Minutes")
    else:
        gameType = smiteEnums.QueueType(int(sortedTeams[0].CompletePlayerList[0].Queue)).name.replace('_', ' ')
        # gameLength = sortedTeams[0].CompletePlayerList[0].Time_In_Match_Seconds / 60
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.now())
        embed.set_author(name=f"{gameType} | Live Match")
    return embed  # not a complete Embed


def CreateHeader(embed, team1: CompleteTeam, team2: CompleteTeam, isLive=False):
    """
    Creates the header, displays proper side for winner loser
    :param isLive:
    :param embed: Embed with settings
    :param team1:
    :param team2:
    :return: embed
    """
    if isLive is False:
        # TODO create ranked embed and Ranked enums continue on body, add to CompletePlayer, remove prints, live match embeds
        if "Ranked" in smiteEnums.QueueType(int(team1.CompletePlayerList[0].match_queue_id)).name:
            # Ranked
            # Determine Winner and Loser, Calculate Team Damage, Calculate Team KDA
            if team1.Win_Status == "Winner":
                embed.add_field(
                    name=f":trophy:{team1.Win_Status}:trophy:",
                    value=f"\n:crossed_swords:KDA:{team1.team_kda}\n:small_blue_diamond:**Averages:**{team1.totalDamage}",
                    inline=True)
            else:
                embed.add_field(
                    name=f":red_circle:{team1.Win_Status}:red_circle:",
                    value=f"\n:crossed_swords:KDA:{team1.team_kda}\n:dagger:Damage:{team1.totalDamage}",
                    inline=True)

            embed.add_field(name=f"", value=f"\n ", inline=True)

            if team2.Win_Status == "Winner":
                embed.add_field(
                    name=f":trophy:{team2.Win_Status}:trophy:",
                    value=f"\n:crossed_swords:KDA:{team2.team_kda}\n:dagger:Damage:{team2.totalDamage}",
                    inline=True)
            else:
                embed.add_field(
                    name=f":red_circle:{team2.Win_Status}:red_circle:",
                    value=f"\n:crossed_swords:KDA:{team2.team_kda}\n:dagger:Damage:{team2.totalDamage}",
                    inline=True)
            return embed
        else:
            # First Embed Line
            # Determine Winner and Loser, Calculate Team Damage, Calculate Team KDA
            if team1.Win_Status == "Winner":
                embed.add_field(
                    name=f":trophy:{team1.Win_Status}:trophy:",
                    value=f"\n:crossed_swords:KDA:{team1.team_kda}\n:dagger:Damage:{team1.totalDamage}",
                    inline=True)
            else:
                embed.add_field(
                    name=f":red_circle:{team1.Win_Status}:red_circle:",
                    value=f"\n:crossed_swords:KDA:{team1.team_kda}\n:dagger:Damage:{team1.totalDamage}",
                    inline=True)

            embed.add_field(name=f"", value=f"\n ", inline=True)

            if team2.Win_Status == "Winner":
                embed.add_field(
                    name=f":trophy:{team2.Win_Status}:trophy:",
                    value=f"\n:crossed_swords:KDA:{team2.team_kda}\n:dagger:Damage:{team2.totalDamage}",
                    inline=True)
            else:
                embed.add_field(
                    name=f":red_circle:{team2.Win_Status}:red_circle:",
                    value=f"\n:crossed_swords:KDA:{team2.team_kda}\n:dagger:Damage:{team2.totalDamage}",
                    inline=True)
            return embed
    else:  # Live = True
        if "Ranked" in smiteEnums.QueueType(int(team1.CompletePlayerList[0].Queue)).name:
            # Ranked
            # Calculate MMR Averages

            if "Conquest" in smiteEnums.QueueType(int(team1.CompletePlayerList[0].Queue)).name:
                embed.add_field(
                        name=f":small_blue_diamond:Averages::small_blue_diamond:",
                        value=f"\n{team1.CQRankEmoji, team1.CQRankName} [{team1.getConquestAverage}]\n ",
                        inline=True)

                embed.add_field(name=f"", value=f"\n ", inline=True)

                embed.add_field(
                        name=f":small_blue_diamond:Averages::small_blue_diamond:",
                        value=f"\n{team2.CQRankEmoji, team2.CQRankName} [{team2.getConquestAverage}]\n ",
                        inline=True)
                return embed

def CreateBody(embed, team1, team2, isLive=False):
    """
    Checks if player is hidden, tries to prevent error with name, prints stats in line
    :param isLive:
    :param embed: Embed with settings and header
    :param team1:
    :param team2:
    :return: embed
    """

    if isLive is False:
        for i in range(len(team1.CompletePlayerList)):
            embed.add_field(
                name=f"{team1.CompletePlayerList[i].getGodEmoji()} {team1.CompletePlayerList[i].playerName}",
                value=f"\n{team1.CompletePlayerList[i].itemEmojis}\n:crossed_swords:KDA:{team1.CompletePlayerList[i].currentMatchKDA}\n:dagger:Damage:{team1.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{team1.CompletePlayerList[i].Gold_Earned}",
                inline=True)
            embed.add_field(
                name=f"{team1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {team2.CompletePlayerList[i].accountLevel:3d}",
                value=f"\n{team1.CompletePlayerList[i].partyEmoji} <:blank:1131261670153527346> {team2.CompletePlayerList[i].partyEmoji}\n{team1.CompletePlayerList[i].platformEmoji} <:blank:1131261670153527346> {team2.CompletePlayerList[i].platformEmoji}",
                inline=True)
            embed.add_field(
                name=f"{team2.CompletePlayerList[i].getGodEmoji()} {team2.CompletePlayerList[i].playerName}",
                value=f"\n{team2.CompletePlayerList[i].itemEmojis}\n:crossed_swords:KDA:{team2.CompletePlayerList[i].currentMatchKDA}\n:dagger:Damage:{team2.CompletePlayerList[i].Damage_Player}\n:coin:Gold:{team2.CompletePlayerList[i].Gold_Earned}",
                inline=True)
        return embed
    else:
        for i in range(len(team1.CompletePlayerList)):
            embed.add_field(
                name=f"{team1.CompletePlayerList[i].getGodEmoji()} {team1.CompletePlayerList[i].playerName}",
                value=f"\n:crossed_swords:KDA: {team1.CompletePlayerList[i].kdr}\n:small_orange_diamond:WR: {int(team1.CompletePlayerList[i].winratio)}%",
                inline=True)

            embed.add_field(
                name=f"{team1.CompletePlayerList[i].accountLevel:3d} <:level:1093664230928023603> {team2.CompletePlayerList[i].accountLevel:3d}",
                value=f"\n{team1.CompletePlayerList[i].platformEmoji} <:blank:1131261670153527346> {team2.CompletePlayerList[i].platformEmoji}",
                inline=True)

            embed.add_field(
                name=f"{team2.CompletePlayerList[i].getGodEmoji()} {team2.CompletePlayerList[i].playerName}",
                value=f"\n:crossed_swords:KDA: {team2.CompletePlayerList[i].kdr}\n:small_orange_diamond:WR: {int(team2.CompletePlayerList[i].winratio)}%",
                inline=True)
        return embed
