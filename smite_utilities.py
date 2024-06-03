import os
import re

from helpers import smiteEnums
import pyrez
import pyrez.api
import pyrez.enumerations
import pyrez.models
import requests
from dotenv import load_dotenv
from pyrez.api import SmiteAPI

load_dotenv()


class PlayerStats(pyrez.models.Smite.Player, pyrez.models.PlayerAcheviements):
    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.PlayerAcheviements.__init__(self, **kwargs)


class CompletePlayer(pyrez.models.Smite.Player, pyrez.models.LiveMatch, pyrez.models.PlayerAcheviements):
    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.LiveMatch.__init__(self, **kwargs)
        pyrez.models.PlayerAcheviements.__init__(self, **kwargs)

        # Checking for name, overwriting garbage data
        if kwargs.get("playerName") == "":
            kwargs["playerName"] = "~~HiddenProfile~~"
            self.setPlayerName("~~HiddenProfile~~")
        self.setPlayerName(re.sub(r"\[.*?\]", '', kwargs.get("playerName")))

        self.partyNumber = 0
        self.partyEmoji = ""
        self.godEmoji = None
        self.isSolo = False
        self.itemEmojis = None
        self.item1 = None
        self.item2 = None
        self.item3 = None
        self.item4 = None
        self.item5 = None
        self.item6 = None
        self.platformEmoji = None
        self.ConquestEmoji = None
        self.JoustEmoji = None
        self.DuelEmoji = None
        self.setGodEmoji()
        self.setPlatformEmoji()
        self.setRankEmojis()

    def setRankEmojis(self):
        try:
            rankedCQ = smiteEnums.Rank(self.__kwargs__.get("Tier_Conquest")).name
        except ValueError:
            rankedCQ = "Unranked"
        self.ConquestEmoji = smiteEnums.RankEmoji["Conquest" + re.sub(r'(I{1,3}|IV|V)$', '', rankedCQ)].value

        try:
            rankedJ = smiteEnums.Rank(self.__kwargs__.get("Tier_Joust")).name
        except ValueError:
            rankedJ = "Unranked"
        self.JoustEmoji = smiteEnums.RankEmoji["Joust" + re.sub(r'(I{1,3}|IV|V)$', '', rankedJ)].value

        try:
            rankedD = smiteEnums.Rank(self.__kwargs__.get("Tier_Duel")).name
        except ValueError:
            rankedD = "Unranked"
        self.DuelEmoji = smiteEnums.RankEmoji["Duel" + re.sub(r'(I{1,3}|IV|V)$', '', rankedD)].value

    def setPlayerName(self, name: str):
        self.playerName = name

    def setParty(self, partyID: int):
        self.partyNumber = partyID

    def setPartyEmoji(self):
        if self.partyNumber == 1:
            self.partyEmoji = "<:party1:1131297842980458506>"
        elif self.partyNumber == 2:
            self.partyEmoji = "<:party2:1131297853403316276>"
        elif self.partyNumber == 3:
            self.partyEmoji = "<:party3:1131297867164819616> "
        elif self.partyNumber == 4:
            self.partyEmoji = "<:party4:1131297899607752807> "
        else:
            self.partyEmoji = "<:partySolo:1131267287958179851>"

    def setPlatformEmoji(self):
        """
            Unknown = -1
            HiRez = 1
            Steam = 5
            PS4 = 9
            Xbox = 10
            Switch = 22
            Discord = 25
            Epic_Games = 28

        :return:
        """
        if self.playerPortalId is not None:
            if self.playerPortalId == "1":
                self.platformEmoji = "<:portalHirez:1134174555938754571>"
            elif self.playerPortalId == "5":
                self.platformEmoji = "<:portalSteam:1134174557620678707>"
            elif self.playerPortalId == "9":
                self.platformEmoji = "<:portalPS:1134174557025083493>"
            elif self.playerPortalId == "10":
                self.platformEmoji = "<:portalXbox:1134174560237916341>"
            elif self.playerPortalId == "22":
                self.platformEmoji = "<:portalSwitch:1134174559243870300>"
            elif self.playerPortalId == "25":
                self.platformEmoji = "<:portalDiscord:1134174552654618688>"
            elif self.playerPortalId == "28":
                self.platformEmoji = "<:portalEpic:1134174554865029201>"
            else:
                self.platformEmoji = "<:blank:1131261670153527346>"

        else:
            if self.Platform == "Hirez":
                self.platformEmoji = "<:portalHirez:1134174555938754571>"
            elif self.Platform == "Steam":
                self.platformEmoji = "<:portalSteam:1134174557620678707>"
            elif self.Platform == "PSN":
                self.platformEmoji = "<:portalPS:1134174557025083493>"
            elif self.Platform == "XboxLive":
                self.platformEmoji = "<:portalXbox:1134174560237916341>"
            elif self.Platform == "Nintendo":
                self.platformEmoji = "<:portalSwitch:1134174559243870300>"
            elif self.Platform == "Discord":
                self.platformEmoji = "<:portalDiscord:1134174552654618688>"
            elif self.Platform == "EpicGames":
                self.platformEmoji = "<:portalEpic:1134174554865029201>"
            else:
                self.platformEmoji = "<:blank:1131261670153527346>"

    def setGodEmoji(self):
        print(smiteEnums.God(self.__kwargs__.get("GodId")).name)
        try:
            self.godEmoji = smiteEnums.Emoji[
                smiteEnums.God(self.__kwargs__.get("GodId")).name.replace(" ", "").replace("'", "").replace("_",
                                                                                                            "")].value
        except KeyError:
            self.godEmoji = smiteEnums.UIEmoji["blank"].value

    def getGodEmoji(self):
        return self.godEmoji

    @property
    def currentMatchKDA(self):
        return f"{self.Kills_Player}/{self.match_Deaths}/{self.Assists}"

    @property
    def kdr(self):
        try:
            total_kills = (self.AssistedKills / 2) + self.PlayerKills
            if self.Deaths != 0:
                kdr = total_kills / self.Deaths
                return round(kdr, 2)
            else:
                return total_kills

        except:
            return 0

    def groupItemEmojis(self):
        """
        makes emojis readable for embed
        e1+e2+e3...

        :return: str(emojis)
        """
        emojis = ""
        emojis += str(self.item1)
        emojis += str(self.item2)
        emojis += str(self.item3)
        emojis += str(self.item4)
        emojis += str(self.item5)
        emojis += str(self.item6)
        return emojis


