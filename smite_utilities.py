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

    def getMatch(self, inGameName: str):
        match = self.smite.getMatch(1300411352)
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

    complete = wow.getLiveMatch("Marbach")
    for player in complete:
        print(player, "\n\n")


if __name__ == "__main__":
    main()
