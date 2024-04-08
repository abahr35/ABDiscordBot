import random

import discord.ui
from discord.ext import commands
from discord.ui import Button, View
from discord import Embed, Interaction


# Blackjack game logic
class Blackjack:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []

    def create_deck(self):
        """Creates and shuffles a deck of 52 cards"""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        deck = [{'suit': suit, 'value': value} for suit in suits for value in values]
        random.shuffle(deck)
        return deck

    def draw_card(self):
        """Draws a card from the deck"""
        if len(self.deck) > 0:
            return self.deck.pop()
        else:
            self.deck = self.create_deck()  # Reshuffle and recreate deck if empty
            return self.deck.pop()

    def calculate_score(self, hand):
        """Calculates the score of a hand"""
        score = 0
        ace_count = 0
        for card in hand:
            value = card['value']
            if value in ['Jack', 'Queen', 'King']:
                score += 10
            elif value == 'Ace':
                ace_count += 1
                score += 11
            else:
                score += int(value)

        while score > 21 and ace_count:
            score -= 10
            ace_count -= 1

        return score

    def player_hit(self):
        """Player draws a card"""
        self.player_hand.append(self.draw_card())

    def dealer_play(self):
        """Dealer's play logic"""
        while self.calculate_score(self.dealer_hand) < 17:
            self.dealer_hand.append(self.draw_card())


class BlackjackButtons(discord.ui.View):

    def __init__(self, game, ctx):
        super().__init__(timeout=180)  # Timeout after 3 minutes of inactivity
        self.game = game
        self.ctx = ctx

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit_button(self, button: Button, interaction: Interaction):
        self.game.player_hit()
        player_score = self.game.calculate_score(self.game.player_hand)
        if player_score > 21:
            # Player busts, reveal dealer's full hand
            embed = self.ctx.cog.create_game_embed(self.game, "Bust! You lose.", game_over=True)
            await interaction.response.edit_message(embed=embed, view=None)
            del self.ctx.cog.games[self.ctx.channel.id]
        else:
            embed = self.ctx.cog.create_game_embed(self.game, "Your turn!")
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand_button(self, button: Button, interaction: Interaction):
        self.game.dealer_play()
        player_score = self.game.calculate_score(self.game.player_hand)
        dealer_score = self.game.calculate_score(self.game.dealer_hand)
        result = "It's a draw!" if player_score == dealer_score else \
            "You win!" if player_score > dealer_score or dealer_score > 21 else "You lose!"
        embed = self.ctx.cog.create_game_embed(self.game, result, game_over=True)
        await interaction.response.edit_message(embed=embed, view=None)
        del self.ctx.cog.games[self.ctx.channel.id]


# Discord Cog for Blackjack with Embeds and Buttons
class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    def card_to_str(self, card):
        """Converts a card dictionary to a string representation with emojis for suits."""
        suit_emojis = {
            'Hearts': '♥️',
            'Diamonds': '♦️',
            'Clubs': '♣️',
            'Spades': '♠️'
        }
        return f"{card['value']} {suit_emojis[card['suit']]}"

    def hand_to_str(self, hand):
        """Converts a hand (list of card dictionaries) to a string representation."""
        return ', '.join([self.card_to_str(card) for card in hand])

    def create_game_embed(self, game, message, game_over=False):
        """Creates an embed to display the game state with formatted cards."""
        embed = Embed(title="♠️♥️ Blackjack Game ♦️♣️", description=message, color=0x1F8B4C)
        embed.add_field(name="Your Hand", value=self.hand_to_str(game.player_hand), inline=False)

        if game_over:
            # When the game is over, show the full dealer's hand
            dealer_hand_str = self.hand_to_str(game.dealer_hand)
        else:
            # During the game, hide the second card
            dealer_hand_str = self.hand_to_str([game.dealer_hand[0]]) + ", [hidden]"

        embed.add_field(name="Dealer's Hand", value=dealer_hand_str, inline=False)
        embed.set_footer(text="Game over." if game_over else "Use the buttons below to 'Hit' or 'Stand'.")
        return embed

    @discord.slash_command(name="blackjack", description="Starts a new game of Blackjack")
    async def blackjack(self, ctx):
        """Starts a new game of Blackjack with buttons."""
        if ctx.channel.id in self.games:
            await ctx.send("A game is already in progress in this channel.")
            return

        game = Blackjack()
        self.games[ctx.channel.id] = game
        game.player_hand.append(game.draw_card())
        game.player_hand.append(game.draw_card())
        game.dealer_hand.append(game.draw_card())
        game.dealer_hand.append(game.draw_card())

        embed = self.create_game_embed(game, "Your turn! Choose 'Hit' or 'Stand'.")
        view = BlackjackButtons(game, ctx)
        await ctx.send(embed=embed, view=view)

    @discord.slash_command(name="exitblackjack", description="Ends the current game of blackjack")
    async def exit_blackjack(self, ctx):
        """Ends the current game of Blackjack in the channel."""
        if ctx.channel.id not in self.games:
            await ctx.send("There is no ongoing game of Blackjack in this channel.")
        else:
            del self.games[ctx.channel.id]  # Remove the game from the active games dictionary
            await ctx.send("The game of Blackjack has been ended.")


def setup(bot):
    bot.add_cog(BlackjackCog(bot))
