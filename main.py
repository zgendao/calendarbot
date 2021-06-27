import os
import time
from datetime import datetime, timedelta

import discord
from discord.embeds import Embed
from dotenv import load_dotenv
from notion_client import Client

#Discord init
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = os.getenv('DISCORD_GUILD')
discordServer = None
discordClient = discord.Client()

#Notion init
NOTION_CALENDAR = os.getenv('NOTION_CALENDAR')
notion = Client(auth=os.environ["NOTION_TOKEN"])

async def poll(message):
    for emoji in ('👍', '👎'):
        await message.add_reaction(emoji)

async def sendMessage(id, name, startDate, channels):
    embed=discord.Embed(color=0xcd2323)
    embed.set_author(name="📅", url=("https://www.notion.so/" + str(id).replace("-", "")))
    embed.add_field(name=name, value=startDate, inline=False)
    embed.add_field(name="Coming", value="-", inline=True)
    embed.add_field(name="Not Coming", value="-", inline=True)
    embed.set_footer(text=', '.join(map(str,channels)))

    for channelname in channels:
        channel = discord.utils.get(discordServer.text_channels, name=channelname)
        message = await channel.send(embed=embed)
        #await poll(message)



async def queryNotifications():
    results = notion.databases.query(**{"database_id": NOTION_CALENDAR, "filter" : {"property": "Notification", "checkbox": {"equals": True}}})["results"]
    for event in results:
        startingTime = datetime.fromisoformat(event["properties"]["Date"]["date"]["start"])
        timeBetween = startingTime.replace(tzinfo=None) - datetime.today()
        if timeBetween <= timedelta():
            notion.pages.update(event["id"], **{"properties": {'Notification': {"checkbox": False}}})
            continue
        channels = list(map(lambda x: x["name"], event["properties"]["Channels"]["multi_select"]))
        await sendMessage(event["id"], event["properties"]["Name"]["title"][0]["plain_text"] , startingTime.strftime("%Y. %m. %d.\n%H:%M"), channels)
        notion.pages.update(event["id"], **{"properties": {'Notification': {"checkbox": False}}})


async def queryReminders():
    results = notion.databases.query(**{"database_id": NOTION_CALENDAR, "filter" : {"property": "Reminder", "checkbox": {"equals": True}}})["results"]
    for event in results:
        startingTime = datetime.fromisoformat(event["properties"]["Date"]["date"]["start"])
        timeBetween = startingTime.replace(tzinfo=None) - datetime.today()
        if timeBetween <= timedelta():
            notion.pages.update(event["id"], **{"properties": {'Reminder': {"checkbox": False}}})
            continue
        if timeBetween <= timedelta(minutes=10):
            channels = list(map(lambda x: x["name"], event["properties"]["Channels"]["multi_select"]))
            await sendMessage(event["id"], event["properties"]["Name"]["title"][0]["plain_text"] , "In 10 minutes", channels)
            notion.pages.update(event["id"], **{"properties": {'Reminder': {"checkbox": False}}})


@discordClient.event
async def on_ready():
    global discordServer
    for guild in discordClient.guilds:
        if str(guild.name) == DISCORD_GUILD:
            discordServer=guild
            break
    
    if not discordServer:
        raise Exception("This Discord Server can't be found!")

    print(
        f'{discordClient.user} is connected to the following guild:\n'
        f'{discordServer.name}(id: {discordServer.id})'
    )
    discordClient.loop.create_task(mainLoop())

@discordClient.event
async def on_reaction_add(reaction, user):
    if str(user) != "Calendar bot#1720":
        if str(reaction) == "👍":
            for sent_embed in reaction.message.embeds:
                embed_dict=sent_embed.to_dict()
                users = embed_dict['fields'][1]['value']
                if users == '-':
                    users = str(user.name)
                else:
                    users = users + "\n" + str(user.name)
                embed_dict['fields'][1]['value']=users
                print("eljut")
                await reaction.message.edit(embed=Embed.from_dict(embed_dict))
        if str(reaction) == "👎":
            for sent_embed in reaction.message.embeds:
                embed_dict=sent_embed.to_dict()
                users = embed_dict['fields'][2]['value']
                if users == '-':
                    users = str(user.name)
                else:
                    users = users + "\n" + str(user.name)
                embed_dict['fields'][1]['value']=users
                print("eljut")
                await reaction.message.edit(embed=Embed.from_dict(embed_dict))


async def mainLoop():
    while True:
        try:
            await queryNotifications()
            await queryReminders()
        except:
            pass
        time.sleep(3)


discordClient.run(DISCORD_TOKEN)
