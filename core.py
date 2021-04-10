import asyncio
import datetime

import discord
import nest_asyncio
from dateutil import tz
from discord.ext import commands

from utils.automation import scheduler
from utils.core import bot

nest_asyncio.apply()


@bot.client.event
async def on_connect() -> None:
    '''event handler triggered when the bot is connected to Discord. Logs this information
    '''
    pass


@bot.client.command()
async def ping(ctx: commands.Context):
    msg = f'Pong! {int(bot.client.latency * 1000)} ms'
    await ctx.send(msg)


@bot.client.before_invoke
async def typing(ctx: commands.Context):
    await ctx.trigger_typing()


async def event_update(channel_id: int, msg_id: int):
    try:
        channel = await bot.client.fetch_channel(channel_id)
        msg: discord.Message = await channel.fetch_message(msg_id)
    except discord.errors.Forbidden:
        scheduler.remove_job(f"event_update-{msg.id}")
        return
    embed: discord.Embed = msg.embeds[0]
    options = {"\u2705": 'Yes ' + "\u2705",
               "\u2754": 'Maybe ' + "\u2754",
               "\u274C": 'No ' + "\u274C"}
    mapping = {s: [] for s in options}
    end = False
    for r in msg.reactions:
        if r.emoji in options:
            async for user in r.users():
                if not user.bot:
                    mapping[str(r.emoji)].append(user.display_name)
    updated_embed = discord.Embed(title=embed.title,
                                  description=embed.description,
                                  color=discord.Color.dark_gold())
    updated_embed.add_field(name=embed.fields[0].name, value=embed.fields[0].value, inline=embed.fields[0].inline)
    for m in mapping:
        users = sorted(mapping[m], key=lambda x: x)
        if users == "" or users is None or users == []:
            users = ['‎']
        updated_embed.add_field(name=f"{options[m]}", value="\n".join(users), inline=True)
    await msg.edit(embed=updated_embed)
    start: datetime.datetime = datetime.datetime.strptime(embed.fields[0].value, "%d.%m.%Y %I:%M %p %Z")
    from_zone = tz.tzutc()
    start = start.replace(tzinfo=from_zone)
    if start - datetime.timedelta(seconds=20) < datetime.datetime.now(from_zone):
        scheduler.remove_job(f"event_update-{msg.id}")
        await msg.clear_reactions()


@bot.client.command(name='create')
async def create(ctx: commands.Context, title: str, description: str, date: str):
    """Create a new embed for an event and add the reactions to vote for
    Format of the date should be DD.MM.YYYYTHH:MM"""
    try:
        start: datetime.datetime = datetime.datetime.strptime(date, "%d.%m.%YT%H:%M")
    except Exception as e:
        embed = discord.Embed(
            title=f"Invalid date. Please use the format ``DD.MM.YYYYTHH:MM``.", description=str(e),
            color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    date = start.replace(tzinfo=from_zone)
    start = start.replace(tzinfo=from_zone)
    start = start.astimezone(to_zone)
    embed = discord.Embed(title=title,
                          description=description,
                          color=discord.Color.dark_gold())
    embed.add_field(name="Date",
                    value=date.strftime("%d.%m.%Y") + "   `" + date.strftime("%I:%M") + "` " + date.strftime("%p %Z"),
                    inline=False)
    embed.add_field(name='Yes ' + "\u2705", value='‎', inline=True)
    embed.add_field(name='Maybe ' + "\u2754", value='‎', inline=True)
    embed.add_field(name='No ' + "\u274C", value='‎', inline=True)
    embed.set_footer(text="This bot is coded by Doluk#9534")
    msg = await ctx.send(embed=embed)
    EVENT_EMOJI = ["\u2705", "\u2754", "\u274C"]
    for emoji in EVENT_EMOJI:
        # Add all the applicable emoji to the message
        await msg.add_reaction(emoji)
    scheduler.add_job(event_update, 'interval', seconds=20,
                      end_date=str(start),
                      args=[msg.channel.id, msg.id],
                      coalesce=True, id=f"event_update-{msg.id}", misfire_grace_time=15,
                      replace_existing=True)


###############################################################################
# Start the bot
###############################################################################

asyncio.get_event_loop().run_until_complete(bot.client.run(bot.config.discord.token))
