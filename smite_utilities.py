import os
import pyrez
import pyrez.api
import pyrez.enumerations
import pyrez.models
import requests
from dotenv import load_dotenv
from pyrez.api import SmiteAPI
import json
import pprint

load_dotenv()


class CompletePlayer(pyrez.models.Smite.Player, pyrez.models.LiveMatch):
    # PlayerStats: pyrez.models.Smite.Player, LiveMatchObject

    def __init__(self, **kwargs):
        pyrez.models.Smite.Player.__init__(self, **kwargs)
        pyrez.models.LiveMatch.__init__(self, **kwargs)
        self.partyNumber = 0

    def setParty(self, id: int):
        self.partyNumber = id

    def getParty(self):
        return self.partyNumber


class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def getMatchType(self, gameModeId) -> str:
        acceptableIds = [426, 435, 440, 445, 448, 451, 450, 10189, 10193, 10195, 10197]
        acceptableMds = ["Conquest", "Arena", "Siege", "Assault", "Joust", "Ranked Conquest", "Ranked Joust", "Slash",
                         "Noob Conquest", "Noob Arena", "Noob Joust"]
        matchDictionary = dict(zip(acceptableIds, acceptableMds))
        try:
            return matchDictionary[gameModeId]
        except KeyError:
            return "Mystery Game"

    def getPlayerStats(self, inGameName: str):
        try:
            return self.smite.getPlayer(inGameName)
        except pyrez.PlayerNotFound:
            return pyrez.models.Player

    def generateParty(self, players):
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

            print(f"partyID: {party_id} -> partyNumber: {party_number}")

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

    match = wow.createCompleteStats("jodihighroll3r")

    sortedMatch = wow.generateParty(match)

    print("T1")
    for player in sortedMatch[0]:
        print(player.getParty())
        print(player.PartyId)

    print("T2")
    for player in sortedMatch[1]:
        print(player.getParty())
        print(player.PartyId)


if __name__ == "__main__":
    main()
