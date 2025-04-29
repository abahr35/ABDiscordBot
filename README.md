# Smite Tracker Discord Bot

A Python-based **Discord bot** that tracks and displays **player stats** and **recent match data** for [Smite](https://www.smitegame.com/), using the **Hi-Rez Studios API**. The bot responds to user commands and automatically fetches updates based on Discord presence changes.

## ⚙️ Features

 **Player Rating Lookup**  
  Fetches and displays **player ratings** using the Hi-Rez API.

-  **Automatic Match Tracking**  
  Observes Discord **presence changes** (e.g., launching Smite) and automatically fetches **recent match data**.

-  **Clean, Structured Output**  
  Parses raw API data and returns **easy-to-read summaries** directly in Discord channels.

-  **Async Performance**  
  Uses **Async-IO** to handle multiple Discord commands and API calls **concurrently** for responsive user experience.

## 🛠 Tech Stack

- **Python 3.9+**
- **discord.py**
- **AsyncIO**
- **Hi-Rez API**

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or later
- Discord Bot Token
- Hi-Rez API developer credentials (Dev ID and Auth Key)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/smite-tracker-bot.git
   cd smite-tracker-bot

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Add your API keys and bot token to a .env file

4. Run the bot
   ```bash
   python bot.py
   
## 💡 Commands

- /stats <username>
- /trackme <username> (Monitors user presence for state changes and calls the stats of each player in the lobby.)

## 🔐 API Keys

- You must request Hi-Rez API credentials, and register a bot application via the Discord Developer Portal.

## Screenshots
Stats Command:

![image](https://github.com/user-attachments/assets/0801ac79-ab60-4775-91ab-0275b0974cfc)

Trackme command, automatically posted when a user leaves the match:

![image](https://github.com/user-attachments/assets/fffc0b1d-4270-465e-90a2-4c212f7b2416)

Trackme command, automatically posted when a user joins a match:

![image](https://github.com/user-attachments/assets/5da73fc0-1b8a-48a2-ba98-9504879ffd78)

## 📚 Learning Objectives

This project was developed in 2023 to demonstrate:

Integration of third-party APIs (Hi-Rez, Discord)

Use of asynchronous programming with AsyncIO

Building real-time interactive bots

Data cleaning and presentation in user-facing formats

