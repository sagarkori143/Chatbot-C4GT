import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNELID = int(os.getenv('CHANNELID'))
# Define your API endpoint
API_URL = 'http://127.0.0.1:5000/chatbot'

# Initialize the bot with the required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.content.startswith('/'):
        await message.channel.send("Please type commands only.", delete_after=10)
        await message.delete()
        return

    await bot.process_commands(message)

@bot.tree.command(name="menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message("Please select an option from the menu:", ephemeral=True)
    await show_menu(interaction, "menu")

async def show_menu(interaction, menu_key):
    # Define the data to send in the API request
    data = {'choice': menu_key}

    # Send the data to the API
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        await interaction.followup.send("An error occurred while loading the menu.", ephemeral=True)
        return

    # Process the API response
    response_data = response.json()
    print(f"API Response Data: {response_data}")
    if "options" in response_data:
        options = response_data["options"]
        view = View()
        for option in options:
            view.add_item(OptionButton(label=option, custom_id=f'{interaction.id}_{option}'))
        await interaction.followup.send(f"Please choose an option from {menu_key}:", view=view, ephemeral=True)
    else:
        print(f"Options not found in API response: {response_data}")
        await interaction.followup.send("An error occurred while loading the menu.", ephemeral=True)

import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token and channel ID from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNELID = int(os.getenv('CHANNELID'))

# Define your API endpoint
API_URL = 'http://127.0.0.1:5000/chatbot'

# Initialize the bot with the required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Store the current menu state
menu_state = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.tree.command(name="menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message("Please select an option from the menu:", ephemeral=True)
    await show_menu(interaction, "menu")

async def show_menu(interaction, menu_key):
    global menu_state

    # Fetch the menu options from the API
    data = {'choice': menu_key}
    response = fetch_from_api(data)
    if response is None:
        await interaction.followup.send("An error occurred while loading the menu.", ephemeral=True)
        return

    menu_state[interaction.user.id] = response.get('options', [])

    options = menu_state[interaction.user.id]
    if not options:
        await interaction.followup.send("No options available.", ephemeral=True)
        return

    view = View()
    for option in options:
        button = OptionButton(label=option)
        button.callback = lambda inter, opt=option: handle_option_selection(inter, opt)
        view.add_item(button)

    await interaction.followup.send(f"Please choose an option:", view=view, ephemeral=True)

class OptionButton(Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)

async def handle_option_selection(interaction, option_key):
    global menu_state

    # Fetch data from API based on the option key
    data = {'choice': option_key}
    response = fetch_from_api(data)

    if response is None:
        await interaction.response.send_message("An error occurred while processing your request. Please try again.", ephemeral=True)
        return

    if 'options' in response:
        menu_state[interaction.user.id] = response['options']
        await show_menu(interaction, option_key)
    elif 'answer' in response:
        await interaction.edit_original_response(content=response['answer'])
    elif 'error' in response:
        await interaction.response.send_message(response['error'], ephemeral=True)

def fetch_from_api(data):
    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Run the bot with your token
bot.run(DISCORD_TOKEN)

# Run the bot with your token
bot.run(DISCORD_TOKEN)
