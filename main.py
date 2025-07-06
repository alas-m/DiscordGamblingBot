# A simple gambling bot for discord (no payments). Created by: alas-m
# Github: https://github.com/alas-m

import discord
import asyncio
from discord.ext import commands
import random
import datetime

from functions import Database

db = Database("database.db")

TOKEN = "YOUR_DISCORD_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class NoOtherException(Exception):
    def __init__(self, message="Not enough balance"):
        self.message = message
        super().__init__(self.message)

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="info")
async def userinfo(ctx):

    if db.user_exists(ctx.author.id) == False:
        db.add_user(ctx.author.id)

    try:
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        user = replied_message.author

        try:
            with open(f"stake_log/{user.id}.txt", 'r') as f:
                stake_log = f.read().split("\n")[-5:][::-1][1:]
            final_log = ""
            for i in stake_log:
                final_log += f"{i}\n"
        except:
            final_log = "`Empty`"

        balance = db.mybal(user.id)
        embed = discord.Embed(title="User Information", color=0xf09890)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Balance", value=f"${balance}", inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        if isinstance(user, discord.Member):
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]), inline=True)

        embed.add_field(name="\nStakes Log", value=final_log, inline=True)

        await ctx.send(embed=embed)

    except:

        user = ctx.author

        try:
            with open(f"stake_log/{user.id}.txt", 'r') as f:
                stake_log = f.read().split("\n")[-5:][::-1][1:]
            final_log = ""
            for i in stake_log:
                final_log += f"{i}\n"
        except:
            final_log = "`Empty`"

        balance = db.mybal(user.id)
        embed = discord.Embed(title="User Information", color=0xf09890)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Balance", value=f"${balance}", inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        if isinstance(user, discord.Member):
            embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]), inline=True)

        embed.add_field(name="\nStakes Log", value=final_log, inline=True)

        await ctx.send(embed=embed)

@bot.command(name="dice")
async def dice(ctx, *args):

    if db.user_exists(ctx.author.id) == False:
        db.add_user(ctx.author.id)

    if len(args) == 2:
        try:
            balance = db.mybal(ctx.author.id)
            price = int(args[0])
            quantity = int(args[1])

            if balance >= price * quantity:

                if quantity < 1:
                    await ctx.send("Error: Quantity must be at least 1.")
                    return

                single_dice_multipliers = {1: 0.05, 2: 0.1, 3: 0.5, 4:1, 5: 1.5, 6: 2}

                rolls = [random.randint(1, 6) for _ in range(quantity)]
                embed = discord.Embed(title="Dice Game", description=f"Dice rolls: {rolls}", color=0x4854b0)

                if quantity == 1:
                    multiplier = single_dice_multipliers[rolls[0]]
                    winnings = price * multiplier
                    embed = embed.add_field(
                        name=f"Roll: {rolls[0]} with multiplier {multiplier}.",
                        value = f"Total winnings: {winnings:.2f}"
                    )

                    if price * quantity > winnings:
                        res = winnings - (price * quantity)
                        status = f"Loss by ${res}"

                        embed = embed.add_field(
                        name=f"Result:",
                        value = status
                        )   

                    else:
                        res = winnings - (price * quantity)
                        status = f"Win by ${res}"

                        embed = embed.add_field(
                        name=f"Result:",
                        value = status
                        )

                    await ctx.send(embed=embed)

                    db.update_bal(winnings - (price * quantity), ctx.author.id)

                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
                    with open(f"stake_log/{ctx.author.id}.txt", "a") as file:
                        file.write(f"`{timestamp}`: `{status} in Dice Game`\n")

                else:
                    if all(roll == rolls[0] for roll in rolls):
                        multiplier = 2
                        winnings = price * multiplier
                        embed = embed.add_field(
                            name=f"All dice show the same side.",
                            value =  f"Multiplier: {multiplier}x. Total winnings: {winnings:.2f}"
                        )

                        if price * quantity > winnings:
                            res = winnings - (price * quantity)
                            status = f"Loss by ${res}"

                            embed = embed.add_field(
                            name=f"Result:",
                            value = status
                            )   

                        else:
                            res = winnings - (price * quantity)
                            status = f"Win by ${res}"

                            embed = embed.add_field(
                            name=f"Result:",
                            value = status
                            )
                        await ctx.send(embed=embed)
                        db.update_bal(winnings - (price * quantity), ctx.author.id)

                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
                        with open(f"stake_log/{ctx.author.id}.txt", "a") as file:
                            file.write(f"`{timestamp}`: `{status} in Dice Game`\n")

                    else:
                        side_counts = {side: rolls.count(side) for side in set(rolls)}
                        base_winnings = 0
                        detailed_multiplier_info = []

                        for side, count in side_counts.items():
                            individual_multiplier = single_dice_multipliers[side]
                            side_winnings = price * individual_multiplier * count
                            base_winnings += side_winnings
                            detailed_multiplier_info.append(f"Side {side}: {side_winnings:.2f}")

                        duplicate_count = max(side_counts.values())
                        if duplicate_count > 1:
                            additional_multiplier = 1 + (duplicate_count - 1) * 0.1
                        else:
                            additional_multiplier = 1.0

                        total_winnings = base_winnings * additional_multiplier
                        multiplier_details = "\n".join(detailed_multiplier_info)

                        embed.add_field(name="Detailed Winnings", value=multiplier_details, inline=False)
                        embed.add_field(name="Base Winnings", value=f"{base_winnings:.2f}", inline=True)
                        if duplicate_count > 1:
                            embed.add_field(name="Additional Multiplier", value=f"{additional_multiplier:.2f}", inline=True)
                        embed.add_field(name="Total Winnings", value=f"{total_winnings:.2f}", inline=True)
                        
                        if price * quantity > total_winnings:
                            res = total_winnings - (price * quantity)
                            status = f"Loss by ${res}"

                            embed = embed.add_field(
                            name=f"Result:",
                            value = status
                            )   

                        else:
                            res = total_winnings - (price * quantity)
                            status = f"Win by ${res}"

                            embed = embed.add_field(
                            name=f"Result:",
                            value = status
                            )

                        await ctx.send(embed=embed)
                        db.update_bal(total_winnings - (price * quantity), ctx.author.id)

                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
                        with open(f"stake_log/{ctx.author.id}.txt", "a") as file:
                            file.write(f"`{timestamp}`: `{status} in Dice Game`\n")

            else:

                await ctx.send("Insufficient funds! Please replenish your balance using `!topup`")
                return

        except NoOtherException as e:
            await ctx.send(f"Error: {e.message}")

        except ValueError:
            await ctx.send("Error: Both arguments must be numbers.")

    else:
        await ctx.send("Please provide exactly 2 arguments for Dice game. Usage: `!dice <Price> <Quantity>`")

bot.run(TOKEN)