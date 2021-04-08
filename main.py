import asyncio
import json
import os

import discord
from dotenv import load_dotenv
from notion.client import NotionClient

#Discord init
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#Notion init
NTOKEN = os.getenv('NOTION_TOKEN')
NCALENDAR = os.getenv('NOTION_CALENDAR')
nclient = NotionClient(token_v2=NTOKEN)

tablazat = nclient.get_collection_view(NCALENDAR)


server=0
client = discord.Client()

def getEvents(table):
    return table.collection.get_rows()

def saveEvents(events):
    with open('events.json', 'w+') as f:
        f.write(json.dumps(events))

def loadEvents():
    with open('events.json', 'r') as f:
        return json.loads(f.read())

def formatEvent(event):
    pass

events=loadEvents()

async def my_background_task():
    while True:
        await asyncio.sleep(3)
        await client.wait_until_ready()
        if server:
            newEvents=getEvents(tablazat)
            for event in newEvents:
                if event.Reset_send:
                    try:
                        events.remove(event.id)
                        saveEvents(events)
                    except:
                        pass
                    event.Reset_send=False
                    event.Send_reminder=False

                if (event.id not in events) and event.Send_reminder and event.date:
                    for tag in event.tags:
                        try:
                            channel = discord.utils.get(server.text_channels, name=tag)
                            print("Új event!", event)
                            embed=discord.Embed(color=0xcd2323)
                            embed.set_author(name="📅", url=("https://www.notion.so/" + str(event.id).replace("-", "")))
                            embed.add_field(name=event.title, value=event.date.start.strftime("%Y. %m. %d.\n%H:%M"), inline=True)
                            embed.set_footer(text=', '.join(map(str,event.tags)))
                            await channel.send(embed=embed)
                            events.append(event.id)
                            saveEvents(events)
                        except:
                            pass




@client.event
async def on_ready():
    global server
    for guild in client.guilds:
        if guild.name == GUILD:
            server=guild

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


client.loop.create_task(my_background_task())
client.run(TOKEN)


