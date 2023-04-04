import os

import pyrez
import pyrez.api
import requests
from pyrez.api import SmiteAPI
import pyrez.enumerations
import pyrez.models
from dotenv import load_dotenv

load_dotenv()

class embedInfo():
    def __init__(self):
        self.player = None
        self.livematch = None


class SmiteTracker:
    def __init__(self, devID: int, authKey: str):
        self.smite = SmiteAPI(devID, authKey)

    def getPlayerStats(self, inGameName: str):
        return self.smite.getPlayer(inGameName)

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
    id = int(os.getenv("DEV_ID"))
    key = os.getenv("AUTH_KEY")
    wow = SmiteTracker(id, key)
    name = "BOOM555"

    players = wow.getLiveMatch(name)
    print(players)
    team1 = []
    team2 = []

    for i in range(len(players)):
        if players[i].taskForce == 1:
            team1.append(players[i])

        elif players[i].taskForce == 2:
            team2.append(players[i])
        else:
            print("not added")

    print("Team 1: \n", team1)
    print("Team 2: \n", team2)

    # try:
    #     for player in match:
    #         try:
    #
    #             if player.playerName == "":
    #                 print("No name found")
    #             else:
    #                 print(player.playerName)
    #             print(player.accountLevel)
    #             try:
    #                 print(wow.getPlayerStats(player.playerId).winratio)
    #             except AttributeError:
    #                 print("Not found")
    #         except pyrez.exceptions.PlayerNotFound:
    #             print("Hidden Player")
    #             print("-")
    #             print("-")
    # except TypeError:
    #     pass

    # print(unformattedStats)


if __name__ == "__main__":
    main()
