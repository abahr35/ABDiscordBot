import os
from typing import List, Union, Type

import pyrez
import pyrez.api
import requests
from pyrez.api import SmiteAPI
import pyrez.enumerations
import pyrez.models
from dotenv import load_dotenv

load_dotenv()


# TODO
class CompletePlayer:
    def __init__(self, PlayerStats: pyrez.models.Smite.Player, LiveMatchObject):
        self.playerStats = PlayerStats
        self.liveMatchObject = LiveMatchObject

class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def getPlayerStats(self, inGameName: str):
        try:
            return self.smite.getPlayer(inGameName)
        except pyrez.PlayerNotFound:
            return pyrez.models.Player

    #todo was here 4/5
    def createCompleteStats(self, InGameName):
        match = self.getLiveMatch(InGameName)
        stats = []
        completeStats = []

        for player in match:
            if player.playerName != "":
                stats.append(self.getPlayerStats(str(player.playerName)))
            else:
                stats.append(None)

        for i in range(len(match)):
            completeStats.append(CompletePlayer(stats[i], match[i]))

        return completeStats

    def getPlayerID(self, inGameName: str):
        try:
            playerID = self.smite.getPlayerId(inGameName)
            return playerID[0].playerId
        except pyrez.exceptions.PlayerNotFound:
            return

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
    name = "MistressKarma"

    complete = wow.createCompleteStats(name)
    for player in complete:
        if player.playerStats is not None:
            print(type(player.playerStats))
            print(player.playerStats.winratio)
        print(player.liveMatchObject.godId)

    # players = wow.getLiveMatch(name)
    #
    # teamOne, teamTwo, teamOnePlayerStats, teamTwoPlayerStats = [], [], [], []
    #
    # for player in players:
    #     (teamOne, teamTwo)[player.taskForce == 1].append(player)  # if taskforce == 1 append teamOne else team 2
    #     if player.playerName == "":
    #         player.playerName = "~~Hidden Profile~~"
    # for player in teamOne:
    #     if player.playerName != "~~Hidden Profile~~":
    #         teamOnePlayerStats.append(wow.getPlayerStats(player.playerName))
    #     else:
    #         teamOnePlayerStats.append(pyrez.Player)
    #
    # for player in teamTwo:
    #     if player.playerName != "~~Hidden Profile~~":
    #         teamTwoPlayerStats.append(wow.getPlayerStats(player.playerName))
    #     else:
    #         teamTwoPlayerStats.append(pyrez.Player)
    #
    # print(len(teamOne))
    # print(len(teamTwo))
    # print(type(teamOne[0]))
    #
    # for i in range(len(teamOne)):
    #     print("Team 1: \n", teamOne[i])
    #     print(f"Stats: \n {int(teamOnePlayerStats[i].winratio)}% MMR: {teamOne[i].Rank_Stat}")
    #
    # for i in range(len(teamTwo)):
    #     print("Team 2: \n", teamTwo[i])
    #     print(f"Stats: \n {int(teamOnePlayerStats[i].winratio)}% MMR: {teamTwo[i].Rank_Stat}")


if __name__ == "__main__":
    main()
