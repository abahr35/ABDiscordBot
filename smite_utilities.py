import os

import pyrez
import pyrez.api
import pyrez.enumerations
import pyrez.models
import requests
from dotenv import load_dotenv
from pyrez.api import SmiteAPI

load_dotenv()


class CompletePlayer(pyrez.models.Smite.Player, pyrez.models.LiveMatch):
    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.LiveMatch.__init__(self, **kwargs)
        if self.hidden_profile:
            self.setPlayerName("~~Hidden Profile~~")
        self.partyNumber = 0
        self.emoji = None
        self.isSolo = False

    def setPlayerName(self, name: str):
        self.playerName = name

    def setParty(self, partyID: int):
        self.partyNumber = partyID

    def getParty(self):
        return self.partyNumber

    def setEmoji(self, emoji):
        self.emoji = emoji

    def getEmoji(self):
        return self.emoji

    @property
    def matchKDA(self):
        return f"{self.Kills_Player}/{self.Deaths}/{self.Assists}"

    @property
    def kdr(self):
        # total_kills = self. + (assists * 0.5)
        # kdr = total_kills / deaths if deaths != 0 else total_kills
        return 0  # or kdr

    def getPortal(self):
        try:
            return pyrez.enumerations.PortalId(self.portalId).name
        except ValueError:
            return "Mystery Console"


class CompleteTeam:
    def __init__(self, CompletePlayerList: list[CompletePlayer]):
        self.CompletePlayerList = CompletePlayerList
        self.calculateParties()
        self.Win_Status = CompletePlayerList[0].Win_Status
        self.Match_Id = CompletePlayerList[0].matchId

    def calculateParties(self):
        party_map = {}  # Dictionary to map party IDs to party numbers
        party_counter = 0  # Counter to track the current party number

        for player in self.CompletePlayerList:
            party_id = player.PartyId

            if party_id in party_map:
                # If party ID already exists in the map, assign the existing party number
                party_number = party_map[party_id]
            else:
                # If party ID is new, increment the counter and assign the next party number
                party_counter += 1
                party_number = party_counter
                party_map[party_id] = party_number

            player.setParty(party_number)

    @property
    def totalDamage(self):
        totalDamage = 0
        for player in self.CompletePlayerList:
            totalDamage += player.Damage_Player
        return totalDamage

    @property
    def kda(self) -> str:
        """
        calculates teams KDA
        :return: Team Kills/Deaths/Assists
        """
        t1KDA = [(player.Kills_Player, player.Deaths, player.Assists) for player in self.CompletePlayerList]
        pCount = len(t1KDA)
        avgKills = sum([e[0] for e in t1KDA]) / pCount
        avgDeaths = sum(e[1] for e in t1KDA) / pCount
        avgAssists = sum(e[2] for e in t1KDA) / pCount
        return f"{int(avgKills)}/{int(avgDeaths)}/{int(avgAssists)}"


class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def getDamage(self, playerList):
        totalDamage = 0
        for player in playerList:
            totalDamage += player.Damage_Player
        return totalDamage

    def getKDA(self, playerList):
        teamKills = 0
        teamDeaths = 0
        teamAssists = 0
        for player in playerList:
            teamKills += player.Kills_Player
            teamDeaths += player.Deaths
            teamAssists += player.Assists
        return f"{teamKills}/{teamDeaths}/{teamAssists}"

    def getMatchType(self, gameModeId):
        if gameModeId is None:
            raise TypeError
        try:
            return pyrez.enumerations.QueueSmite(gameModeId).name
        except ValueError:
            return "Mystery Game"

    def getPlayerStats(self, inGameName: str):
        try:
            return self.smite.getPlayer(inGameName)
        except pyrez.PlayerNotFound:
            return pyrez.models.Player

    def generateParty(self, players) -> tuple[list[CompletePlayer], list[CompletePlayer]]:
        party_map = {}  # Dictionary to map party IDs to party numbers
        party_counter = 0  # Counter to track the current party number

        for player in players:
            party_id = player.PartyId

            if party_id in party_map:
                # If party ID already exists in the map, assign the existing party number
                party_number = party_map[party_id]
            else:
                # If party ID is new, increment the counter and assign the next party number
                party_counter += 1
                party_number = party_counter
                party_map[party_id] = party_number

            player.setParty(party_number)

            # print(f"partyID: {party_id} -> partyNumber: {party_number}")

        return self.sortTeams(players)

    def createCompleteStats(self, InGameName):
        compiledMatch = []
        match = self.getRecentMatch(InGameName)
        for player in match:
            match_dict = player.__kwargs__
            try:
                if player.playerName == "":
                    player.playerName = "~~Hidden Profile~~"
                player_dict = self.smite.getPlayer(player.playerId).__kwargs__

            except pyrez.exceptions.PlayerNotFound:
                player_dict = pyrez.models.Smite.Player()

            combined_data = {}
            combined_data.update(match_dict)
            combined_data.update(player_dict)

            compiledMatch.append(CompletePlayer(**combined_data))

        teamOneList, teamTwoList = [], []
        for player in compiledMatch:
            (teamOneList, teamTwoList)[player.taskForce == 1].append(player)

        teamOne, teamTwo = CompleteTeam(teamOneList), CompleteTeam(teamTwoList)

        return teamOne, teamTwo

    def createLiveCompleteStats(self, InGameName):
        compiledMatch = []
        match = self.getLiveMatch(InGameName)
        for player in match:
            match_dict = player.__kwargs__
            try:
                if player.playerName == "":
                    player.playerName = "~~Hidden Profile~~"
                player_dict = self.smite.getPlayer(player.playerId).__kwargs__

            except pyrez.exceptions.PlayerNotFound:
                player_dict = pyrez.models.Smite.Player()

            combined_data = {}
            combined_data.update(match_dict)
            combined_data.update(player_dict)

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
    name = "JodiHighRoll3r"

    match = wow.createCompleteStats(name)

    sortedMatch = wow.generateParty(match)

    print(sortedMatch[0][0])

    # for player in sortedMatch[0]:
    #     print(player.playerName)

    # print("T1")
    # for player in sortedMatch[0]:
    #     print()
    #     print(player.playerName)
    #     print(player.getParty())
    #     print(player.godName)
    #     print(player.godId)
    #     print(player.PartyId)
    #
    # print("\nT2")
    # for player in sortedMatch[1]:
    #     print()
    #     print(player.playerName)
    #     print(player.getParty())
    #     print(player.godName)
    #     print(player.godId)
    #     print(player.PartyId)


if __name__ == "__main__":
    main()
