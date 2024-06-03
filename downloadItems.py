import os
import requests
import shutil
from dotenv import load_dotenv
from pyrez.api import SmiteAPI

load_dotenv()


def save_image(image_url, save_path):
    response = requests.get(image_url, stream=True)
    with open(save_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


# Instantiate the API wrapper
devID = int(os.getenv("DEV_ID"))
key = os.getenv("AUTH_KEY")

api = SmiteAPI(devID, key)

# Get all items
items = api.getItems()

# Download all item images
# for item in items:
#     image_url = item.itemIcon_URL
#     # Prepare filename: remove spaces and commas, save as .jpg
#     filename = "".join([c for c in item.itemName if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ".jpg"
#     filename = filename.replace(' ', '').replace(',', '')
#     save_path = os.path.join('/items', filename)
#     save_image(image_url, save_path)

# print(items)
for item in items:
    if item.activeFlag:
        print(str(item.deviceName).replace(" ", "").replace("'", "").replace("*", "").replace("-", "") + ": " + str(item.itemId))
