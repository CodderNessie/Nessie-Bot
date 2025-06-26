import discord
from discord.ext import commands
from discord import app_commands
import os
import time
import random
import json
import asyncio
import traceback
from discord.ext import tasks
from datetime import datetime, timedelta
from discord.ui import View, Button
from flask import Flask
from threading import Thread
from yt_dlp import YoutubeDL
from discord import ui, ButtonStyle
from discord import app_commands

from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
intents = discord.Intents.default()
intents.guilds = True
intents.invites = True
intents = discord.Intents.default()
intents.members = True  # Important for permissions & member info
client = discord.Client(intents=intents)

class ContinueButtonView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # no timeout, active until lottery ends

    @ui.button(label="Continue", style=ButtonStyle.green, custom_id="continue_button")
    async def continue_button(self, interaction: discord.Interaction, button: ui.Button):
        global lottery_active, lottery_tickets

        if not lottery_active:
            await interaction.response.send_message("❌ The lottery is no longer active.", ephemeral=True)
            return

        user_id = interaction.user.id
        if user_id in lottery_tickets:
            ticket_number = lottery_tickets[user_id]
            await interaction.response.send_message(
                f"🎟️ You already have ticket #{ticket_number}. Check your DMs!", ephemeral=True
            )
            return

        existing = set(lottery_tickets.values())
        while True:
            number = random.randint(1000, 9999)
            if number not in existing:
                break

        lottery_tickets[user_id] = number

        try:
            await interaction.user.send(f"🎟️ Your lottery ticket number is **#{number}**. Good luck!")
            await interaction.response.send_message("✅ Ticket sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I couldn't send you a DM. Please check your privacy settings.", ephemeral=True
            )

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # Log full traceback in console for debugging
    import traceback
    print(f"Error in command {interaction.command.name}:")
    traceback.print_exception(type(error), error, error.__traceback__)

    # Send a friendly message to the user
    await interaction.response.send_message("⚠️ An unexpected error occurred. Please try again later.", ephemeral=True)

# Replace this with your actual Discord user ID (integer)
BOT_OWNER_ID = 1294971967530864785

ALLOWED_CHANNEL_ID = 1387835814112792736  # Replace with your channel ID here

