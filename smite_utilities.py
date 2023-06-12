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
    # PlayerStats: pyrez.models.Smite.Player, LiveMatchObject

    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.LiveMatch.__init__(self, **kwargs)
        if self.hidden_profile:
            self.setPlayerName("~~Hidden Profile~~")
        self.partyNumber = 0
        self.emoji = None

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

    def getKDA(self):
        return f"{self.Kills_Player}/{self.Deaths}/{self.Assists}"

    def getPortal(self):
        try:
            return pyrez.enumerations.PortalId(self.portalId).name
        except ValueError:
            return "Mystery Console"


class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def downloadItems(self):
        # downloadItems for emojis
        item_icons = self.smite.getItems()
        count = 0
        for item in item_icons:
            icon_url = item.itemIconURL
        response = requests.get(icon_url)
        name1 = item.deviceName.replace(" ", "")
        name1 = name1.replace("*", "")
        name1 = name1.replace("'", "")
        with open(f"items/{name1}.png", "wb") as file:
            file.write(response.content)
        count += 1
        print(f"wrote {name1}.png {count}")
        print("finished")

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

    def sortTeams(self, playerList: list[CompletePlayer]):
        teamOne, teamTwo = [], []
        for player in playerList:
            (teamOne, teamTwo)[player.taskForce == 1].append(player)
        return teamOne, teamTwo

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

        return compiledMatch

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
