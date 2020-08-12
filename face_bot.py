from discord.ext.commands import Bot
import random
import asyncio
from random import sample
import datetime
import time
import discord
import mysql.connector as mysql
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from fake_useragent import UserAgent
import pickle
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import csv
import FACE

PREFIX = 'm '
token='NzQyODgwODEyOTYxMjM1MTA1.XzMjqw.SamNiyezNdCrzRzTQXh2h5SYsfE'
client = Bot(command_prefix=PREFIX)

async def is_owner(ctx):
    return ctx.author.id == 435504471343235072

@client.command (name='shutdown')
async def kill(ctx):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728:
        await ctx.message.delete()
        await ctx.channel.send('shutting down...')
        sys.exit()
@client.command (name='help')
async def help(ctx):
    embed=discord.Embed(title="Help", description="List of commands", color=0x00ff00)
    embed.add_field(name="m instructions", value="Provides an example of how to use the bot.", inline=False)
    embed.add_field(name="m cats", value="")
    await ctx.channel.send(embed=Embed)

    #copy mafia embed
@client.command (name='instructions')
async def instructions(ctx):
    await ctx.channel.send('Use the command `m card *category* *term*`, e.g. `m card sci proton`. After about 15 seconds, the bot will send a file that you can download and import into anki!')
@client.command (name='cats')
async def cats(ctx):
    await ctx.channel.send('`sci`, `fa`,`hist`,`geo`,`lit`,`ss`,`ce`,`myth`,`religion`,`trash`')
@client.command (name='card')
async def card(ctx,category = None,*term = None):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728 or ctx.guild.id == 634580485951193089:
        if category = None or term = None:
            await ctx.channel.send('You used the wrong format! Use the command `m card *category* *term*`, e.g. `m card sci proton`')#i need access to the other part plz
        term = ' '.join(term)
        await ctx.channel.send('Beginning the carding process...')
        try:
            full_path = await FACE.get_csv(term,category)
        except:
            await ctx.channel.send('There was a problem! Please try again.')
            return
        if full_path == None:
            await ctx.channel.send('That is not a valid category!')
            return
        with open(full_path, 'rb') as fp:
            await ctx.channel.send(file=discord.File(fp, f'{term} (click to download).csv'))
        await asyncio.sleep(7)
        os.remove(full_path)
    else:
        await ctx.channel.send('Sorry, this command is reserved. :peach:')
@client.command (name='info',aliases=['details'])
async def info(ctx):
    embed = discord.Embed (
    title='The Cataclysm:',
    colour=	0x7d99ff,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='The Mafia Inc.')
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/626811419815444490/631882087280017428/silhouette-3073924_960_720.png?width=300&height=600')
    embed.add_field(name='Creators of this bot:', value =f'B3nj1#7587/<@{str(435504471343235072)}> and Shozen#5061/<@{483405210274889728}>', inline=True)
    embed.add_field(name='Programming language:', value ='Python 3.6.3', inline=True)
    embed.add_field(name='Library:', value ='Discord python rewrite branch (v1.4)', inline=True)
    await ctx.channel.send(embed=embed)
@client.event
async def on_message(ctx):# we do not want the bot to reply to itself
    if ctx.author == client.user:
        return
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    # if ctx.author.id==248640104606859264:
    #     await ctx.channel.send(ctx.author.mention+' STOP') KEVIN STOP
    await client.process_commands(ctx)

#start up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
client.run(token)
