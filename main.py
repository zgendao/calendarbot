import asyncio
import json
import os
from datetime import datetime

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
NBLOCK = os.getenv('NOTION_BLOCK')
nclient = NotionClient(token_v2=NTOKEN)

block=nclient.get_block(NBLOCK)
for child in block.children:
    try:
        if child.title=='Meetings':
            break
    except:
        pass

tablazat = nclient.get_collection_view(NCALENDAR)


server=0
client = discord.Client()

def getEvents(table):
    return table.collection.get_rows()

async def reminder(date, event):
    seconds=(date-datetime.now()).total_seconds()-600
    if seconds>0:
        print("New reminder set!")
        await asyncio.sleep(seconds)
        for tag in event.Channels:
            try:
                channel = discord.utils.get(server.text_channels, name=tag)
                print("Reminder!", event)
                embed=discord.Embed(color=0xcd2323)
                embed.set_author(name="📅", url=("https://www.notion.so/" + str(event.id).replace("-", "")))
                embed.add_field(name=event.title, value="In 10 minutes", inline=True)
                embed.set_footer(text=', '.join(map(str,event.Channels)))
                await channel.send(embed=embed)
            except:
                pass
    else:
        pass

async def my_background_task():
    while True:
        await asyncio.sleep(3)
        await client.wait_until_ready()
        if server:
            newEvents=getEvents(tablazat)
            for event in newEvents:
                if  event.Notification and event.date:
                    for tag in event.Channels:
                        try:
                            channel = discord.utils.get(server.text_channels, name=tag)
                            print("Új event!", event)
                            embed=discord.Embed(color=0xcd2323)
                            embed.set_author(name="📅", url=("https://www.notion.so/" + str(event.id).replace("-", "")))
                            embed.add_field(name=event.title, value=event.date.start.strftime("%Y. %m. %d.\n%H:%M"), inline=True)
                            embed.set_footer(text=', '.join(map(str,event.Channels)))
                            event.Notification=False
                            await channel.send(embed=embed)
                        except:
                            pass
                if event.Reminder:
                    asyncio.get_event_loop().create_task(reminder(event.date.start, event))
                    event.Reminder=False




@client.event
async def on_ready():
    global server
    for guild in client.guilds:
        if str(guild.name) == GUILD:
            server=guild
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{server.name}(id: {server.id})'
    )


client.loop.create_task(my_background_task())
client.run(TOKEN)