class CompleteTeam:
    def __init__(self, CompletePlayerList: list[CompletePlayer]):
        self.CompletePlayerList = CompletePlayerList
        self.Win_Status = CompletePlayerList[0].Win_Status
        self.Match_Id = CompletePlayerList[0].matchId
        self.CalculateAverageMMR()
        self.CalculateAverageRank()
        self.CQAvgMMR = 0
        self.JAvgMMR = 0
        self.DAvgMMR = 0
        self.CQAvgRank = 0
        self.JAvgRank = 0
        self.DAvgRank = 0
        self.CQRankEmoji = ""
        self.JRankEmoji = ""
        self.DRankEmoji = ""
        self.CQRankName = ""
        self.JRankName = ""
        self.DRankName = ""

    @property
    def getConquestAverage(self):
        return self.CQAvgMMR

    @property
    def getJoustAverage(self):
        return self.JAvgMMR

    @property
    def getDuelAverage(self):
        return self.DAvgMMR

    @property
    def totalDamage(self):
        totalDamage = 0
        for player in self.CompletePlayerList:
            totalDamage += player.Damage_Player
        return totalDamage

    @property
    def team_kda(self) -> str:
        """
        calculates teams KDA
        :return: Team Kills/Deaths/Assists
        """

        t1KDA = [(player.Kills_Player, player.match_Deaths, player.Assists) for player in self.CompletePlayerList]
        Kills = sum(e[0] for e in t1KDA)
        Deaths = sum(e[1] for e in t1KDA)
        Assists = sum(e[2] for e in t1KDA)
        return f"{int(Kills)}/{int(Deaths)}/{int(Assists)}"

    def CalculateAverageRank(self):
        for player in self.CompletePlayerList:
            self.CQAvgRank += smiteEnums.Rank(player.tierConquest).value
            self.JAvgRank += smiteEnums.Rank(player.tierJoust).value
            self.DAvgRank += smiteEnums.Rank(player.tierDuel).value
        self.CQAvgRank /= len(self.CompletePlayerList)
        self.JAvgRank /= len(self.CompletePlayerList)
        self.DAvgRank /= len(self.CompletePlayerList)

        try:
            rankedCQ = smiteEnums.Rank(int(self.CQAvgRank)).name
        except ValueError:
            rankedCQ = "Unranked"
        self.CQRankEmoji = smiteEnums.RankEmoji["Conquest" + re.sub(r'(I{1,3}|IV|V)$', '', rankedCQ)].value
        self.CQRankName = smiteEnums.Rank(int(self.CQAvgRank))

        try:
            rankedJ = smiteEnums.Rank(int(self.JAvgRank)).name
        except ValueError:
            rankedJ = "Unranked"
        self.JRankEmoji = smiteEnums.RankEmoji["Joust" + re.sub(r'(I{1,3}|IV|V)$', '', rankedJ)].value
        self.JRankName = smiteEnums.Rank(int(self.JAvgRank))

        try:
            rankedD = smiteEnums.Rank(int(self.DAvgRank)).name
        except ValueError:
            rankedD = "Unranked"
        self.DRankEmoji = smiteEnums.RankEmoji["Duel" + re.sub(r'(I{1,3}|IV|V)$', '', rankedD)].value
        self.DRankName = smiteEnums.Rank(int(self.DAvgRank))

    def CalculateAverageMMR(self):
        # Conquest
        for player in self.CompletePlayerList:
            self.CQAvgMMR += player.rankedConquest.rankStat
            self.JAvgMMR += player.rankedJoust.rankStat
            self.DAvgMMR += player.rankedDuel.rankStat
        self.CQAvgMMR /= len(self.CompletePlayerList)
        self.JAvgMMR /= len(self.CompletePlayerList)
        self.DAvgMMR /= len(self.CompletePlayerList)