# === Modal 1: Password ===
class PasswordModal(discord.ui.Modal, title="Authorization Required"):
    password = discord.ui.TextInput(label="Enter Password",
                                    placeholder="Enter the secret password",
                                    required=True,
                                    style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        if self.password.value.strip() != "NESSecurity":
            await interaction.response.send_message(
                "❌ Incorrect password. Access denied.", )
            return

        class ContinueView(discord.ui.View):

            @discord.ui.button(label="Continue",
                               style=discord.ButtonStyle.success)
            async def continue_button(self,
                                      button_interaction: discord.Interaction,
                                      button: discord.ui.Button):
                await button_interaction.response.send_modal(LoginModal())

        await interaction.response.send_message(
            "✅ Password correct. Click below to continue.",
            view=ContinueView(),
        )


# === Modal 2: Login ===
class LoginModal(discord.ui.Modal, title="Login Required"):
    username = discord.ui.TextInput(label="Username",
                                    placeholder="Enter username",
                                    required=True,
                                    style=discord.TextStyle.short)
    password = discord.ui.TextInput(label="Password",
                                    placeholder="Enter password",
                                    required=True,
                                    style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        if self.username.value.strip(
        ) == "Nessie" and self.password.value.strip() == "Nessie7511":
            embed = discord.Embed(
                title="🖥️ System Access Granted",
                description="Choose an option below. \n **Nessie Security™**",
                color=discord.Color.green())
            embed.set_image(
                url=
                "https://www.bleepstatic.com/content/hl-images/2021/06/15/Windows--11.jpg"
            )

            await interaction.response.send_message(embed=embed,
                                                    view=SystemControlView())
        else:
            await interaction.response.send_message(
                "❌ Incorrect login credentials.")


# === Modal 3: User ID Modal ===
class UserIDModal(discord.ui.Modal, title="Enter Target User ID"):
    user_id = discord.ui.TextInput(label="Discord User ID",
                                   placeholder="Target ID here",
                                   required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            user = await interaction.client.fetch_user(int(self.user_id.value))
        except Exception:
            await interaction.followup.send(
                "❌ Could not find a user with that ID.")
            return

        embed = discord.Embed(
            title="🔐 ACCESSING TARGET...",
            description=
            f"User located: `{user.name}#{user.discriminator}`\nInitiating breach...",
            color=discord.Color.dark_red())
        embed.set_image(
            url=user.avatar.url if user.avatar else user.default_avatar.url)

        await interaction.followup.send(embed=embed)

        # Spooky hacker messages
        await asyncio.sleep(2)
        await interaction.followup.send("💻 Breach in progress...")
        await asyncio.sleep(1.5)
        await interaction.followup.send("🧬 Identity override complete.")
        await asyncio.sleep(1)
        await interaction.followup.send("📂 Memory dump initialized... ")
        await asyncio.sleep(2)
        await interaction.followup.send("🔒 Encryption key obtained...")
        await asyncio.sleep(1.5)
        await interaction.followup.send("🔓 Access granted.")
        await asyncio.sleep(1)
        await interaction.followup.send("💥 Target compromised.")
        await asyncio.sleep(2)
        await interaction.followup.send("Cracking for more targets...")
        await asyncio.sleep(2)
        await interaction.followup.send("🔑 Finding passwords...")
        await asyncio.sleep(4)
        await interaction.followup.send(
            "Transferring data from target... Please wait. This may take a while."
        )
        await asyncio.sleep(6)  # shorten for testing; set to 60 if needed
        await interaction.followup.send(
            "✅ Data transfer complete. Target is now under control. ⚠️")
        await asyncio.sleep(0.5)
        await interaction.followup.send("Transfer finished.")
        await asyncio.sleep(0.6)
        await interaction.followup.send(
            "Continue Removing Encryption Keys... 🔏")
        await asyncio.sleep(2)
        await interaction.followup.send("Deleting account and data... 🗑️")
        await asyncio.sleep(3)
        await interaction.followup.send("Removed ✅")


# === View with Buttons after Login ===
class SystemControlView(discord.ui.View):

    @discord.ui.button(label="Target Folder",
                       style=discord.ButtonStyle.primary)
    async def open_target(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.send_modal(UserIDModal())

    @discord.ui.button(label="Close System", style=discord.ButtonStyle.danger)
    async def close_system(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        try:
            await interaction.response.defer()
            await interaction.message.delete()
        except Exception as e:
            print(f"[Close System] Error: {e}")
            await interaction.followup.send("❌ Could not close system.")

def get_default_channel():
    if client.guilds:
        guild = client.guilds[0]
        return guild.system_channel or discord.utils.get(guild.text_channels, permissions__send_messages=True)
    return None



def is_awake():

    async def predicate(interaction):
        if interaction.user.id in sleeping_users:
            await interaction.response.send_message(
                "😴 You are sleeping and can't use commands right now. Use /wake-up to wake up."
            )
            return True
        return True

    return app_commands.check(predicate)

class MusicURLModal(discord.ui.Modal, title="Enter Music URL"):
    url = discord.ui.TextInput(
        label="YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        required=True,
        max_length=200,
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        vc_id = vc_selection.get(self.user_id)
        if not vc_id:
            await interaction.response.send_message("No VC selected.", ephemeral=True)
            return

        voice_channel = interaction.guild.get_channel(vc_id)
        if not voice_channel:
            await interaction.response.send_message("VC not found.", ephemeral=True)
            return

        if interaction.guild.voice_client:
            vc = interaction.guild.voice_client
            await vc.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()

        from yt_dlp import YoutubeDL
        ydl_opts = {'format': 'bestaudio', 'quiet': True, 'noplaylist': True}

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url.value, download=False)
                audio_url = info['url']
                vc.play(discord.FFmpegPCMAudio(audio_url))
                await interaction.response.send_message(f"🎶 Now playing: **{info['title']}**")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

def save_data():
    # Implement your data saving here
    pass

def get_default_channel():
    for guild in client.guilds:
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            return guild.system_channel
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
    return None

async def is_admin(interaction: discord.Interaction):
    member = interaction.guild.get_member(interaction.user.id)
    if member is None:
        member = await interaction.guild.fetch_member(interaction.user.id)
    return member.guild_permissions.administrator

# === GLOBALS & DATA ===
DATA_FILE = "data.json"

vc_selection = {}

forced_sleep_until = {}
sleeping_users = set()
user_balances = {}
last_steal_times = {}
last_daily_reward_times = {}
last_give_money_times = {}
user_shields = {}
user_selected_guns = {}
recent_thefts = []
last_error_trace = None
user_inventories = {}  # track user inventories

WEAPONS = [
    "a rusty pistol", "a crossbow", "a shadowy dagger", "a blazing torch",
    "an enchanted sword", "a vial of poison", "a cursed axe",
    "a bone-crushing hammer"
]

SHOP_ITEMS = {
    "Mystery Box": 100_000,
    "Shield": 250_000,
}


# === DATA LOAD/SAVE ===
def save_data():
    data = {
        "user_balances": user_balances,
        "last_steal_times": last_steal_times,
        "last_daily_reward_times": last_daily_reward_times,
        "last_give_money_times": last_give_money_times,
        "user_shields": user_shields,
        "user_selected_guns": user_selected_guns,
        "recent_thefts": recent_thefts,
        "user_inventories": user_inventories,
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# === LOTTERY SYSTEM ===
lottery_tickets = {}  # {user_id: ticket_number}
lottery_active = False
lottery_end_time = None

def get_default_channel():
    for guild in client.guilds:
        return guild.system_channel or discord.utils.get(guild.text_channels, permissions__send_messages=True)
    return None


def load_data():
    global user_balances, last_steal_times, last_daily_reward_times, last_give_money_times, user_shields, user_selected_guns, recent_thefts, user_inventories
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            user_balances.update({
                int(k): v
                for k, v in data.get("user_balances", {}).items()
            })
            last_steal_times.update({
                int(k): v
                for k, v in data.get("last_steal_times", {}).items()
            })
            last_daily_reward_times.update({
                int(k): v
                for k, v in data.get("last_daily_reward_times", {}).items()
            })
            last_give_money_times.update({
                int(k): v
                for k, v in data.get("last_give_money_times", {}).items()
            })
            user_shields.update({
                int(k): v
                for k, v in data.get("user_shields", {}).items()
            })
            user_selected_guns.update({
                int(k): v
                for k, v in data.get("user_selected_guns", {}).items()
            })
            recent_thefts.extend(data.get("recent_thefts", []))
            user_inventories.update({
                int(k): v
                for k, v in data.get("user_inventories", {}).items()
            })


# === FLASK KEEP-ALIVE SETUP ===
app = Flask(__name__)


@app.route('/')
def home():
    return "Nessie Discord Bot is running!"


@app.route('/health')
def health():
    return {
        "status":
        "online",
        "bot":
        str(client.user)
        if 'client' in globals() and client.user else "Not logged in"
    }


def run_flask():
    app.run(host='0.0.0.0', port=5000)


def keep_alive():
    server = Thread(target=run_flask)
    server.daemon = True
    server.start()


# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    load_data()
    await tree.sync()
    print(f"Nessie is online as {client.user}")


# === COMMANDS ===


@tree.command(name="commands", description="List all commands")
@is_awake()
async def commands_command(interaction: discord.Interaction):
    cmds = [
        "/help - Instructions and info",
        "/pfp - Show a user's avatar",
        "/feed-nessie - Feed Nessie some fish",
        "/punch - Try punching Nessie",
        "/guns-list - Show all guns",
        "/select-gun - Pick a gun",
        "/attack - Attack a user",
        "/say - Make Nessie say something",
        "/debug - Show last error trace",
        "/steal - Steal money from a user",
        "/bank - Check your balance",
        "/give - Give money to another user",
        "/daily-reward - Claim your daily reward ($1,000,000 every 24h)",
        "/give-money - Get $500,000 every 5 minutes",
        "/ping - Check bot's latency",
        "/shop - Show shop items",
        "/buy - Buy an item",
        "/use - Use an item",
        "/inventory - Show your inventory",
        "/version - See the version of Nessie",
        "/roblox - Play roblox",
        "/eat - Eat something",
        "/sleep - Sleep",
        "/drink - Drink something",
        "/wake-up - Wake up",
        "/see - See something unexpected",
        "/think - Think about something",
        "/do - Do something",
        "/ha-music - get the link of a good codding music",
    ]
    await interaction.response.send_message("**Nessie Bot Commands:**\n" +
                                            "\n".join(cmds))


@tree.command(name="help", description="Get instructions on how to use Nessie")
@is_awake()
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Mention me to chat or use /commands to see all commands!")


@tree.command(name="pfp", description="Show a user's avatar")
@is_awake()
@app_commands.describe(user="User to show avatar of (optional)")
async def pfp_command(interaction: discord.Interaction,
                      user: discord.User = None):
    target = user or interaction.user
    embed = discord.Embed(title=f"{target.name}'s Profile Picture")
    embed.set_image(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)


@tree.command(name="feed-nessie", description="Feed Nessie some fish")
@is_awake()
async def feed_nessie_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Aw, thank you so much! I love fish ヾ(•ω•`)o")


@tree.command(name="punch", description="Try punching Nessie")
@is_awake()
async def punch_command(interaction: discord.Interaction):
    await interaction.response.send_message("Ow! Please, stop! o(≧口≦)o")


@tree.command(name="guns-list", description="Show all guns you can pick")
@is_awake()
async def guns_list_command(interaction: discord.Interaction):
    guns_list = "\n".join(f"- {gun}" for gun in WEAPONS)
    await interaction.response.send_message(
        f"Here are the guns you can pick:\n{guns_list}")


@tree.command(name="select-gun", description="Select your gun")
@is_awake()
@app_commands.describe(gun="Gun to select")
async def select_gun_command(interaction: discord.Interaction, gun: str):
    if gun not in WEAPONS:
        await interaction.response.send_message(
            f"Invalid gun! Choose from: {', '.join(WEAPONS)}")
        return
    user_selected_guns[interaction.user.id] = gun
    save_data()
    await interaction.response.send_message(
        f"{interaction.user.mention} selected **{gun}** as their gun!")


@tree.command(name="attack", description="Attack a user")
@is_awake()
@app_commands.describe(user="User to attack")
async def attack_command(interaction: discord.Interaction,
                         user: discord.Member):
    attacker = interaction.user
    victim = user
    if user_shields.get(victim.id):
        uses_left = user_shields[victim.id]
        if uses_left <= 1:
            user_shields.pop(victim.id)
        else:
            user_shields[victim.id] = uses_left - 1
        save_data()
        await interaction.response.send_message(
            f"🛡️ {victim.mention}'s **Shield** blocked the attack! Uses left: {user_shields.get(victim.id, 0)}"
        )
        return
    weapon = user_selected_guns.get(attacker.id, random.choice(WEAPONS))
    await interaction.response.send_message(
        f"💥 {attacker.mention} used {weapon} to attack {victim.mention}!")


@tree.command(name="say", description="Make Nessie say something")
@is_awake()
@app_commands.describe(message="Message Nessie will say")
async def say_command(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@tree.command(name="debug", description="Show last error trace")
@is_awake()
async def debug_command(interaction: discord.Interaction):
    global last_error_trace
    if last_error_trace:
        await interaction.response.send_message(
            f"Last error trace:\n```py\n{last_error_trace}\n```")
    else:
        await interaction.response.send_message("✅ No errors recorded.")


@tree.command(name="steal", description="Steal money from a user")
@is_awake()
@app_commands.describe(user="User to steal from")
async def steal_command(interaction: discord.Interaction,
                        user: discord.Member):
    if user.id == interaction.user.id:
        await interaction.response.send_message(
            "You can't steal from yourself!")
        return
    now = time.time()
    last_steal = last_steal_times.get(interaction.user.id, 0)
    if now - last_steal < 600:
        await interaction.response.send_message(
            "You can only steal once every 10 minutes. Please wait.")
        return
    if user_shields.get(user.id):
        uses_left = user_shields[user.id]
        if uses_left <= 1:
            user_shields.pop(user.id)
        else:
            user_shields[user.id] = uses_left - 1
        save_data()
        await interaction.response.send_message(
            f"🛡️ {user.mention}'s **Shield** blocked your stealing attempt! Uses left: {user_shields.get(user.id, 0)}"
        )
        return
    target_balance = user_balances.get(user.id, 0)
    if target_balance < 1000:
        await interaction.response.send_message(
            "Target user has insufficient funds to steal from.")
        return
    steal_amount = random.randint(1000, min(500000, target_balance))
    user_balances[user.id] = target_balance - steal_amount
    user_balances[interaction.user.id] = user_balances.get(
        interaction.user.id, 0) + steal_amount
    last_steal_times[interaction.user.id] = now
    recent_thefts.append({
        "thief": interaction.user.id,
        "victim": user.id,
        "amount": steal_amount,
        "time": now
    })
    save_data()
    await interaction.response.send_message(
        f"You successfully stole ${steal_amount:,} from {user.mention}!")


@tree.command(name="bank", description="Check your bank balance")
@is_awake()
async def bank_command(interaction: discord.Interaction):
    balance = user_balances.get(interaction.user.id, 0)
    await interaction.response.send_message(
        f"**Bank** 🏦\n    • You have ${balance:,} 💵 in your bank account.")


@tree.command(name="daily-reward",
              description="Claim daily reward ($1,000,000 every 24h ⌛)")
@is_awake()
async def daily_reward_command(interaction: discord.Interaction):
    now = time.time()
    last_claim = last_daily_reward_times.get(interaction.user.id, 0)
    if now - last_claim < 86400:
        await interaction.response.send_message(
            "❎ You already claimed your daily reward. Come back later!")
        return
    user_balances[interaction.user.id] = user_balances.get(
        interaction.user.id, 0) + 1_000_000
    last_daily_reward_times[interaction.user.id] = now
    save_data()
    await interaction.response.send_message(
        "You claimed your daily reward of $1,000,000 💵!")


@tree.command(name="give-money", description="Get $500,000 every 5 minutes")
@is_awake()
async def give_money_command(interaction: discord.Interaction):
    now = time.time()
    last_claim = last_give_money_times.get(interaction.user.id, 0)
    if now - last_claim < 300:
        remaining_time = 300 - (now - last_claim)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        await interaction.response.send_message(
            f"❎ You can only claim this every 5 minutes. Please wait {minutes}m {seconds}s."
        )
        return
    user_balances[interaction.user.id] = user_balances.get(
        interaction.user.id, 0) + 500_000
    last_give_money_times[interaction.user.id] = now
    save_data()
    await interaction.response.send_message("You got $500,000! 💵")


@tree.command(name="give", description="Give money to another user")
@is_awake()
@app_commands.describe(user="User to give money to", amount="Amount to give")
async def give_command(interaction: discord.Interaction, user: discord.Member,
                       amount: int):
    if amount <= 0:
        await interaction.response.send_message("❎ Amount must be positive.")
        return
    sender_balance = user_balances.get(interaction.user.id, 0)
    if sender_balance < amount:
        await interaction.response.send_message("❎ Insufficient funds.")
        return
    user_balances[interaction.user.id] = sender_balance - amount
    user_balances[user.id] = user_balances.get(user.id, 0) + amount
    save_data()
    await interaction.response.send_message(
        f"You gave ${amount:,} to {user.mention}. 💵")


@tree.command(name="ping", description="Check bot latency")
@is_awake()
async def ping_command(interaction: discord.Interaction):
    latency = client.latency * 1000
    await interaction.response.send_message(f"Pong! Latency: {latency:.2f} ms")


@tree.command(name="shop", description="Show shop items")
@is_awake()
async def shop_command(interaction: discord.Interaction):
    shop_msg = "**Shop** 🏛️\n\n"
    for item, price in SHOP_ITEMS.items():
        shop_msg += f"- {item} { '🎁' if item == 'Mystery Box' else '🛡️' if item == 'Shield' else ''} ~ ${price:,}\n"
    await interaction.response.send_message(shop_msg)


@tree.command(name="buy", description="Buy an item from the shop")
@is_awake()
@app_commands.describe(item="Item to buy")
async def buy_command(interaction: discord.Interaction, item: str):
    item = item.strip()
    if item not in SHOP_ITEMS:
        await interaction.response.send_message("Item not found in shop.")
        return
    price = SHOP_ITEMS[item]
    balance = user_balances.get(interaction.user.id, 0)
    if balance < price:
        await interaction.response.send_message("Insufficient funds.")
        return
    user_balances[interaction.user.id] = balance - price

    # Add item to inventory
    inventory = user_inventories.get(interaction.user.id, [])
    inventory.append(item)
    user_inventories[interaction.user.id] = inventory
    save_data()

    await interaction.response.send_message(
        f"💵 You bought a **{item}** for ${price:,}!")


@tree.command(name="use", description="Use an item from your inventory")
@is_awake()
@app_commands.describe(item="Item to use")
async def use_command(interaction: discord.Interaction, item: str):
    item = item.strip()
    inventory = user_inventories.get(interaction.user.id, [])
    if item not in inventory:
        await interaction.response.send_message(
            f"❎ You don't have a {item} in your inventory.")
        return

    if item == "Mystery Box":
        reward = get_mystery_box_reward()
        user_balances[interaction.user.id] = user_balances.get(
            interaction.user.id, 0) + reward
        inventory.remove(item)
        await interaction.response.send_message(
            f"🎉 You opened a Mystery Box and won ${reward:,}!")
    elif item == "Shield":
        user_shields[interaction.user.id] = user_shields.get(
            interaction.user.id, 0) + 3
        inventory.remove(item)
        await interaction.response.send_message(
            "🛡️ You activated a Shield with 3 uses!")
    else:
        await interaction.response.send_message(
            f"You used {item}, but nothing happened.")
        return

    user_inventories[interaction.user.id] = inventory
    save_data()


def get_mystery_box_reward():
    # Weighted chances:
    # 40% chance: 300,000
    # 25% chance: 500,000
    # 20% chance: 700,000
    # 10% chance: 1,000,000
    # 5% chance: 10,000,000
    roll = random.random()
    if roll < 0.40:
        return 300_000
    elif roll < 0.65:  # 0.40 + 0.25
        return 500_000
    elif roll < 0.85:  # 0.65 + 0.20
        return 700_000
    elif roll < 0.95:  # 0.85 + 0.10
        return 1_000_000
    else:  # last 5%
        return 10_000_000


@tree.command(name="inventory", description="Show your inventory")
@is_awake()
async def inventory_command(interaction: discord.Interaction):
    inventory = user_inventories.get(interaction.user.id, [])
    if not inventory:
        await interaction.response.send_message(
            "**INVENTORY** 🎒\n \n  **Your inventory** ***is empty.***")
        return
    counts = {}
    for item in inventory:
        counts[item] = counts.get(item, 0) + 1
    inv_msg = "\n".join(f"{item} x{count}" for item, count in counts.items())
    await interaction.response.send_message(f"Your inventory:\n{inv_msg}")


@tree.command(name="version", description="Version of Nessie")
@is_awake()
async def version_command(interaction: discord.Interaction):
    await interaction.response.send_message("**Version** 🌐\n   • 1.99.96")


@tree.command(name="roblox",
              description="Get the links of some cool roblox games")
async def roblox_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Games** 🎮\n   • https://www.roblox.com/games/126884695634066/Grow-a-Garden **-Grow a Garden**\n   • https://www.roblox.com/games/16732694052/TRADING-Fisch **-Fisch**\n   • https://www.roblox.com/games/17625359962/RIVALS **-Rivals**\n   • https://www.roblox.com/games/10449761463/The-Strongest-Battlegrounds **-The Strongest Battlegrounds**\n   • https://www.roblox.com/games/116495829188952/Dead-Rails-Alpha **-Dead Rails**\n   • https://www.roblox.com/games/20321167/Pilot-Training-Flight-Simulator **-Pilot Training Flight Simulator ~PTFS~**"
    )


# === ERROR HANDLING ===
@client.event
async def on_command_error(ctx, error):
    global last_error_trace
    last_error_trace = traceback.format_exc()
    print(f"Error: {last_error_trace}")
    try:
        await ctx.send("An error occurred. Use /debug to see more info.")
    except Exception:
        pass


@tree.command(name="eat", description="Eat something")
@is_awake()
async def eat_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**You ate an apple!**\n   • 🍏\n \n ***Sneak & Peaks***\n   • **An apple a day keeps the doctor away!**"
    )


@tree.command(name="sleep", description="Go to sleep and disable commands")
async def sleep(interaction: discord.Interaction):
    sleeping_users.add(interaction.user.id)
    await interaction.response.send_message(
        "**You fell asleep...**\n   - Use /wake-up to wake up. 💤")


@tree.command(name="drink", description="Take a risky drink")
@is_awake()
async def drink(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    chance = random.random()  # Float between 0.0 and 1.0

    if chance < 0.9:  # 90% chance to lose money
        balance = bank.get(user_id, 0)
        if balance < 100000:
            await interaction.response.send_message(
                "❎ You don't have enough money to risk losing $100,000 💵!")
            return

        bank[user_id] = balance - 100000
        save_data()
        await interaction.response.send_message(
            "💸 You drank something awful and lost $100,000!")
    else:  # 10% chance to fall asleep
        sleeping_users.add(interaction.user.id)
        forced_sleep_until[interaction.user.id] = time.time() + 60  # 1 minutes
        await interaction.response.send_message(
            "🥴 You feel dizzy and fall asleep! **You can't wake up for** ***1 minute.***\n    Never drink again! 🤕"
        )


@tree.command(name="wake-up", description="Wake up and enable commands")
async def wake_up(interaction: discord.Interaction):
    user_id = interaction.user.id
    now = time.time()

    # Check forced sleep status
    if user_id in forced_sleep_until:
        if now < forced_sleep_until[user_id]:
            remaining = int(forced_sleep_until[user_id] - now)
            await interaction.response.send_message(
                f"😴 You are too tired to wake up! Try again in {remaining} seconds."
            )
            return
        else:
            forced_sleep_until.pop(user_id)

    sleeping_users.discard(user_id)
    await interaction.response.send_message(
        "**🌅 You woke up!**\n   - You can use commands again! 🛏")


@tree.command(name="see", description="See something cool.")
async def see(interaction: discord.Interaction):
    # Use known good image links from Discord-friendly sources
    options = [
        ("Eiffel Tower",
         "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/960px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg"
         ),
        ("Owner of Roblox",
         "https://pbs.twimg.com/profile_images/1668347239419502593/KIRVs0LD_400x400.jpg"
         ),  # Replace with better image if needed
        ("Nuclear Explosion",
         "https://www.thebrighterside.news/uploads/2024/07/nuclear-explosion-1.webp?format=webp&optimize=high&precrop=4%3A3%2Csmart"
         )
    ]

    outcome = random.choices(options, weights=[20, 30, 50], k=1)[0]
    label, image_url = outcome

    embed = discord.Embed(title=f"You see... {label}!",
                          color=discord.Color.orange())
    embed.set_image(url=image_url)

    await interaction.response.send_message(embed=embed)


@tree.command(name="think", description="Just take a brake and think, man...")
@is_awake()
async def think_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**THINKING...**\n   - You took a brake and thought about life. 🤔\n   - You are now ready to take action! 💪 \n    - Hmmm... What if you just... **SLEEP?** 😴\n     - Use /sleep to sleep. 🛌\n      - Use /wake-up to wake up. 🛏️\n       - Use /drink to drink something. 🍹\n        - Use /eat to eat something. 🍎\n         - Use /see to see something. 👀\n          - Use /roblox to play roblox. 🎮"
    )


@tree.command(name="do", description="Do something")
@is_awake()
async def do_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**DOING...**\n   - You did something. 💪\n     -You are now ready to take action! 💪"
    )


@tree.command(name="tar-get", description="Begin target acquisition protocol")
async def tar_get_command(interaction: discord.Interaction):
    await interaction.response.send_modal(PasswordModal())


@tree.command(name="ha-music", description="Codding Music")
@is_awake()
async def ha_music_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Codding Music** \n https://www.youtube.com/watch?v=AF8LSurfct4&list=PLEM4vOSCprStzppPemEYAF6ZEUrQYj5N5 \n**Duration: 1:54:10**"
    )

@tree.command(name="binary-code", description="Get The binary code of the ...")
@is_awake()
async def binary_code_command(interaction: discord.Interaction):
    await interaction.response.send_message("01001101 01101111 01100100 01100001 01101100 00100000 00110001 00101110 00100000 00101101 01010011 01100101 01100011 01110010 01100101 01110100 00100000 01010000 01100001 01110011 01110011 01110111 01101111 01110010 01100100 00101101 00001101 00001010 01010000 01100001 01110011 01110011 01110111 01101111 01110010 01100100 00111010 00100000 01001110 01000101 01010011 01010011 01100101 01100011 01110101 01110010 01101001 01110100 01111001 00100000 00001101 00001010 00001101 00001010 01001101 01101111 01100100 01100001 01101100 00100000 00110010 00101110 00100000 00101101 01001100 01101111 01100111 01101001 01101110 00100000 01010011 01111001 01110011 01110100 01100101 01101101 00101101 00001101 00001010 01010101 01110011 01100101 01110010 01101110 01100001 01101101 01100101 00111010 00100000 01001110 01100101 01110011 01110011 01101001 01100101 00001101 00001010 01010000 01100001 01110011 01110011 01110111 01101111 01110010 01100100 00111010 00100000 01001110 01100101 01110011 01110011 01101001 01100101 00110111 00110101 00110001 00110001")

@tree.command(name="play-music", description="Play music in a voice channel")
async def play_music(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
        return

    # Get voice channels the bot has permission to connect to
    vcs = [
        vc for vc in interaction.guild.voice_channels
        if vc.permissions_for(interaction.guild.me).connect
    ]

    if not vcs:
        await interaction.response.send_message("❌ I can't see or connect to any voice channels.", ephemeral=True)
        return

    # Create dropdown options
    options = [
        discord.SelectOption(label=vc.name, value=str(vc.id))
        for vc in vcs
    ]

    # Voice channel selector dropdown
    class VCSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="🎙️ Choose a voice channel", options=options)

        async def callback(self, select_interaction: discord.Interaction):
            vc_selection[select_interaction.user.id] = int(self.values[0])
            await select_interaction.response.send_modal(MusicURLModal(user_id=select_interaction.user.id))

    # View with the dropdown
    class VCView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(VCSelect())

    await interaction.response.send_message(
        "🎧 Please select a voice channel:", view=VCView(), ephemeral=True
    )

@tree.command(name="lottery", description="Buy a free lottery ticket")
async def lottery_command(interaction: discord.Interaction):
    global lottery_active, lottery_tickets

    if interaction.guild is None:
        await interaction.response.send_message("❌ This command only works in servers.", ephemeral=False)
        return

    if not lottery_active:
        await interaction.response.send_message("❌ No active lottery right now.",e)
        return

    user_id = interaction.user.id
    if user_id in lottery_tickets:
        await interaction.response.send_message(f"⚠️ You already have a ticket: #{lottery_tickets[user_id]}.",)
        return

    existing = set(lottery_tickets.values())
    while True:
        number = random.randint(1000, 9999)
        if number not in existing:
            break

    lottery_tickets[user_id] = number
    await interaction.response.send_message(f"🎟️ You got ticket number #{number}. Good luck!", ephemeral=True)

@tree.command(name="start-lottery", description="Start a 24h lottery (only in a specific channel)")
async def start_lottery_command(interaction: discord.Interaction):
    global lottery_active, lottery_end_time, lottery_tickets

    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        await interaction.followup.send("❌ This command only works in servers.",)
        return

    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.followup.send(
            f"❌ You can only start the lottery in <#{ALLOWED_CHANNEL_ID}>.",
        )
        return

    if lottery_active:
        await interaction.followup.send("⚠️ Lottery already active.", ephemeral=False)
        return

    lottery_active = True
    lottery_tickets = {}
    lottery_end_time = datetime.utcnow() + timedelta(days=1)

    if not check_lottery_end.is_running():
        check_lottery_end.start()

    view = ContinueButtonView()

    await interaction.followup.send(
        "Lottery Started! 💵\nPress Continue to get your ticket! 🎟️",
        view=view
    )

@tree.command(name="cancel-lottery", description="Cancel the active lottery")
async def cancel_lottery_command(interaction: discord.Interaction):
    global lottery_active, lottery_tickets, lottery_end_time

    await interaction.response.defer(ephemeral=False)

    if interaction.guild is None:
        await interaction.followup.send("❌ This command only works in servers.",)
        return

    if not lottery_active:
        await interaction.followup.send("ℹ️ No active lottery to cancel.",)
        return

    lottery_active = False
    lottery_tickets = {}
    lottery_end_time = None

    if check_lottery_end.is_running():
        check_lottery_end.stop()

    await interaction.followup.send("🛑 Lottery cancelled and all tickets cleared.")

    channel = get_default_channel()
    if channel:
        await channel.send("🛑 The lottery has been cancelled.")

@tasks.loop(seconds=60)
async def check_lottery_end():
    global lottery_active, lottery_end_time, lottery_tickets

    if not lottery_active:
        check_lottery_end.stop()
        return

    if datetime.utcnow() >= lottery_end_time:
        lottery_active = False
        check_lottery_end.stop()

        channel = get_default_channel()

        if not lottery_tickets:
            if channel:
                await channel.send("📭 The lottery ended but no one entered.")
            return

        winner_id = random.choice(list(lottery_tickets.keys()))
        winning_number = lottery_tickets[winner_id]
        prize = 500_000_000  # 500 million dollars

        user_balances[winner_id] = user_balances.get(winner_id, 0) + prize
        # save_data() if you use persistent storage

        if channel:
            try:
                guild = channel.guild
                user = await guild.fetch_member(winner_id)
                winner_mention = user.mention
            except:
                winner_mention = f"<@{winner_id}>"

            await channel.send(
                f"🏆 The lottery has ended!\n"
                f"🎟️ Winning ticket: **#{winning_number}**\n"
                f"🎉 Congratulations {winner_mention}, you won **${prize:,}**!"
            )


# === RUN ===
keep_alive()
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("Error: DISCORD_TOKEN environment variable not found!")
else:
    client.run(TOKEN)