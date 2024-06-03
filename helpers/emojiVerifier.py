from smite_utilities import SmiteTracker
from helpers import smiteEnums


def VerifyGods(smiteObj: SmiteTracker, currentEmojis: dict):
    updatedGods = smiteObj.smite.getGods()

    # Enum names as a set for efficient look-up
    currentGodNames = {god.name.replace("_", "") for god in smiteEnums.God}

    unimplementedGods = []
    for God in updatedGods:
        # Sanitizing name to match enum format (removing spaces and apostrophes)
        sanitized_name = str(God.godName).replace(" ", "").replace("'", "")
        if sanitized_name not in currentGodNames:
            unimplementedGods.append(God.godName)

    print("Unimplemented Gods", unimplementedGods)


# def VerifyItems(smiteObj: SmiteTracker, currentEmojis: dict):
#     updatedItems = smiteObj.smite.getItems()  # Replace with your method to get items
#
#     # Assuming you have an enum for items similar to gods
#     currentItems = {item.name.replace("_", "") for item in smiteEnums.Items}
#
#     unimplementedItems = []
#     for item in updatedItems:
#         # Sanitizing the item name (adjust this according to your item names)
#         sanitized_name = str(item.itemName).replace(" ", "").replace("'", "")
#         if sanitized_name not in currentItems:
#             unimplementedItems.append(item.itemName)
#
#     print(unimplementedItems)

def VerifyItems():
    godNames = {god.name for god in smiteEnums.God}
    itemNames = {item.name for item in smiteEnums.Item}
    emojiNames = {emoji.name for emoji in smiteEnums.Emoji}
    print(itemNames)
    print(emojiNames)

    unimplementedEmoji = [item_name for item_name in itemNames if item_name not in emojiNames]
    print("Unimplemented Emojis", unimplementedEmoji)

