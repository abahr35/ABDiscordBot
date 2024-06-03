from smite_utilities import CompleteTeam
from helpers import smiteEnums


def calculateParties(sortedMatch: tuple[CompleteTeam, CompleteTeam]):
    """
    figures out party number in match based on both teams and changes input teams
    :param sortedMatch
    :return: None
    """

    teamList1, teamList2 = sortedMatch

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


def _get_emoji(key, isGod=False):
    """
    Helper function to retrieve an emoji from the emoji's dictionary.
    If the key is not found, it returns the emoji for the default key.
    :param key: string(name of emoji)
    :param isGod: Default: True | used to determine ValueError, Blank or " "
    :return: Emoji in discord readable way
    """

    sanitized_key = str(key).replace(" ", "").replace("'", "")
    try:
        return smiteEnums.Emoji[sanitized_key].value

    except KeyError:
        if isGod is True:
            return smiteEnums.UIEmoji["blank"].value
        else:
            return smiteEnums.Emoji["noitem"].value


def batchSetEmoji(sortedTeams: tuple[CompleteTeam, CompleteTeam]):
    """
    Helper mutator function to set the emojis for each player in the team
    sets God, items

    :param sortedTeams:
    :return: None
    """

    # Get and Set all God Emojis for each team
    for player in sortedTeams[0].CompletePlayerList:
        print(player.godName)
        player.setGodEmoji = _get_emoji(player.godName, isGod=True)
        player.item1 = _get_emoji(player.Item_Purch_1)
        player.item2 = _get_emoji(player.Item_Purch_2)
        player.item3 = _get_emoji(player.Item_Purch_3)
        player.item4 = _get_emoji(player.Item_Purch_4)
        player.item5 = _get_emoji(player.Item_Purch_5)
        player.item6 = _get_emoji(player.Item_Purch_6)
        player.itemEmojis = player.groupItemEmojis()  # set to usable string

    for player in sortedTeams[1].CompletePlayerList:
        print(player.godName)
        player.setGodEmoji = _get_emoji(player.godName, isGod=True)
        player.item1 = _get_emoji(player.Item_Purch_1)
        player.item2 = _get_emoji(player.Item_Purch_2)
        player.item3 = _get_emoji(player.Item_Purch_3)
        player.item4 = _get_emoji(player.Item_Purch_4)
        player.item5 = _get_emoji(player.Item_Purch_5)
        player.item6 = _get_emoji(player.Item_Purch_6)
        player.itemEmojis = player.groupItemEmojis()  # set to usable string