class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def getDamage(self, playerList):
        totalDamage = 0
        for player in playerList:
            totalDamage += player.Damage_Player
        return totalDamage

    def getMatchType(self, gameModeId):
        if gameModeId is None:
            return ""
        try:
            return pyrez.enumerations.QueueSmite(gameModeId).name
        except ValueError:
            return "Mystery Game"

    def getPlayerStats(self, inGameName: str):
        playerStats = self.smite.getPlayer(inGameName)
        playerAchivements = self.smite.getPlayerAchievements(playerStats.playerId)

        playerDict = {}
        playerDict.update(playerStats.__kwargs__)
        playerDict.update(playerAchivements.__kwargs__)
        _ = PlayerStats(**playerDict)
        return _

    def createCompleteStatsLive(self, InGameName):
        """
            Gets match data from recent match. Uses data from match to get player stats and achievements.
            Internally handles private players.
            Also sorts by team to return.
        :param InGameName: string
        :return: tuple(CompleteTeam, CompleteTeam)
        """
        compiledMatch = []
        match = self.getLiveMatch(InGameName)
        for player in match:
            match_dict = player.__kwargs__
            try:
                match_dict["match_Deaths"] = match_dict["Deaths"]
            except KeyError:
                pass

            if player.hidden_profile:
                player.playerName = "~~Hidden Profile~~"
                player_dict = pyrez.models.Smite.Player()
                player_achievement_dict = pyrez.PlayerAcheviements()
                combined_data = {}
                combined_data.update(match_dict)
                combined_data.update(player_dict)
                combined_data.update(player_achievement_dict)
                compiledMatch.append(CompletePlayer(**combined_data))

            else:  # not Private
                try:
                    player_achievement_dict = self.smite.getPlayerAchievements(player.playerId).__kwargs__
                    player_dict = self.smite.getPlayer(player.playerId).__kwargs__

                except pyrez.exceptions.PlayerNotFound:
                    player_dict = pyrez.models.Smite.Player()
                    player_achievement_dict = pyrez.PlayerAcheviements()

                combined_data = {}
                combined_data.update(match_dict)
                combined_data.update(player_dict)
                combined_data.update(player_achievement_dict)

                compiledMatch.append(CompletePlayer(**combined_data))

        teamOneList, teamTwoList = [], []
        for player in compiledMatch:
            (teamOneList, teamTwoList)[player.taskForce == 1].append(player)

        teamOne, teamTwo = CompleteTeam(teamOneList), CompleteTeam(teamTwoList)

        return teamOne, teamTwo

    def createCompleteMatchStats(self, InGameName):
        """
            Gets match data from recent match. Uses data from match to get player stats and achievements.
            Internally handles private players.
            Also sorts by team to return.
        :param InGameName: string
        :return: tuple(CompleteTeam, CompleteTeam)
        """

        compiledMatch = []
        match = self.getRecentMatch(InGameName)
        for player in match:
            match_dict = player.__kwargs__
            try:
                match_dict["match_Deaths"] = match_dict["Deaths"]
            except KeyError:
                pass

            try:
                player_achievement_dict = self.smite.getPlayerAchievements(player.playerId).__kwargs__
                player_dict = self.smite.getPlayer(player.playerId).__kwargs__
            except pyrez.exceptions.PlayerNotFound:
                player_dict = pyrez.models.Smite.Player()
                player_achievement_dict = pyrez.PlayerAcheviements()

            combined_data = {}
            combined_data.update(match_dict)
            combined_data.update(player_dict)
            combined_data.update(player_achievement_dict)
            compiledMatch.append(CompletePlayer(**combined_data))

        teamOneList, teamTwoList = [], []
        for player in compiledMatch:
            (teamOneList, teamTwoList)[player.taskForce == 1].append(player)

        teamOne, teamTwo = CompleteTeam(teamOneList), CompleteTeam(teamTwoList)
        return teamOne, teamTwo

    def getPlayerID(self, inGameName: str):
        try:
            playerID = self.smite.getPlayerId(inGameName)
            return playerID[0].playerId
        except pyrez.exceptions.PlayerNotFound:
            return

    def getRecentMatch(self, inGameName: str):
        matches = self.smite.getMatchHistory(self.getPlayerID(inGameName))
        mostRecent = self.smite.getMatch(matches[0].matchId)
        return mostRecent

    def getMatchByID(self, matchId: int):
        match = self.smite.getMatch(matchId)
        return match

    def getLiveMatch(self, inGameName: str):
        playerID = self.getPlayerID(inGameName)
        playerStatus = self.smite.getPlayerStatus(playerID)
        liveMatchID = playerStatus.Match
        try:
            return self.smite.getMatch(liveMatchID, isLiveMatch=True)
        except requests.exceptions.HTTPError:
            return


def main():
    devID = int(os.getenv("DEV_ID"))
    key = os.getenv("AUTH_KEY")
    wow = SmiteTracker(devID, key)
    name = "JodiHighroll3r"


if __name__ == "__main__":
    main()
