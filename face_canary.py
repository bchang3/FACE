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
import time
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import csv
import FACE
import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord.ext import commands, tasks
import matplotlib.pyplot as plt
from num2words import num2words
import math
import secrets
from PIL import Image
import pandas as pd
import requests
import json
PREFIX = ['c ','C ']
token='NzcwNzY5NDk5MzA1NjcyNzU0.X5iZCA.rrqAHZ_GzKtidTYf7S5Gj9NAn6U'
intents = discord.Intents.default()
intents.members = True
client = Bot(command_prefix=PREFIX,intents=intents)
client.remove_command('help')
async def add_count(id):
    None
in_pk = []
close_pk = []
in_tk = []
close_tk = []
carding = []

cat_embed = discord.Embed(
    title=f'CATEGORIES:',
    colour=	0xf7f7f7,
)
for abbrev,cat in FACE.first_cat_dict.items():
    cat_embed.add_field(name=cat.capitalize(),value=abbrev)

subcat_lookup = dict()
for cat in FACE.first_cat_dict.values():
    results = []
    set_subcats = []
    for abbreviation,sub_cat in FACE.first_subcat_dict.items():
        original = sub_cat
        sub_cat = sub_cat.casefold()
        if cat in sub_cat and sub_cat.find(cat) == 0:
            results.append((abbreviation,original))
            set_subcats.append(original)
    set_subcats = list(set(set_subcats))
    embed = discord.Embed(
        title=f'SUBCATEGORIES',
        colour=	0xf7f7f7,
    )
    for subcat in set_subcats:
        all_abbrev = []
        for abbrev,subcat2 in results:
            if subcat == subcat2:
                all_abbrev.append(abbrev)
        embed.add_field(name=subcat,value=', '.join(all_abbrev))
    subcat_lookup[cat] = embed
@tasks.loop(seconds=60)
async def update_premium():
    mydb,mycursor = mysql_connect() #user_id,server_id,premium
    mycursor.execute(f'SELECT * FROM premium_servers')
    member_ids = [x.id for x in patron_role.members]
    table = mycursor.fetchall()
    for row in table:
        if row[0] not in member_ids:
            mycursor.execute(f'DELETE FROM premium_servers WHERE user_id = {row[0]}')
    mydb.commit()
    in_table_ids = list(set([x[0] for x in table]))
    for id in member_ids:
        if id not in in_table_ids:
            for i in range(3):
                mycursor.execute(f'INSERT INTO premium_servers (user_id) VALUES ({id})')
            member = bot_guild.get_member(id)
            await member.send(
'''Hi! Thank you for deciding to support us! Below is some important information:
**---**  To activate your premium membership, use the command **m activate** in your chosen server.
**---**  It could take up to 10 minutes for your benefits to become available.
**---**  You can use `m activate` up to three times in three different servers.
**---** Keep in mind that premium carding features will not be available and server members will not be able to use the bot in their DMs if the server has more than **50 people**. ''')
    mydb.commit()
@tasks.loop(minutes=30)
async def update_trial():
    mydb,mycursor = mysql_connect()
    mycursor.execute(f'SELECT * FROM trial_premium')
    rows = mycursor.fetchall()
    for row in rows:
        if row[1] - int(time.time()) < 0:
            mycursor.execute(f'UPDATE trial_premium set used = {True} WHERE server_id = {row[0]}')
    mydb.commit()
def mysql_connect():
    mydb = mysql.connect(
      host="127.0.0.1",
      user="root",
      password="TheCataclysm91$(*",
      database="face_log"
    )
    mycursor = mydb.cursor(buffered=True)
    return mydb, mycursor
def is_owner(ctx):
    return ctx.author.id == 435504471343235072 or ctx.author.id == 483405210274889728
def has_num(s):
    return any(i.isdigit() for i in s)
async def premium(id,ctx):
    def pred(m):
        return m.author == ctx.author and m.channel==ctx.channel
    if id == 0:
        await ctx.send('Please send the id of a premium server that you are in to authorize your command.\nThe id can be found by right clicking on the server icon after enabling developer mode in `User settings` --> `Appearance` --> `Advanced` -> `Developer mode`.')
        try:
            msg = await client.wait_for('message',timeout=10,check=pred)
        except asyncio.TimeoutError:
            await ctx.send('You did not respond in time!')
            return False
        else:
            try:
                id = int(msg.content)
                authorized = client.get_guild(id)
                if len(authorized.members) > 50 and id != 634580485951193089:
                    await ctx.send('That server has more than 50 members! (DM usage is only allowed for premium servers with less than 50 members)')
                    return False
                elif ctx.author.id not in [member.id for member in authorized.members]:
                    await ctx.send('You are not in that server!')
                    return False
            except:
                await ctx.send('Server not found!')
                return False
    mydb,mycursor = mysql_connect()
    mycursor.execute(f'SELECT timeout FROM trial_premium WHERE server_id = {id}')
    row = mycursor.fetchone()
    if row and (row[0] - int(time.time()) > 0):
        return 'trial'
    mycursor.execute(f'SELECT premium FROM premium_servers WHERE server_id = {id}')
    premium = mycursor.fetchone()
    if premium and premium[0] == True:
        return True
    else:
        return False
async def get_difficulty(difficulty,ctx,in_list=None):
    new_numbers = []
    for x in difficulty:
        if x[0] == '[':
            if len(new_numbers) > 0:
                await ctx.channel.send('You specified difficulty twice!')
                if in_list:
                    in_list.remove(ctx.author.id)
                return
            if x[-1] != ']':
                await ctx.channel.send('Please do not use spaces when specifying difficulty!')
                if in_list:
                    in_list.remove(ctx.author.id)
                return
            else:
                numbers = x[1:-1]
                if len(numbers) == 0:
                    await ctx.channel.send('You didn\'t put anything in the brackets!')
                    if in_list:
                        in_list.remove(ctx.author.id)
                    return
                numbers = numbers.split(',')
                for entry in numbers:
                    if '-' in entry:
                        for num in list(range(int(entry[0]),int(entry[-1])+1)):
                            new_numbers.append(num)
                    else:
                        new_numbers.append(entry)
                try:
                    new_numbers = list(map(int,new_numbers))
                except:
                    await ctx.channel.send('Make sure you are using a dash when specifying difficulty!')
                    if in_list:
                        in_list.remove(ctx.author.id)
                    return
                new_numbers = list(set(new_numbers))
    return new_numbers
practice_sim_dict = dict()
class TK_Player():
    def __init__(self,author,team,ctx):
        self.ctx = ctx
        self.author = author
        self.total_points = 0
        self.tossups_heard = 0
        self.powers = 0
        self.tens = 0
        self.negs = 0
        self.team=team
        self.answerlines_missed = []
        self.cdepths = []
        def pred(m):
            return m.author == self.author and m.channel == self.ctx.channel
        def any_pred(m):
            return m.author == self.author
        self.pred = pred
        self.any_pred = any_pred
    def update(self,res):
        points = res[0]
        cdepth = res[1]
        self.total_points += points
        if points == 15:
            self.cdepths.append(cdepth)
            self.team.team_points += 15
            self.powers += 1
        elif points == 10:
            self.cdepths.append(cdepth)
            self.team.team_points += 10
            self.tens += 1
        elif points == -5:
            self.team.team_points -= 5
            self.negs += 1
    def get_cdepth(self):
        return sum(self.cdepths)/len(self.cdepths) if len(self.cdepths) else 0
class PR_Player():
    def __init__(self,author,team):
        self.author = author
        self.total_points = 0
        self.tossups_heard = 0
        self.powers = 0
        self.tens = 0
        self.negs = 0
        self.team=team
    def update(self,points):
        self.total_points += points
        if points == 15:
            self.team.team_points += 15
            self.powers += 1
        elif points == 10:
            self.team.team_points += 10
            self.tens += 1
        elif points == -5:
            self.team.team_points -= 5
            self.negs += 1
N_e = 0 #number of questions seen
m = 0 #number of tournaments
@client.command (name='end')
async def end(ctx):
    if ctx.author.id in in_pk:
        await ctx.channel.send('Did you mean `m pk end?`')
    else:
        await ctx.channel.send('Try sending the name of the command before end, e.g. `m practice end` or `m pk end`')
@client.command (name='help')
async def help(ctx):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    embed= discord.Embed(
    title= 'Help',
    colour= 0x42f5dd,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
    embed.add_field(name='m server',value='Join our support server [here](https://discord.gg/YsbhefcXpA)!')
    embed.add_field(name="m invite",value="Get an invite for the bot!",inline=True)
    embed.add_field(name='m info',value='Displays info about the bot!')
    embed.add_field(name="m instructions `name of command`", value="In depth instructions on a specific command. e.g. `m instructions card`", inline=False)
    embed.add_field(name="m example `name of command`", value="Examples for a specific command. e.g. `m example card`", inline=False)
    embed.add_field(name="m trial",value="Activate a 3 day premium trial!",inline=True)
    embed.add_field(name="m activate",value="Activates premium (only usable by patrons)",inline=True)
    embed.add_field(name="m cats", value="Displays the abbreviations used for categories", inline=True)
    embed.add_field(name="m subcats",value="Displays the abbreviations used for subcategories",inline=True)
    embed.add_field(name="m diffs",value="Displays the difficulty system used by the bot",inline=True)
    embed.add_field(name="m card", value="m card `category` `difficulty` `term`")
    embed.add_field(name="m pk", value = "m pk `category` `[optional] difficulty` `[optional] team` `[optional] comp` `[optional] timed`")
    embed.add_field(name="m tk", value = "Starts a tossup reader (text only)!\nm tk `category` `[optional] difficulty` `[optional] team`")
    embed.add_field(name="m sim", value = "Starts a simulation of a game (text only)!\nm sim `category` `[optional] difficulty` `[optional] ffa`")
    embed.add_field(name="m tournament", value = "Cards from a tournament\nm tournament `tournament name`")
    embed.add_field(name="m practice `[optional ffa]`",value="Starts a practice session. `m practice ffa` for free for all and `m practice` for teams")
    embed.add_field(name="m lookup",value = "m lookup `category` `term`\nShows frequency of a term in a graph!")
    embed.add_field(name="m list",value = "m list `category` `[optional] term` `[optional] difficulty`\nShows most frequent answerlines of a category or in relation to a term.")
    try:
        await ctx.channel.send(embed=embed)
    except:
        await ctx.channel.send('Error: Missing permissions. Please make sure the bot has `embed links` permission!')
    #copy mafia embed
@client.command (name='info',aliases=['details'])
async def info(ctx):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    embed = discord.Embed (
    title='FACE',
    colour=	0x7d99ff,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/626811419815444490/631882087280017428/silhouette-3073924_960_720.png?width=300&height=600')
    embed.add_field(name='Used in:',value=f'`{len(client.guilds)} servers!`')
    embed.add_field(name='Creators of this bot:', value =f'B3nj1#7587/<@{str(435504471343235072)}> and Shoorsen#5061/<@{483405210274889728}>', inline=True)
    embed.add_field(name='Programming language:', value ='Python 3.6.3', inline=True)
    embed.add_field(name='Library:', value =f'Discord python rewrite branch (v{discord.__version__})', inline=True)
    await ctx.channel.send(embed=embed)
@client.command (name='leave')
async def leave(ctx,id):
    if is_owner(ctx):
        guild = client.get_guild(int(id))
        if guild == None:
            await ctx.channel.send('Not a valid guild...')
        else:
            await guild.leave()
            await ctx.channel.send(f'Left {guild.name} :slight_frown:')
@client.command (name='shutdown')
async def shutdown(ctx):
    if is_owner(ctx):
        global is_shutdown
        await ctx.message.delete()
        await ctx.channel.send('shutting down...')
        for user_id in in_pk:
            try:
                user = client.get_user(user_id)
                await user.send('FACE is going offline for updates and bug fixes. The bot should be back up in a few minutes! Sorry for any inconveniences :slight_frown:')
            except:
                continue
        for user_id in in_tk:
            try:
                user = client.get_user(user_id)
                await user.send('FACE is going offline for updates and bug fixes. The bot should be back up in a few minutes! Sorry for any inconveniences :slight_frown:')
            except:
                continue
        for channel_id in practice_sim_dict.keys():
            try:
                channel = client.get_channel(channel_id)
                await channel.send('FACE is going offline for updates and bug fixes. The bot should be back up in a few minutes! Sorry for any inconveniences :slight_frown:')
            except:
                continue
        await asyncio.sleep(2)
        sys.exit()
@client.command (name='status')
async def status(ctx):
    if is_owner(ctx):
        await client.change_presence( activity=discord.Game(name='m help',type=0), afk=False)
@client.command (name='activate')
async def activate(ctx):
    mydb,mycursor = mysql_connect()
    try:
        guild_id = ctx.guild.id
    except:
        await ctx.channel.send('You cannot activate premium in a dm channel!')
    if await premium(ctx.guild.id,ctx) == True:
        await ctx.channel.send('This server already has access to premium features :slight_smile:!')
        return
    mycursor.execute(f'SELECT * FROM premium_servers WHERE user_id = {ctx.author.id}')
    rows = mycursor.fetchall()
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    if rows == []:
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='This command is only usable by patrons. If you recently became a patron, it may take up to 15 minutes for your benefits to be available.',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
    else:
        slots = [row for row in rows if row[1] == None]
        if len(slots) == 0:
            await ctx.channel.send('You have already activated premium in three servers!')
        else:
            await ctx.channel.send(f'Are you sure you want to activate premium in **{ctx.guild.name}**? You cannot reverse this decision. `y` for yes, `n` for no')
            try:
                msg = await client.wait_for('message',check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time...')
                return
            else:
                if msg.content.lower() == 'y':
                    mycursor.execute(f'UPDATE premium_servers SET server_id = {ctx.guild.id},premium = {True} WHERE server_id IS NULL AND user_id = {ctx.author.id} LIMIT 1')
                    mydb.commit()
                    await ctx.channel.send('Premium activated! :white_check_mark:')
                elif msg.content.lower() == 'n':
                    await ctx.channel.send('Abandoning the activation process...')
                    return
                else:
                    await ctx.channel.send('Not a valid response!')
                    return
@client.command (name='trial')
async def trial(ctx):
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    mydb,mycursor = mysql_connect()
    try:
        guild_id = ctx.guild.id
    except:
        await ctx.channel.send('You cannot start a trial in a dm channel!')
        return
    await add_count(guild_id)
    if await premium(ctx.guild.id,ctx) == True:
        await ctx.channel.send('This server already has access to premium features :slight_smile:!')
        return
    elif await premium(ctx.guild.id,ctx) == 'trial':
        await ctx.channel.send('This server is in the middle of its free trial :slight_smile:!')
        return
    mycursor.execute(f'SELECT * FROM trial_premium WHERE server_id = {ctx.guild.id}')
    rows = mycursor.fetchone()
    if rows == None:
        await ctx.channel.send(f'Are you sure you want to activate your free trial in **{ctx.guild.name}**? This is only usable once and will last for 24 hours. `y` for yes, `n` for no')
        try:
            msg = await client.wait_for('message',check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time...')
            return
        else:
            if msg.content.lower() == 'y':
                mycursor.execute(f'INSERT INTO trial_premium (server_id,timeout,used) VALUES ({ctx.guild.id},{int(time.time()+86400*3)},{False})') #86400
                mydb.commit()
                await ctx.channel.send('Free 24 hour trial activated! :white_check_mark:')
            elif msg.content.lower() == 'n':
                await ctx.channel.send('Abandoning the free trial activation process...')
                return
            else:
                await ctx.channel.send('Not a valid response!')
                return
    else:
        if rows[2] == True:
            await ctx.channel.send('The free trial for this server has already been used...:slight_frown:')
        else:
            await ctx.channel.send('The free trial is currently activated!')
@client.command (name='premium')
async def command_premium(ctx):
    try:
        guild_id = ctx.guild.id
    except:
        None
    else:
        if await premium(guild_id,ctx):
            await ctx.channel.send('This server already has access to premium features :slight_smile:!')
            return
    embed = discord.Embed (
    title='FACE Bot',
    colour=	0x7dffba,
    )
    embed.add_field(name='This server does not have premium features...yet :smirk:',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
    await ctx.channel.send(embed=embed)
@client.command (name='invite')
async def invite(ctx):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    embed= discord.Embed(
    title= 'Invite FACE!',
    colour= 0xf0f0f0,
    timestamp=datetime.datetime.now()
    )
    embed.add_field(name='Link',value='[invite FACE to your server](https://discord.com/oauth2/authorize?client_id=742880812961235105&scope=bot&permissions=121920)')
    await ctx.send(embed = embed)
@client.command (name='server')
async def server(ctx):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    embed= discord.Embed(
    title= 'Join our server!',
    colour= 0xf0f0f0,
    timestamp=datetime.datetime.now()
    )
    embed.add_field(name='Link',value='Join our support server [here](https://discord.gg/YsbhefcXpA)!')
    await ctx.send(embed=embed)
@client.command (name='instructions')
async def instructions(ctx,command = None):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    if command == None:
        await ctx.channel.send('Specify a command after m instructions, e.g. `m instructions card`')
    elif command == 'card':
        await ctx.channel.send('**---** Use the command `m card *category* [difficulty] *term(s)*`, e.g. `m card sci [3-5,7] proton`.\n**---** The bot will send a file that you can download and **import into Anki**!\n**---** Use `m card *category* *difficulty*` to card an entire category, e.g. `m card myth [3]`\n**---** You can substitue `all` for the category if you want to card specific terms across all categories.\n**---** Use the keyword `filtered` at the end of your command to remove similar cards and make your review more efficient. (e.g. `m card sci proton filtered`)')
    elif command == 'tournament':
        await ctx.channel.send('***---*** Use `m tournament *tournament name*`\n***---*** The cards will be from the tournament with the closest name, try to be as specific as possible.')
    elif command == 'pk':
        await ctx.channel.send('***---*** Starts a pk practice session.\n**---** m pk `category` `difficulty` `game_mode` `timed?`, e.g. `m pk sci [4-6] timed` or `m pk sci[4-6]`.\n***---*** Use `team` or `comp` to make a team pk or a competitive pk, e.g. `m pk all [3] team`, `m pk sci [4-6] comp`\n**---** Use `{}` for multiple categories, e.g. `m pk {sci,myth}`\n**---** Use m subcats `category` to view subcategories, and PK with subcategories using a colon, e.g. `m pk sci:bio [4-6]`\n**---** Use `m pk end` to end the game.\n**---** Use `~` before your messages to talk during the pk. e.g. `~that was a bad question`')
    elif command == 'tk':
        await ctx.channel.send('**---** Starts a tossup reader (text only) practice session.\n**---** m tk `category` `difficulty` `team`\n **---** e.g. `m tk sci [4-6]` or `m tk all [3] team`.\n**---** Use `m tk end` to end the game and `m next` to get the next question.')
@client.command (name='cats')
async def cats(ctx):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    embed = cat_embed
    embed.timestamp = datetime.datetime.now()
    await ctx.channel.send(embed=embed)
@client.command(name='subcats')
async def subcats(ctx,cat=None):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    if cat == None:
        await ctx.channel.send('Use m subcats `category` to browse subcategories. e.g. `m subcats sci`')
        return
    if cat.casefold() in FACE.first_cat_dict.values():
        cat = cat.casefold()
    elif FACE.first_cat_dict.get(cat.casefold()):
        cat = FACE.first_cat_dict.get(cat).casefold()
    else:
        await ctx.channel.send('That is not a valid category!')
        return
    embed = subcat_lookup.get(cat)
    embed.timestamp = datetime.datetime.now()
    await ctx.channel.send(embed=embed)
@client.command(name='diffs')
async def diffs(ctx):
    explanation_dict = {
    1: 'Middle School',
    2: 'Easy High School',
    3: 'Regular High School',
    4: 'Hard High School',
    5: 'National High School',
    6: 'Easy College',
    7: 'Regular College',
    8: 'Hard College',
    9: 'Open'
    }
    explanation_str = str()
    for key,value in explanation_dict.items():
        if key == 1:
            explanation_str = f'`{key}` **-->** {value}'
        else:
            explanation_str = f'{explanation_str}\n`{key}` **-->** {value}'
    await ctx.channel.send(explanation_str)
@client.command(name='example')
async def example(ctx,command):
    example_dict = {
    'card': '`m card sci proton [3]`\n`m card sci proton, neutron, electron`\n`m card religion [2]` (cards all religion tossups at level 2)\n`m card religion [3] filtered` (filters similar cards, make take longer to run)',
    'tournament': '`m tournament PACE 2019`\n`m tournament 2014 Masonic`',
    'pk': '`m pk all [3]`\n`m pk sci`\n`m pk all [3] comp` (competitive pk)`m pk lit [3] team` (team pk)',
    'tk': '`m tk all [3]`\n`m tk sci`\n`m pk lit [3] team` (team tk)',
    'sim': '`m sim all [3]`\n`m sim sci`\n`m sim all [3] ffa` (free for all, default is teams)',
    'practice': '`m practice ffa` (free for all)\n`m practice` (teams)',
    'lookup': '`m lookup sci Albert Einstein`\n`m lookup lit Ernest Hemmingway`',
    'list': '`m list sci [3]`\n`m list sci Albert Einstein` (returns related answerlines to Einstein)'
    }
    if example_dict.get(command):
        await ctx.channel.send(example_dict.get(command))
    else:
        await ctx.channel.send('No examples found!')

@client.command (name='tk')
async def tk(ctx,category=None,*difficulty):
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    # hour = datetime.datetime.now().hour
    # if ctx.author.id == 483405210274889728 and category != 'end':
    #     if not (hour >= 23 or hour < 2):
    #         token = secrets.token_urlsafe(16)
    #         print(token)
    #         await ctx.channel.send('Enter the token senpai: ')
    #         try:
    #             msg = await client.wait_for('message',check=pred,timeout=10)
    #         except asyncio.TimeoutError:
    #             await ctx.channel.send('Timed out!')
    #             return
    #         else:
    #             if msg.content != token:
    #                 await ctx.channel.send('That\'s incorrect...')
    #                 return
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    await add_count(guild_id)
    def close(id):
        global close_tk
        if id not in close_tk:
            return False
        return True
    def buzz_pred(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.casefold() in ['buzz','m skip','m tk end','c tk end']
    async def take_answer(end_question,author,edits_left=0,total_edits=0):
        for player in team.members:
            if author == player.author:
                ans_player = player
        cdepth = (total_edits - edits_left)/total_edits * 100 if total_edits > 0 else None
        cdepth = 100 if cdepth == 0 else cdepth
        try:
            msg = await client.wait_for('message', check=ans_player.pred,timeout=10)
        except asyncio.TimeoutError:
            add_points = -5 if end_question == False else 0
            ans_player.points += add_points
            await ctx.channel.send(f':x: `{add_points}`')
            await ctx.channel.send(formatted_answer)
        else:
            if msg.content == 'm skip':
                skip = True
                return 'break_loop'
            if msg.content != 'm tk end':
                def find_ans(ans,key):
                    if ans.find(key)==-1:
                        return
                    else:
                        first = ans.find(key)+2
                    second = ans.find(key,first)
                    new_str = ans[first:second]
                    return new_str
                underlined_portion = find_ans(formatted_answer,'__')
                underlined_portion = find_ans(formatted_answer,'**') if underlined_portion == None else underlined_portion
                underlined_portion = underlined_portion.casefold() if underlined_portion else underlined_portion
                no_response = 0
                similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                if similarity > 80 or msg.content.casefold() == underlined_portion:
                    add_points = 15 if ('(*)' not in tu_msg.content and '(*)' in question) else 10
                    ans_player.points += add_points
                    await ctx.channel.send(f'`{add_points}`')
                    correct = True
                else:
                    add_points = -5 if end_question == False else 0
                    ans_player.points += add_points
                    await ctx.channel.send(f':x: `{add_points}`')
                    ans_player.answerlines_missed.append(raw_answer)
                    correct = False
                await ctx.channel.send(f'ANSWER: {formatted_answer}')
                given_abbrev = msg.content.casefold().strip()
                real_abbrev = ''.join([x[0] for x in raw_answer.casefold().split()])
                if (10 <= similarity <= 75 or (msg.content.casefold() in formatted_answer.casefold()) or has_num(msg.content.casefold()) or has_num(raw_answer.casefold()) or given_abbrev == real_abbrev) and correct == False:   #;  where should this go follow m
                    await ctx.channel.send('Were you correct? Respond with `y` or `n`')
                    try:
                        msg = await client.wait_for('message', check=ans_player.pred,timeout=10)
                    except asyncio.TimeoutError:
                        None
                    else:
                        if msg.content != 'm tk end':
                            if msg.content.lower().startswith('n'):
                                add_points = -5 if end_question == False else 0
                                await ctx.channel.send(f':x: `{add_points}`')
                            elif msg.content.lower().startswith('y'):
                                correct = True
                                add_points = 15 if ('(*)' not in tu_msg.content and '(*)' in question) else 10
                                ans_player.points += add_points
                                ans_player.answerlines_missed.remove(raw_answer)
                                await ctx.channel.send(f'`{add_points}`')
                            else:
                                add_points = -5 if end_question == False else 0
                                await ctx.channel.send('Not a valid response! :x: `-5`')
                        else:
                            return 'end'
            else:
                return 'end'
        return add_points,ans_player,cdepth
    class Team():
        def __init__(self,members):
            self.members = members
            self.authors = [x.author for x in members]
            def team_pred(m):
                return ((m.author == ctx.author or m.author in self.authors) and m.channel == ctx.channel) and m.channel == ctx.channel and not m.content.startswith('~')
            def team_buzz_pred(m):
                return ((m.author == ctx.author or m.author in self.authors) and m.channel == ctx.channel) and m.content.casefold() in ['buzz','m skip','m tk end','c tk end','c skip'] and m.channel == ctx.channel
            def continue_pred(m):
                return ((m.author == ctx.author or m.author in self.authors) and m.channel == ctx.channel) and m.content.casefold() in ['c next','m next','c tk end','m tk end'] and m.channel == ctx.channel
            self.buzzpred = team_buzz_pred
            self.continuepred = continue_pred
            self.pred = team_pred
            self.total_points = 0
            self.tossups_heard = 0
            self.powers = 0
            self.difficulties = []
        def update(self,res,tk_difficulty):
            points = res[0]
            ans_player = res[1]
            cdepth = res[2]
            self.total_points += points
            self.difficulties.append(tk_difficulty)
            self.tossups_heard += 1
            ans_player.update(points,cdepth)
            if points == 15:
                self.powers += 1
        def get_winner(self):
            self.members.sort(key=lambda x: x.points)
            winner = self.members[1]
            loser = self.members[0]
            return winner,loser
        def get_ppg(self):
            ppg = 0 if (self.tossups_heard == 0) else 20*(self.total_points/self.tossups_heard)
            return ppg
        def get_diff(self):
            avg_diff = 0 if len(self.difficulties) == 0 else sum(self.difficulties)/len(self.difficulties)
            return avg_diff
        async def get_embed(self,category,is_team,guild_id):
            ppg = self.get_ppg()
            embed = discord.Embed (
            title=f'TK RESULTS:',
            colour=	0x303845,
            timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name='**PP20TUH**:',value=f'{ppg:.3f}')
            embed.add_field(name='POWERS:',value=f'{self.powers}',inline = True)
            embed.add_field(name='Total Points:',value=f'{self.total_points}',inline = True)
            embed.add_field(name='Avg diff.', value=f'{self.get_diff():.2f}')
            embed.add_field(name='Category',value=f'{category.upper()}')
            embed.add_field(name='Tossups Seen:',value=f'{self.tossups_heard}',inline = True)
            for player in self.members:
                embed.add_field(name=f'{player.author.name}:',value =f'{player.get_stats()}\n{player.points} total points\nC-Depth: {player.get_cdepth():.2f}',inline=True)
                await self.get_answerlines(player)
            if not await premium(guild_id,ctx):
                embed.add_field(name='Please support us!',value=f'FACE has many more features like Team TKs. Learn about our premium features [here](https://www.patreon.com/facebot)!',inline=False)
            return embed
        async def get_answerlines(self,player):
            cards = player.answerlines_missed
            def card_pred(m):
                return m.author == player.author and m.channel == ctx.channel
            if len(cards) > 0:
                await ctx.channel.send(f'{player.author.mention},Would you like missed answerlines? Respond with `n` for no and `y` for yes.')
                try:
                    msg = await client.wait_for('message',check=card_pred,timeout=20)
                except asyncio.TimeoutError:
                    await ctx.channel.send('You did not respond in time...')
                else:
                    if msg.content.casefold() != 'n':
                        cards = [f'**---** {x}\n' for x in cards]
                        cards = '**MISSED ANSWERLINES:**\n'+''.join(cards) +'Thanks for playing!'
                        try:
                            await player.author.send(cards)
                        except:
                            await ctx.channel.send('Could not send missed answerlines, check that server DMs are turned on.')
    class Player():
        def __init__(self,author,pred):
            self.author = author
            def pred(m):
                return m.author == self.author and m.channel == ctx.channel
            def buzz_pred(m):
                return m.author == self.author and m.channel == ctx.channel and m.content.casefold() in ['buzz','m skip','m tk end','c tk end'] and m.channel == ctx.channel
            def continue_pred(m):
                return (m.author == self.author and m.channel == ctx.channel) and m.content.casefold() in ['c next','m next','c tk end','m tk end'] and m.channel == ctx.channel
            self.pred = pred
            self.buzzpred = buzz_pred
            self.continuepred = continue_pred
            self.points = 0
            self.tossups_heard = 0
            self.powers = 0
            self.negs = 0
            self.tens = 0
            self.cdepths = []
            self.answerlines_missed = []
            self.difficulties = []
            self.no_responses = 0
        def update(self,points,cdepth):
            self.tossups_heard += 1
            correct = False
            if points == 15:
                self.powers += 1
                correct = True
            elif points == 10:
                self.tens += 1
                correct = True
            elif points == -5:
                self.negs += 1
            if cdepth and correct == True:
                self.cdepths.append(cdepth)
        def get_ppg(self):
            ppg = 0 if (self.tossups_heard == 0) else 20*(self.points/self.tossups_heard)
            return ppg
        def get_stats(self):
            stats = f'{self.powers}/{self.tens}/{self.negs}'
            return stats
        def get_cdepth(self):
            cdepth = 0 if len(self.cdepths) == 0 else sum(self.cdepths)/len(self.cdepths)
            return cdepth
    global in_tk
    global close_tk
    if ctx.author.id in in_tk: #orig_category != 'ranked'
        if category == 'end':
            if ctx.author.id not in close_tk:
                close_tk.append(ctx.author.id)
            await ctx.channel.send('Ending the tk...')
        elif category == 'end--force':
            if ctx.author.id in close_tk:
                close_tk.remove(ctx.author.id)
            in_tk.remove(ctx.author.id)
        else:
            await ctx.channel.send('You are already in a tk! Use `m tk end` to end a tk and allow a few seconds for the tk to end. If you are **not** in a tk, use `m tk end--force` after a while.')
        return
    # elif orig_category == 'ranked':
    #     if ranked_passed == ranked_questions:
    #         close_pk.append(ctx.author.id)
    #         await ctx.channel.send('Ending the pk...')
    elif category == 'end':
        await ctx.channel.send('You are not in a tk!')
        return
    in_tk.append(ctx.author.id)
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m tk *category* *[difficulty]*`, e.g. `m tk sci [3-7]` or `m tk sci:bio [1-9]`')
        in_tk.remove(ctx.author.id)
        return
    difficulty = list(difficulty)
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        in_tk.remove(ctx.author.id)
        return
    if 'timed' in difficulty:
        difficulty.remove('timed')
        timed = True

    else:
        timed = False
    is_team = False
    team = [Player(ctx.author,pred)]
    if 'team' in difficulty:
        if not await premium(guild_id,ctx):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Team tks are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            in_tk.remove(ctx.author.id)
            return
        # difficulty.remove('team')
        start = time.time()
        while start - time.time() < 60:
            await ctx.channel.send('Add a member to your team by mentioning them, e,g, respond with `@my_teammate`.')
            try:
                msg = await client.wait_for('message', check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time!')
                in_tk.remove(ctx.author.id)
                return
            else:
                if msg.content.startswith('m done'):
                    break
                teammate = None
                if len(msg.mentions)>0:
                    teammate = msg.mentions[0]
                if teammate and teammate not in team:
                    is_team = True
                    team.append(Player(teammate,pred))
                    await ctx.channel.send('Teammate added! :ballot_box_with_check:\nUse m done when you are done adding team members.')
                else:
                    await ctx.channel.send('That is not a valid Discord user!')
                    in_tk.remove(ctx.author.id)
                    return
    elif 'comp' in difficulty:
        await ctx.channel.send('TKs only have team and single-player modes! e.g. `m tk all [3] team` or `m tk myth [3]`')
        in_tk.remove(ctx.author.id)
        return
    new_numbers = await get_difficulty(difficulty,ctx,in_tk)
    if new_numbers == None:
        in_tk.remove(ctx.author.id)
        return
    difficulty = new_numbers[:]
    orig_category = category
    tossups = await FACE.get_tk_tossup(category,difficulty)
    if tossups == None:
        await ctx.channel.send('Please check your category spellings. Do not use spaces within the `{}` when specifying multiple categories.')
        in_tk.remove(ctx.author.id)
        return
    elif tossups == 'not enough':
        await ctx.channel.send('Not enough tossups found!')
        in_tk.remove(ctx.author.id)
        return
    elif tossups == 'error':
        await ctx.channel.send('There was an error...please try again.')
        in_tk.remove(ctx.author.id)
        return
    else:
        game_end = False
        id = ctx.author.id
        team = Team(team)
        first_time = True
        no_response = 0
        pred_to_use = team.pred
        continue_pred_to_use = team.continuepred
        buzz_pred_to_use = team.buzzpred
        player_up = team #BOOKMARK
        await ctx.channel.send('**INSTRUCTIONS**\n**---** Use `m next` to get the next question and `buzz` to buzz\n**---** Use `m tk end` to end the game.')
        while True:
            if id in close_tk:
                embed = await team.get_embed(category,is_team,guild_id)
                await ctx.channel.send(embed=embed)
                close_tk.remove(id)
                in_tk.remove(id)
                return
            if team.tossups_heard > 0:
                tossups = await FACE.get_tk_tossup(category,difficulty)
                if tossups == 'error':
                    await ctx.channel.send('There was an error...please try again. Ending the tk.')
                    embed = await team.get_embed(category,is_team,guild_id)
                    await ctx.channel.send(embed=embed)
                    close_tk.remove(id)
                    in_tk.remove(id)
                    return
            for i,q in enumerate(tossups):
                try:
                    skip = False
                    question = q[0][0]
                    raw_answer = q[0][2]
                    formatted_answer = q[0][1]
                    tk_difficulty = q[0][3]
                    words = q[2]
                    num_words = len(q[2])
                    sentences = q[3]
                    max_words = q[1]
                    edits = math.ceil(num_words/5)
                    edits_left = edits-1
                except:
                    await ctx.channel.send('There was an error...please try again. Ending the tk.')
                    embed = await team.get_embed(category,is_team,guild_id)
                    await ctx.channel.send(embed=embed)
                    close_tk.remove(id)
                    in_tk.remove(id)
                    return
                try:
                    mark = question.find(words[4])+len(words[4])
                except:
                    continue
                tu_msg = await ctx.channel.send(question[:mark])
                correct = False
                while edits_left > 0:
                    if id in close_tk:
                        embed = await team.get_embed(category,is_team,guild_id)
                        await ctx.channel.send(embed=embed)
                        close_tk.remove(id)
                        in_tk.remove(id)
                        return
                    to_date = edits - edits_left
                    if 4+(to_date*5) >= len(words):
                        looking = words[-1]
                    else:
                        looking = words[4+(to_date*5)]
                    # await ctx.channel.send(f'looking for {looking}, mark is {mark}')
                    mark = question.find(looking,mark)+len(looking)
                    await tu_msg.edit(content=question[:mark])
                    edits_left -= 1
                    try:
                        buzz_msg = await client.wait_for('message',check=pred_to_use,timeout=1.4)
                    except asyncio.TimeoutError:
                        None
                    else:
                        if buzz_msg.content.casefold() in ['c skip','m skip']:
                            await ctx.channel.send('Skipped :dizzy:')
                            skip = True
                            break
                        elif buzz_msg.content.casefold() == 'buzz':
                            await tu_msg.edit(content=question[:mark]+'**$**')
                            await ctx.channel.send(f'{buzz_msg.author.mention} buzzed :loudspeaker:')
                            res = await take_answer(False,buzz_msg.author,edits_left,edits)
                            if res == 'break_loop':
                                break
                            skip = True if res == 'skip' else False
                            if skip == True:
                                await ctx.channel.send('Skipped :dizzy:')
                                break
                            if id in close_tk:
                                embed = await team.get_embed(category,is_team,guild_id)
                                await ctx.channel.send(embed=embed)
                                close_tk.remove(id)
                                in_tk.remove(id)
                                return
                            if id not in close_tk and skip == False:
                                player_up.update(res,tk_difficulty)
                                await asyncio.sleep(2)
                            await tu_msg.edit(content=question[:mark]+'**$**'+question[mark:])
                            correct = True
                            break
                if not correct and not skip:
                    try:
                        buzz_msg = await client.wait_for('message',check=buzz_pred_to_use,timeout=10)
                    except asyncio.TimeoutError:
                        await ctx.channel.send(f'This tossup goes dead...:headstone:\nAnswer:{formatted_answer}')
                    else:
                        if buzz_msg.content.casefold() not in ['c skip','m skip']:
                            if id in close_tk:
                                embed = await team.get_embed(category,is_team,guild_id)
                                await ctx.channel.send(embed=embed)
                                close_tk.remove(id)
                                in_tk.remove(id)
                                return
                            if buzz_msg.content.casefold() == 'buzz':
                                await tu_msg.edit(content=question[:mark]+'**$**')
                                await ctx.channel.send(f'{buzz_msg.author.mention} buzzed :loudspeaker:')
                                res = await take_answer(True,buzz_msg.author)
                                skip = True if res == 'skip' else False
                                if skip == True:
                                    break
                                if id not in close_tk and skip == False:
                                    player_up.update(res,tk_difficulty)
                                    await asyncio.sleep(2)
                                await tu_msg.edit(content=question[:mark]+'**$**'+question[mark:])
                        else:
                            await ctx.channel.send('Skipped :dizzy:')
                if skip == True:
                    continue
                try:
                    msg = await client.wait_for('message',check=continue_pred_to_use,timeout=60)
                except asyncio.TimeoutError:
                    await ctx.channel.send('Timed out! Ending the tk...')
                    embed = await team.get_embed(category,is_team,guild_id)
                    await ctx.channel.send(embed=embed)
                    in_tk.remove(id)
                    if id in close_tk:
                        close_tk.remove(id)
                    return
                else:
                    continue
    embed = await team.get_embed(category,is_team,guild_id)
    await ctx.channel.send(embed=embed)
    in_tk.remove(id)
@client.command (name='pk')
async def pk(ctx,category=None,*difficulty):
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith('~')
    # hour = datetime.datetime.now().hour
    # if ctx.author.id == 483405210274889728 and category != 'end':
    #     if not (hour >= 23 or hour < 2):
    #         token = secrets.token_urlsafe(16)
    #         print(token)
    #         await ctx.channel.send('Enter the token senpai: ')
    #         try:
    #             msg = await client.wait_for('message',check=pred,timeout=10)
    #         except asyncio.TimeoutError:
    #             await ctx.channel.send('Timed out!')
    #             return
    #         else:
    #             if msg.content != token:
    #                 await ctx.channel.send('That\'s incorrect...')
    #                 return
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    await add_count(guild_id)
    def close(id):
        global close_pk
        if id not in close_pk:
            return False
        return True
    # def team_pred(m):
    #     return ((m.author == ctx.author or m.author in team.members) and m.channel == ctx.channel) and not m.content.startswith('~')
    class Team():
        def __init__(self,members):
            self.members = members
            self.authors = [x.author for x in members]
            def team_pred(m):
                return ((m.author == ctx.author or m.author in self.authors) and m.channel == ctx.channel) and not m.content.startswith('~')
            self.pred = team_pred
            self.total_points = 0
            self.bonuses_heard = 0
            self.thirties = 0
            self.difficulties = []
        def update(self,points,pk_difficulty):
            self.total_points += points
            self.difficulties.append(pk_difficulty)
            self.bonuses_heard += 1
            if points == 30:
                self.thirties += 1
        def get_winner(self):
            self.members.sort(key=lambda x: x.points)
            winner = self.members[1]
            loser = self.members[0]
            return winner,loser
        def get_ppb(self):
            ppb = 0 if (self.bonuses_heard == 0) else (self.total_points/self.bonuses_heard)
            return ppb
        def get_diff(self):
            avg_diff = 0 if len(self.difficulties) == 0 else sum(self.difficulties)/len(self.difficulties)
            return avg_diff
        async def get_embed(self,category,comp_pk,is_team,guild_id):
            ppb = self.get_ppb()
            if comp_pk: #ranked_pk
                winner,loser = self.get_winner()
            embed = discord.Embed (
            title=f'PK RESULTS:',
            colour=	0x303845,
            timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            if comp_pk:
                winner,loser = team.get_winner()
                embed.add_field(name='**WINNER**',value=f'{winner.author.name}')
                embed.add_field(name=f'{winner.author.name}\'s Points',value=f'{winner.points} points, PPB: {winner.get_ppb()}')
                embed.add_field(name=f'{loser.author.name}\'s Points',value=f'{loser.points} points, PPB: {loser.get_ppb()}')
            # elif ranked_pk:
            #     winner,loesr = team.get_winner()
            #     embed.add_field(name='**WINNER**',value=f'{winner.author.name}')
            #     embed.add_field(name=f'{winner.author.name}\'s Points',value=f'{winner.points} points, PPB: {winner.get_ppb()}')
            #     embed.add_field(name=f'{loser.author.name}\'s Points',value=f'{loser.points} points, PPB: {loser.get_ppb()}')
            else:
                embed.add_field(name='**PPB**:',value=f'{ppb:.3f}')
                embed.add_field(name='30 30 30:',value=f'{self.thirties}',inline = True)
                embed.add_field(name='Total Points:',value=f'{self.total_points}',inline = True)
            embed.add_field(name='Avg diff.', value=f'{self.get_diff():.2f}')
            embed.add_field(name='Category',value=f'{category.upper()}')
            embed.add_field(name='Bonuses Seen:',value=f'{self.bonuses_heard}',inline = True)
            if not await premium(guild_id,ctx):
                embed.add_field(name='Please support us!',value=f'FACE has many more features like Team PKs or getting reviewable PK cards. Learn about our premium features [here](https://www.patreon.com/facebot)!',inline=False)
            # if await premium(guild_id,ctx):
            for player in self.members:
                await self.get_cards(player.answerlines_missed,player)
            if is_team == True:
                for player in self.members:
                    embed.add_field(name=f'{player.author.name}:',value =f'{player.points} total points',inline=False)
            return embed
        async def get_cards(self,cards,player):
            def card_pred(m):
                return m.author == player.author and m.channel == ctx.channel
            await ctx.channel.send(f'{player.author.mention},Would you like missed answerlines? Respond with `n` for no and `y` for yes.')
            try:
                msg = await client.wait_for('message',check=card_pred,timeout=20)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time...')
            else:
                if msg.content.casefold() != 'n':
                    list_cards = [f'**---** {x[1]}\n' for x in cards]
                    list_cards = '**MISSED ANSWERLINES:**\n'+''.join(list_cards) +'Thanks for playing!'
                    try:
                        await player.author.send(list_cards)
                    except:
                        await ctx.channel.send('Could not send missed answerlines, check that server DMs are turned on.')
            if await premium(guild_id,ctx):
                await ctx.channel.send(f'{player.author.mention},Would you like PK review cards? Respond with `n` for no and `y` for yes.')
                try:
                    msg = await client.wait_for('message',check=card_pred,timeout=20)
                except asyncio.TimeoutError:
                    await ctx.channel.send('You did not respond in time. Deleting PK cards...')
                else:
                    if msg.content.casefold() != 'n':
                        full_path = await FACE.make_bonus_cards(cards,player.author.id)
                        with open(full_path, 'rb') as fp:
                            try:
                                await player.author.send(file=discord.File(fp, f'Your PK cards (click to download).csv'))
                            except:
                                await ctx.channel.send('Could not send pk cards, check that server DMs are turned on.')
                        await asyncio.sleep(5)
                        os.remove(full_path)
    class Player():
        def __init__(self,author,pred):
            self.author = author
            self.pred = pred
            self.points = 0
            self.bonuses_heard = 0
            self.thirties = 0
            self.answerlines_missed = []
            self.difficulties = []
            self.no_responses = 0
        def update(self,points,pk_difficulty):
            nonlocal team
            self.difficulties.append(pk_difficulty)
            self.bonuses_heard += 1
            team.bonuses_heard += 1
            if points == 30:
                self.thirties += 1
        def get_ppb(self):
            ppb = 0 if (self.bonuses_heard == 0) else (self.points/self.bonuses_heard)
            return ppb
    global in_pk
    global close_pk
    if ctx.author.id in in_pk: #orig_category != 'ranked'
        if category == 'end':
            if ctx.author.id not in close_pk:
                close_pk.append(ctx.author.id)
            await ctx.channel.send('Ending the pk...')
        elif category == 'end--force':
            if ctx.author.id in close_pk:
                close_pk.remove(ctx.author.id)
            in_pk.remove(ctx.author.id)
        else:
            await ctx.channel.send('You are already in a pk! Use `m pk end` to end a pk and allow a few seconds for the pk to end. If you are **not** in a pk, use `m pk end--force` after a while.')
        return
    # elif orig_category == 'ranked':
    #     if ranked_passed == ranked_questions:
    #         close_pk.append(ctx.author.id)
    #         await ctx.channel.send('Ending the pk...')
    elif category == 'end':
        await ctx.channel.send('You are not in a pk!')
        return
    in_pk.append(ctx.author.id)
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m pk *category* *[difficulty]*`, e.g. `m pk sci [3-7]` or `m pk sci:bio [1-9]`')
        in_pk.remove(ctx.author.id)
        return
    difficulty = list(difficulty)
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        in_pk.remove(ctx.author.id)
        return
    if 'timed' in difficulty:
        difficulty.remove('timed')
        timed = True

    else:
        timed = False
    is_team = False
    comp_pk = False
    ranked_pk = False
    team = [Player(ctx.author,pred)]
    if 'team' in difficulty:
        if not await premium(guild_id,ctx):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Team PKs are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            in_pk.remove(ctx.author.id)
            return
        # difficulty.remove('team')
        start = time.time()
        while start - time.time() < 60:
            await ctx.channel.send('Add a member to your team by mentioning them, e,g, respond with `@my_teammate`.')
            try:
                msg = await client.wait_for('message', check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time!')
                in_pk.remove(ctx.author.id)
                return
            else:
                if msg.content.startswith('m done'):
                    break
                teammate = None
                if len(msg.mentions)>0:
                    teammate = msg.mentions[0]
                if teammate and teammate not in team:
                    is_team = True
                    team.append(Player(teammate,pred))
                    await ctx.channel.send('Teammate added! :ballot_box_with_check:\nUse m done when you are done adding team members.')
                else:
                    await ctx.channel.send('That is not a valid Discord user!')
                    in_pk.remove(ctx.author.id)
                    return
    elif 'comp' in difficulty:
        if not await premium(guild_id,ctx):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Competitive PKs are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            in_pk.remove(ctx.author.id)
            return
        await ctx.channel.send('Ping your opponent to add them, e.g.`@my_opponent`.')
        try:
            msg = await client.wait_for('message', check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time!')
            in_pk.remove(ctx.author.id)
            return
        else:
            if len(msg.mentions)>0:
                opponent = msg.mentions[0]
            if opponent:
                if 'comp' in difficulty:
                    comp_pk = True
                def pred_B(m):
                    return m.author == opponent and m.channel == ctx.channel and not m.content.startswith('~')
                team.append(Player(opponent,pred_B))
                await ctx.channel.send('Opponent added :ballot_box_with_check:')
            else:
                await ctx.channel.send('That is not a valid Discord user!')
                in_pk.remove(ctx.author.id)
                return
    elif category == 'ranked':
        # difficulty.remove('comp')
        await ctx.channel.send('Ping your opponent to add them, e.g.`@my_opponent`.')
        try:
            msg = await client.wait_for('message', check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time!')
            in_pk.remove(ctx.author.id)
            return
        else:
            if len(msg.mentions)>0:
                opponent = msg.mentions[0]
            if opponent:
                # if 'ranked' == category:
                #     ranked_pk = True
                def pred_B(m):
                    return m.author == opponent and m.channel == ctx.channel and not m.content.startswith('~')
                team.append(Player(opponent,pred_B))
                await ctx.channel.send('Opponent added :ballot_box_with_check:')
            else:
                await ctx.channel.send('That is not a valid Discord user!')
                in_pk.remove(ctx.author.id)
                return
    new_numbers = await get_difficulty(difficulty,ctx,in_pk)
    if new_numbers == None:
        in_pk.remove(ctx.author.id)
        return
    difficulty = new_numbers[:]
    orig_category = category
    bonuses = await FACE.get_bonus(category,difficulty)
    if bonuses == None:
        await ctx.channel.send('Please check your category spellings. Do not use spaces within the `{}` when specifying multiple categories.')
        in_pk.remove(ctx.author.id)
        return
    elif bonuses == 'not enough':
        await ctx.channel.send('Not enough bonuses found!')
        in_pk.remove(ctx.author.id)
        return
    else:
        num_bonuses = bonuses[-1][0]
        await ctx.channel.send(f'{num_bonuses} bonuses found!')
        category = bonuses[-1][1]
        game_end = False
        id = ctx.author.id
        team = Team(team)
        first_time = True
        no_response = 0
        while True and game_end == False and close(id) == False:
            if not first_time:
                bonuses = await FACE.get_bonus(orig_category,difficulty)
            if bonuses == None:
                await ctx.channel.send('There was an error :slight_frown:. Ending the pk.')
                if id not in close_pk:
                    close_pk.append(id)
                break
            for i in range(4):
                if comp_pk == True: #or ranked_pk == True
                    if i % 2 == 0:
                        player_up = team.members[0]
                    else:
                        player_up = team.members[1]
                    avatar = player_up.author.avatar_url
                    pred_to_use = player_up.pred
                else:
                    pred_to_use = team.pred
                    player_up = team
                    avatar = ctx.author.avatar_url
                skip = False
                if game_end == True or close(id) == True:
                    break
                points = 0
                possible_points = 0
                tournament = bonuses[i][0][1]
                leadin = bonuses[i][0][0]
                color = bonuses[i][0][3]
                pk_difficulty = bonuses[i][0][2]
                for num in range(3):
                    question = bonuses[i][num+1][0]
                    formatted_answer = bonuses[i][num+1][1]
                    raw_answer = bonuses[i][num+1][2]
                    if game_end == True or close(id) == True:
                        break
                    possible_points += 10
                    embed = discord.Embed (
                    title=f'Question {team.bonuses_heard+1} ~ {tournament}',
                    colour=	0x56cef0,
                    timestamp=datetime.datetime.now()
                    )
                    if color:
                        embed.colour = color
                    embed.set_thumbnail(url=avatar)
                    if num == 0:
                        embed.add_field(name='\u200b',value = f'{leadin}')
                    embed.add_field(name='\u200b',value = f'**---**         {question}',inline=False)
                    if timed == True:
                        embed.set_footer(text='You have 16 seconds...')
                    await ctx.channel.send(embed=embed)
                    try:
                        if timed == True:
                            msg = await client.wait_for('message', check=pred_to_use,timeout=16)
                        else:
                            msg = await client.wait_for('message', check=pred_to_use,timeout=300)
                    except asyncio.TimeoutError:
                        await ctx.channel.send(formatted_answer)
                        if no_response >= 4:
                            embed = await team.get_embed(category,comp_pk,is_team,guild_id)
                            await ctx.channel.send(embed=embed)
                            if id in close_pk:
                                close_pk.remove(id)
                            game_end = True
                            break
                        no_response += 1
                    else:
                        if msg.content == 'm skip':
                            skip = True
                            no_response = 0
                            break
                        if msg.content != 'm pk end':
                            for player in team.members:
                                if msg.author == player.author:
                                    ans_player = player
                            def find_ans(ans,key):
                                if ans.find(key)==-1:
                                    return
                                else:
                                    first = ans.find(key)+2
                                second = ans.find(key,first)
                                new_str = ans[first:second]
                                return new_str
                            underlined_portion = find_ans(formatted_answer,'__')
                            underlined_portion = find_ans(formatted_answer,'**') if underlined_portion == None else underlined_portion
                            underlined_portion = underlined_portion.casefold() if underlined_portion else underlined_portion
                            no_response = 0
                            similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                            if similarity > 80 or msg.content.casefold() == underlined_portion:
                                ans_player.points += 10
                                points += 10
                                await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                correct = True
                            else:
                                await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                ans_player.answerlines_missed.append((question,raw_answer))
                                correct = False
                            await ctx.channel.send(f'ANSWER: {formatted_answer}')
                            given_abbrev = msg.content.casefold().strip()
                            real_abbrev = ''.join([x[0] for x in raw_answer.casefold().split()])
                            if (20 <= similarity <= 80 or (msg.content.casefold() in formatted_answer.casefold()) or has_num(msg.content.casefold()) or has_num(raw_answer.casefold()) or given_abbrev == real_abbrev) and correct == False:   #;  where should this go follow m
                                await ctx.channel.send('Were you correct? Respond with `y` or `n`')
                                try:
                                    msg = await client.wait_for('message', check=pred_to_use,timeout=10)
                                except asyncio.TimeoutError:
                                    None
                                else:
                                    if msg.content != 'm pk end':
                                        if msg.content.lower().startswith('n'):
                                                await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                        elif msg.content.lower().startswith('y'):
                                            ans_player.points += 10
                                            ans_player.answerlines_missed.remove((question,raw_answer))
                                            points += 10
                                            await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                        else:
                                            await ctx.channel.send('Not a valid response!')
                    await asyncio.sleep(0.5)
                if id not in close_pk and skip == False:
                    player_up.update(points,pk_difficulty)
                    await asyncio.sleep(1)
            first_time = False
        if id in close_pk:
            embed = await team.get_embed(category,comp_pk,is_team,guild_id)
            await ctx.channel.send(embed=embed)
            close_pk.remove(id)
        if id in in_pk:
            in_pk.remove(id)
@client.command (name='practice')
async def practice(ctx,extra=None):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    if extra == 'end':
        return
    if practice_sim_dict.get(ctx.channel.id):
        await ctx.channel.send('There is already a practice in this channel!')
        return
    ffa = True if extra == 'ffa' else False
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    def end_pred(m):
        return m.content == 'm practice end' and (m.author== moderator or m.author == ctx.author)
    def check(reaction, user):
        nonlocal msg
        return (str(reaction.emoji) == '🇧' or str(reaction.emoji) == '🅰️') and user != client.user and reaction.message.id == msg.id
    def moderator_pred(m): #used to appoint a moderator
        return m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) > 0
    def buzz_pred(m):
        nonlocal directory
        nonlocal buzzes
        nonlocal ffa
        if not ffa:
            return (((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id).team not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)) and m.channel == ctx.channel
        else:
            return (((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id) not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)) and m.channel == ctx.channel
    def grade_pred(m): # used to grade a tossup answer
        return ((m.author == moderator) and m.content in (ten+power+neg+zero)) or end_pred(m)
    def mod_next(m): # used for advancing tossups after bonuses
        return ((m.author == moderator) and m.content.startswith('m next')) or end_pred(m)
    def grade_bonus(m):
        return ((m.author == moderator) and (m.content.isdigit() and int(m.content) in [0,10,20,30])) or end_pred(m)
    await ctx.channel.send('Do you want to practice with bonuses? (Y/N)')
    try:
        msg = await client.wait_for('message',check=pred,timeout=15)
    except asyncio.TimeoutError:
        await ctx.channel.send('Practice timed out...')
        return
    else:
        if msg.content.casefold().startswith('y'):
            await ctx.channel.send('Bonuses enabled :white_check_mark:.')
            bonuses = True
        elif msg.content.casefold().startswith('n'):
            await ctx.channel.send('Bonuses disabled :x:.')
            bonuses = False
        else:
            await ctx.channel.send('Not a valid response. Ending practice...')
            return
    ten = ['ten','+','10']
    power = ['power','*','15']
    neg = ['neg','-','-5']
    zero = ['zero','0']
    class Team():
        def __init__(self, players, name):
            self.players = players
            self.name = name
            self.team_points = 0
        def init_directory(self):
            self.directory = dict()
            for player in self.players:
                self.directory[player.author.id] = player
    # class Player():
    #     def __init__(self,author,team):
    #         self.author = author
    #         self.total_points = 0
    #         self.tossups_heard = 0
    #         self.powers = 0
    #         self.tens = 0
    #         self.negs = 0
    #         self.team=team
    #     def update(self,points):
    #         self.total_points += points
    #         if points == 15:
    #             self.team.team_points += 15
    #             self.powers += 1
    #         elif points == 10:
    #             self.team.team_points += 10
    #             self.tens += 1
    #         elif points == -5:
    #             self.team.team_points -= 5
    #             self.negs += 1
    start = time.time()
    Team_A = Team([],'A Team')
    Team_B = Team([],'B Team')
    players = []
    game = True
    if not ffa:
        msg = await ctx.channel.send('React to this message to join a team!')
        await msg.add_reaction('🅰️')
        await msg.add_reaction('🇧')
    else:
        msg = await ctx.channel.send('React to this message to join the practice!')
        await msg.add_reaction('🅰️')
    while time.time() - start < 30:#change to 30
        try:
            reaction,user = await client.wait_for('reaction_add', timeout=10,check=check)
        except asyncio.TimeoutError:
            None
        else:
            if user not in players:
                players.append(user)
                if str(reaction.emoji) == '🅰️':
                    Team_A.players.append(PR_Player(user,Team_A))
                else:
                    Team_B.players.append(PR_Player(user,Team_B))
            else:
                try:
                    await msg.remove_reaction(str(reaction.emoji),user)
                except:
                    await ctx.channel.send('Error. Please enable `manage messages` for the FACE role!')
                    return
    if not ffa:
        A_string = '```A TEAM: '
        B_string = '```B TEAM: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}' # append to string with new line
        for x in Team_B.players:
            B_string = B_string + f'\n{x.author.name}'
        practice_size = 2
        await ctx.channel.send(A_string+'```')
        await ctx.channel.send(B_string+'```')
    else:
        A_string = '```FFA: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}'
        practice_size = len(Team_A.players)
        await ctx.channel.send(A_string+'```')
    await ctx.channel.send('Ping the moderator within the next 30 seconds.')
    try:
        msg = await client.wait_for('message', check=moderator_pred, timeout=30)
    except asyncio.TimeoutError:
        await ctx.channel.send('No moderator added. Ending practice.')
        return
    else:
        moderator = msg.mentions[0]
        await ctx.channel.send(f'{moderator.name} is now the moderator.')
    instructions = f'''
{moderator.mention} -- **MODERATOR INSTRUCTIONS**
**---** For powers, type one of the following: `*`,`power`,`15`
**---** For tens: `+`,`ten`,`10`
**---** For negs: `-`,`neg`,`-5`
**---** For no points: `0`,`zero`
**--** Type `m next` if a tossup goes dead.
**---** On bonuses, type `m next` once the bonus is over to assign points.
**---** PLAYERS: Type `buzz` to buzz'''

    await ctx.channel.send(instructions)
    game = True
    tossup_num = 0
    next_num = 0
    Team_A.init_directory()
    Team_B.init_directory()
    directory = {**Team_A.directory, **Team_B.directory}
    practice_sim_dict[ctx.channel.id] = [ffa,'practice',moderator,Team_A,Team_B,ctx]
    while game:
        Team_A.init_directory()
        Team_B.init_directory()
        directory = {**Team_A.directory, **Team_B.directory}
        players = [x.author for x in Team_A.players + Team_B.players]
        #await ctx.channel.send(f'{tossup_num}, {next_num}')
        if tossup_num >= next_num:
            buzzes = []
            await ctx.channel.send(f'\~\~\~\~\~\~\~\~\~\~\~\~**Tossup {tossup_num+1}**\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~')
            next_num = tossup_num + 1
        try:
            msg = await client.wait_for('message', check=buzz_pred,timeout=300)
        except asyncio.TimeoutError:
            await ctx.channel.send(f'{ctx.author.mention} No activity for 5 minutes, please send a message to continue')
            try:
                response = await client.wait_for('message',check=pred,timeout=20)
            except:
                break
            else:
                continue
        else:
            if msg.content == 'm practice end':
                await ctx.channel.send('**Practice ended.**')
                break
            if msg.content == 'm next':
                tossup_num += 1
                continue
            await ctx.channel.send(f'{moderator.mention} `buzz from {msg.author.name}`')
            buzzer =  directory.get(msg.author.id)
            answering_team = buzzer.team if not ffa else buzzer
            try:
                grade = await client.wait_for('message',check=grade_pred,timeout=300)
            except asyncio.TimeoutError:
                def still_here(m):
                    return m.channel == ctx.channel and m.content.lower() == 'resume'
                await ctx.channel.send('Are you still there? Respond with `resume` to stop the practice from ending.')
                try:
                    response = await client.wait_for('message',check=still_here,timeout=60)
                except asyncio.TimeoutError:
                    break
                else:
                    await ctx.channel.send('Practice resuming!')
                    continue
            else:
                if grade.content == 'm practice end':
                    await ctx.channel.send('**Practice ended.**')
                    break
                correct = True
                buzzes.append(answering_team)
                if grade.content in ten:
                    tossup_num += 1
                    buzzer.update(10)
                elif grade.content in power:
                    tossup_num += 1
                    buzzer.update(15)
                elif grade.content in neg:
                    correct = False
                    await ctx.channel.send('neg :x:')
                    buzzer.update(-5)
                elif grade.content in zero:
                    correct = False
                    await ctx.channel.send(':zero:')
                if bonuses == True and correct == True:
                    await ctx.channel.send(f'\~\~\~\~\~\~\~\~\~\~\~\~**Bonus {tossup_num+1}**\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~')
                    try:
                        next_msg = await client.wait_for('message',check=mod_next,timeout=300)
                    except asyncio.TimeoutError:
                        def still_here(m):
                            return m.channel == ctx.channel and m.content.lower() == 'resume'
                        await ctx.channel.send('Are you still there? Respond with `resume` to stop the practice from ending.')
                        try:
                            response = await client.wait_for('message',check=still_here,timeout=60)
                        except asyncio.TimeoutError:
                            break
                        else:
                            await ctx.channel.send('Practice resuming!')
                            continue
                    else:
                        if next_msg.content == 'm practice end':
                            await ctx.channel.send('**Practice ended.**')
                            break
                        await ctx.channel.send('`Points earned on bonus?: `')
                        try:
                            bonus_points = await client.wait_for('message',check=grade_bonus,timeout=300)
                        except asyncio.TimeoutError:
                            def still_here(m):
                                return m.channel == ctx.channel and m.content.lower() == 'resume'
                            await ctx.channel.send('Are you still there? Respond with `resume` to stop the practice from ending.')
                            try:
                                response = await client.wait_for('message',check=still_here,timeout=60)
                            except asyncio.TimeoutError:
                                break
                            else:
                                await ctx.channel.send('Practice resuming!')
                                continue
                        else:
                            if bonus_points.content == 'm practice end':
                                await ctx.channel.send('**Practice ended.**')
                                break
                            if not ffa:
                                answering_team.team_points += int(bonus_points.content)
                            else:
                                answering_team.total_points += int(bonus_points.content)
                elif len(buzzes) == practice_size and correct == False: #change to practice_size
                    tossup_num += 1
    del practice_sim_dict[ctx.channel.id]
    embed = discord.Embed (
    title='Practice Stats',
    colour=	0x83e6d0,
    timestamp=datetime.datetime.now()
    )
    Team_A.players.sort(reverse=True,key=lambda x: x.total_points)
    Team_B.players.sort(reverse=True,key=lambda x: x.total_points)
    A_str = f'{Team_A.team_points} points\n------------------------'
    for i,player in enumerate(Team_A.players):
        stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
        A_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}\nPP20TUH:{20*(player.total_points/tossup_num):.2f}'
    embed.add_field(name='**Team A**',value=A_str)
    B_str = f'{Team_B.team_points} points\n------------------------'
    if not ffa:
        for i,player in enumerate(Team_B.players):
            stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
            B_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}\nPP20TUH:{20*(player.total_points/tossup_num):.2f}'
        embed.add_field(name='**Team B**',value=B_str)
    embed.set_footer(text='Good game!')
    await ctx.channel.send(embed=embed)
@client.command (name='sim')
async def sim(ctx,category=None,*difficulty):
    guild_id = ctx.guild.id
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m sim *category* *[difficulty]*`, e.g. `m sim sci [3-7]` or `m sim sci:bio [1-9]` or `m sim all [3]`')
        return
    try:
        await add_count(ctx.guild.id)
    except:
        None
    if category == 'end':
        return
    if practice_sim_dict.get(ctx.channel.id):
        await ctx.channel.send('There is already a sim in this channel!')
        return
    if not await premium(guild_id,ctx):
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='Practice sims are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
        return
    difficulty = list(difficulty)
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        return
    ffa = True if 'ffa' in difficulty else False
    if 'ffa' in difficulty:
        difficulty.remove('ffa')
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    def end_pred(m):
        return m.content == 'm sim end' and (m.author== moderator or m.author == ctx.author)
    def check(reaction, user):
        nonlocal msg
        return (str(reaction.emoji) == '🇧' or str(reaction.emoji) == '🅰️') and user != client.user and reaction.message.id == msg.id
    def moderator_pred(m): #used to appoint a moderator
        return m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) > 0
    def buzz_pred(m):
        nonlocal directory
        nonlocal buzzes
        nonlocal ffa
        if not ffa:
            return (((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id).team not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)) and m.channel == ctx.channel
        else:
            return (((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id) not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)) and m.channel == ctx.channel
    def grade_pred(m): # used to grade a tossup answer
        return (((m.author == moderator) and m.content.casefold() in ['y','n']) or end_pred(m)) and m.channel == ctx.channel
    def mod_next(m): # used for advancing tossups after bonuses
        return (((m.author == moderator) and m.content.startswith('m next')) or end_pred(m)) and m.channel == ctx.channel
    async def take_answer(end_question,ans_player,edits_left=0,total_edits=0):
        cdepth = (total_edits - edits_left)/total_edits * 100 if total_edits > 0 else None
        cdepth = 100 if cdepth == 0 else cdepth
        try:
            msg = await client.wait_for('message', check=ans_player.pred,timeout=10)
        except asyncio.TimeoutError:
            add_points = -5 if end_question == False else 0
            await ctx.channel.send(f':x: `{add_points}`')
        else:
            if msg.content != 'm sim end':
                def find_ans(ans,key):
                    if ans.find(key)==-1:
                        return
                    else:
                        first = ans.find(key)+2
                    second = ans.find(key,first)
                    new_str = ans[first:second]
                    return new_str
                underlined_portion = find_ans(formatted_answer,'__')
                underlined_portion = find_ans(formatted_answer,'**') if underlined_portion == None else underlined_portion
                underlined_portion = underlined_portion.casefold() if underlined_portion else underlined_portion
                no_response = 0
                similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                if similarity > 80 or msg.content.casefold() == underlined_portion:
                    add_points = 15 if ('(*)' not in tu_msg.content and '(*)' in question) else 10
                    await ctx.channel.send(f'`{add_points}`')
                    await ctx.channel.send(f'ANSWER: {formatted_answer}')
                    correct = True
                else:
                    add_points = -5 if end_question == False else 0
                    await ctx.channel.send(f':x: `{add_points}`')
                    ans_player.answerlines_missed.append(raw_answer)
                    correct = False
                given_abbrev = msg.content.casefold().strip()
                real_abbrev = ''.join([x[0] for x in raw_answer.casefold().split()])
                if (10 <= similarity <= 75 or (msg.content.casefold() in formatted_answer.casefold()) or has_num(msg.content.casefold()) or has_num(raw_answer.casefold()) or given_abbrev == real_abbrev) and correct == False:   #;  where should this go follow m
                    await ans_player.author.send(f'ANSWER: {formatted_answer}')
                    await ans_player.author.send(f'Is the answer correct? Respond with `y` or `n`')
                    try:
                        msg = await client.wait_for('message', check=ans_player.any_pred,timeout=10)
                    except asyncio.TimeoutError:
                        None
                    else:
                        if msg.content != 'm sim end':
                            if msg.content.lower().startswith('n'):
                                add_points = -5 if end_question == False else 0
                                await ctx.channel.send(f':x: `{add_points}`')
                            elif msg.content.lower().startswith('y'):
                                correct = True
                                add_points = 15 if ('(*)' not in tu_msg.content and '(*)' in question) else 10
                                await ctx.channel.send(f'ANSWER: {formatted_answer}')
                                ans_player.answerlines_missed.remove(raw_answer)
                                await ctx.channel.send(f'`{add_points}`')
                            else:
                                add_points = -5 if end_question == False else 0
                                await ctx.channel.send('Not a valid response! :x: `-5`')
                        else:
                            return 'end'
            else:
                return 'end'
        return add_points,cdepth
    await ctx.channel.send('Do you want to practice with bonuses? (Y/N)')
    try:
        msg = await client.wait_for('message',check=pred,timeout=15)
    except asyncio.TimeoutError:
        await ctx.channel.send('Practice timed out...')
        return
    else:
        if msg.content.casefold().startswith('y'):
            await ctx.channel.send('Bonuses enabled :white_check_mark:.')
            bonuses = True
        elif msg.content.casefold().startswith('n'):
            await ctx.channel.send('Bonuses disabled :x:.')
            bonuses = False
        else:
            await ctx.channel.send('Not a valid response. Ending practice...')
            return
    class Team():
        def __init__(self, players, name):
            def team_pred(m):
                return m.author in [x.author for x in self.players] and m.channel == ctx.channel and not m.content.startswith('~')
            self.team_pred = team_pred
            self.players = players
            self.name = name
            self.team_points = 0
            self.bonus_points = 0
            self.tossups_heard = 0
            self.bonuses_heard = 0
            self.powers = 0
        def init_directory(self):
            self.directory = dict()
            for player in self.players:
                self.directory[player.author.id] = player
        def get_ppb(self,tossups_heard):
            return round(self.bonus_points/self.bonuses_heard,2) if self.bonuses_heard > 0 else 0
        def get_ppg(self,tossups_heard):
            return round(self.team_points/tossups_heard * 20,2)

    class game_info():
        def __init__(self):
            self.tossups = []
            self.dict_buzzers = dict()
            self.sort_buzzes = {15:0,10:1,0:2,-5:3}
        def get_spreadsheet(self):
            full_path = f'temp/{int(time.time())}_sim_results.csv'
            try:
                f = open(full_path,"x")
            except:
                os.remove(full_path)
                f = open(full_path,"x")
            f.close()
            with open(full_path, mode='a') as practice_csv:
                card_writer = csv.writer(practice_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                card_writer.writerow(['tossup_num','tossup_id','category','subcategory','powers','tens','zeros','negs'])
                for id,category,subcategory,tossup_num in self.tossups:
                    buzz_info = self.dict_buzzers.get(tossup_num)
                    powers = '\\,'.join(buzz_info[0])
                    tens = '\\,'.join(buzz_info[1])
                    zeros = '\\,'.join(buzz_info[2])
                    negs = '\\,'.join(buzz_info[3])
                    card_writer.writerow([tossup_num,id,category,subcategory,powers,tens,zeros,negs])
            return full_path
        def get_player_spreadsheet(self,a_team,b_team=None):
            full_path = f'temp/{int(time.time())}_sim_player_results.csv'
            try:
                f = open(full_path,"x")
            except:
                os.remove(full_path)
                f = open(full_path,"x")
            f.close()
            with open(full_path, mode='a') as practice_csv:
                card_writer = csv.writer(practice_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                card_writer.writerow(['Player','Powers','Tens','Negs','C-Depth'])
                if b_team:
                    for team in [a_team,b_team]:
                        for player in team.players:
                            card_writer.writerow([player.author.name,player.powers,player.tens,player.negs,player.get_cdepth()])
                else:
                    for player in a_team.players:
                        card_writer.writerow([player.author.name,player.powers,player.tens,player.negs,player.get_cdepth()])
            return full_path

    start = time.time()
    Team_A = Team([],'A Team')
    Team_B = Team([],'B Team')
    players = []
    game = True
    if not ffa:
        msg = await ctx.channel.send('React to this message to join a team!')
        await msg.add_reaction('🅰️')
        await msg.add_reaction('🇧')
    else:
        msg = await ctx.channel.send('React to this message to join the practice!')
        await msg.add_reaction('🅰️')
    while time.time() - start < 30:#change to 30 #FIX ME
        try:
            reaction,user = await client.wait_for('reaction_add', timeout=10,check=check)
        except asyncio.TimeoutError:
            None
        else:
            if user not in players:
                players.append(user)
                if str(reaction.emoji) == '🅰️':
                    Team_A.players.append(TK_Player(user,Team_A,ctx))
                else:
                    Team_B.players.append(TK_Player(user,Team_B,ctx))
            else:
                try:
                    await msg.remove_reaction(str(reaction.emoji),user)
                except:
                    await ctx.channel.send('Error. Please enable `manage messages` for the FACE role!')
                    return
    if not ffa:
        A_string = '```A TEAM: '
        B_string = '```B TEAM: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}' # append to string with new line
        for x in Team_B.players:
            B_string = B_string + f'\n{x.author.name}'
        practice_size = 2
        await ctx.channel.send(A_string+'```')
        await ctx.channel.send(B_string+'```')
    else:
        A_string = '```FFA: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}'
        practice_size = len(Team_A.players)
        await ctx.channel.send(A_string+'```')
    await ctx.channel.send('Ping the moderator within the next 30 seconds.')
    try:
        msg = await client.wait_for('message', check=moderator_pred, timeout=30)
    except asyncio.TimeoutError:
        await ctx.channel.send('No moderator added. Ending practice.')
        return
    else:
        moderator = msg.mentions[0]
        await ctx.channel.send(f'{moderator.name} is now the moderator.')
    instructions = "type **buzz** to buzz! You will be negged if you buzz incorrectly before the end of the question. Moderator: type `m next` to get the next question!"
    await ctx.channel.send(instructions)
    game = True
    tossup_num = 0
    next_num = 0
    Team_A.init_directory()
    Team_B.init_directory()
    directory = {**Team_A.directory, **Team_B.directory}

    new_numbers = await get_difficulty(difficulty,ctx)
    if new_numbers == None:
        return
    difficulty = new_numbers[:]
    orig_category = category
    tossups = await FACE.get_tk_tossup(category,difficulty)
    if tossups == None:
        await ctx.channel.send('Please check your category spellings. Do not use spaces within the `{}` when specifying multiple categories.')
        return
    elif tossups == 'not enough':
        await ctx.channel.send('Not enough tossups found!')
        return
    elif tossups == 'error':
        await ctx.channel.send('There was an error...please try again.')
        return
    else:
        no_response = 0
        pred_to_use = buzz_pred
    list_bonuses = await FACE.get_bonus(category,difficulty)
    if bonuses == None:
        await ctx.channel.send('Please check your category spellings. Do not use spaces within the `{}` when specifying multiple categories.')
        in_pk.remove(ctx.author.id)
        return
    elif bonuses == 'not enough':
        await ctx.channel.send('Not enough bonuses found!')
        in_pk.remove(ctx.author.id)
        return
    game_tracker = game_info()
    practice_sim_dict[ctx.channel.id] = [ffa,'sim',moderator,Team_A,Team_B,ctx]
    while game:
        if tossup_num > 0:
            tossups = await FACE.get_tk_tossup(category,difficulty)
            list_bonuses = await FACE.get_bonus(category,difficulty)
            if tossups == 'error' or list_bonuses == 'error':
                await ctx.channel.send('There was an error...please try again. Ending the practice.')
                break
            elif not tossups:
                await ctx.channel.send('There was an error...please try again. Ending the practice.')
                break
        for i,q in enumerate(tossups):
            Team_A.init_directory()
            Team_B.init_directory()
            directory = {**Team_A.directory, **Team_B.directory}
            players = [x.author for x in Team_A.players + Team_B.players]
            tossup_num = tossup_num+1
            if game == False:
                break
            buzzes = []
            await ctx.channel.send(f'\~\~\~\~\~\~\~\~\~\~\~\~**Tossup {tossup_num}**\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~')
            # try:
            question = q[0][0]
            raw_answer = q[0][2]
            formatted_answer = q[0][1]
            tk_difficulty = q[0][3]

            tossup_id = q[0][4]
            tossup_category = q[0][5]
            tossup_subcategory = q[0][6]
            game_tracker.tossups.append((tossup_id,tossup_category,tossup_subcategory,tossup_num))
            game_tracker.dict_buzzers[tossup_num] = [[],[],[],[]]

            words = q[2]
            num_words = len(q[2])
            sentences = q[3]
            max_words = q[1]
            edits = math.ceil(num_words/5)
            edits_left = edits-1

            points = 0
            possible_points = 0
            tournament = list_bonuses[i][0][1]
            leadin = list_bonuses[i][0][0]
            color = list_bonuses[i][0][3]
            pk_difficulty = list_bonuses[i][0][2]

            try:
                mark = question.find(words[4])+len(words[4])
            except:
                continue
            tu_msg = await ctx.channel.send(question[:mark])
            correct = False
            while edits_left > 0:
                if correct == True or len(buzzes) == practice_size:
                    break
                to_date = edits - edits_left
                if 4+(to_date*5) >= len(words):
                    looking = words[-1]
                else:
                    looking = words[4+(to_date*5)]
                mark = question.find(looking,mark)+len(looking)
                await tu_msg.edit(content=question[:mark])
                edits_left -= 1
                try:
                    buzz_msg = await client.wait_for('message',check=pred_to_use,timeout=2) #BOOKMARK
                except asyncio.TimeoutError:
                    None
                else:
                    if buzz_msg.content.casefold() in ['c sim end','m sim end']:
                        game = False
                        break
                    elif buzz_msg.content.casefold() == 'buzz':
                        buzzer =  directory.get(buzz_msg.author.id)
                        answering_team = buzzer.team if not ffa else buzzer
                        buzzes.append(answering_team)
                        await tu_msg.edit(content=question[:mark]+'**$**')
                        await ctx.channel.send(f'{buzz_msg.author.mention} buzzed :loudspeaker:')
                        res = await take_answer(False,buzzer,edits_left,edits)
                        if res == 'break_loop':
                            break
                        buzzer.update(res)
                        bin = game_tracker.sort_buzzes.get(res[0])
                        game_tracker.dict_buzzers[tossup_num][bin].append(buzzer.author.name)
                        if res[0] != 10 and res[0] != 15:
                            correct = False
                        else:
                            correct = True
                            bonus_pred_to_use = answering_team.team_pred if not ffa else buzzer.team.team_pred
                            bonus_team = answering_team if not ffa else buzzer.team
                            await tu_msg.edit(content=question[:mark]+'**$**'+question[mark:])
            if game == False:
                break
            start = time.time()
            while (not correct) and (len(buzzes) < practice_size) and time.time() - start < 10:
                try:
                    buzz_msg = await client.wait_for('message',check=pred_to_use,timeout=2)
                except asyncio.TimeoutError:
                    None
                else:
                    if buzz_msg.content.casefold() in ['c sim end','m sim end']:
                        game = False
                        break
                    if buzz_msg.content.casefold() == 'buzz':
                        buzzer =  directory.get(buzz_msg.author.id)
                        answering_team = buzzer.team if not ffa else buzzer
                        buzzes.append(answering_team)
                        await tu_msg.edit(content=question[:mark]+'**$**')
                        await ctx.channel.send(f'{buzz_msg.author.mention} buzzed :loudspeaker:')
                        res = await take_answer(True,buzzer)
                        buzzer.update(res)
                        bin = game_tracker.sort_buzzes.get(res[0])
                        game_tracker.dict_buzzers[tossup_num][bin].append(buzzer.author.name)
                        if res[0] != 10 and res[0] != 15:
                            correct = False
                        else:
                            bonus_pred_to_use = answering_team.team_pred if not ffa else buzzer.team.team_pred
                            bonus_team = answering_team if not ffa else buzzer.team
                            correct = True
                            await tu_msg.edit(content=question[:mark]+'**$**'+question[mark:])
            if not correct:
                await ctx.channel.send(f'This tossup goes dead...:headstone:\nAnswer:{formatted_answer}')
            if bonuses == True and correct == True: #FIX ME
                ans_player = bonus_team
                ans_player.bonuses_heard += 1
                for num in range(3):
                    question = list_bonuses[i][num+1][0]
                    formatted_answer = list_bonuses[i][num+1][1]
                    raw_answer = list_bonuses[i][num+1][2]
                    possible_points += 10
                    embed = discord.Embed (
                    title=f'Question {tossup_num} ~ {tournament}',
                    colour=	0x56cef0,
                    timestamp=datetime.datetime.now()
                    )
                    if color:
                        embed.colour = color
                    if num == 0:
                        embed.add_field(name='\u200b',value = f'{leadin}')
                    embed.add_field(name='\u200b',value = f'**---**         {question}',inline=False)
                    await ctx.channel.send(embed=embed)
                    try:
                        msg = await client.wait_for('message', check=bonus_pred_to_use,timeout=300)
                    except asyncio.TimeoutError:
                        None #FIX ME
                    else:
                        if msg.content.casefold() in ['c sim end','m sim end']:
                            game = False
                            break
                        def find_ans(ans,key):
                            if ans.find(key)==-1:
                                return
                            else:
                                first = ans.find(key)+2
                            second = ans.find(key,first)
                            new_str = ans[first:second]
                            return new_str
                        underlined_portion = find_ans(formatted_answer,'__')
                        underlined_portion = find_ans(formatted_answer,'**') if underlined_portion == None else underlined_portion
                        underlined_portion = underlined_portion.casefold() if underlined_portion else underlined_portion
                        no_response = 0
                        similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                        if similarity > 80 or msg.content.casefold() == underlined_portion:
                            ans_player.bonus_points += 10
                            points += 10
                            await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                            correct = True
                        else:
                            await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                            # ans_player.answerlines_missed.append((question,raw_answer))
                            correct = False
                        await ctx.channel.send(f'ANSWER: {formatted_answer}')
                        given_abbrev = msg.content.casefold().strip()
                        real_abbrev = ''.join([x[0] for x in raw_answer.casefold().split()])
                        if (20 <= similarity <= 80 or (msg.content.casefold() in formatted_answer.casefold()) or has_num(msg.content.casefold()) or has_num(raw_answer.casefold()) or given_abbrev == real_abbrev) and correct == False:   #;  where should this go follow m
                            await ctx.channel.send('Were you correct? Respond with `y` or `n`')
                            try:
                                msg = await client.wait_for('message', check=bonus_pred_to_use,timeout=10)
                            except asyncio.TimeoutError:
                                None
                            else:
                                if msg.content.casefold() in ['c sim end','m sim end']:
                                    game = False
                                    break
                                if msg.content.lower().startswith('n'):
                                        await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                elif msg.content.lower().startswith('y'):
                                    ans_player.bonus_points += 10
                                    # ans_player.answerlines_missed.remove((question,raw_answer))
                                    points += 10
                                    await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                else:
                                    await ctx.channel.send('Not a valid response!')
                if tossup_num == 1:
                    await ctx.channel.send('Use `m next` to get the next tossup.')
            if game == False:
                break
            try:
                msg = await client.wait_for('message',check=mod_next,timeout=60)
            except asyncio.TimeoutError:
                await ctx.channel.send('Timed out! Ending the practice...')
                game = False
                break
            else:
                if msg.content in ['c sim end','m sim end']:
                    game = False
                    break
                else:
                    continue
    del practice_sim_dict[ctx.channel.id]
    if tossup_num > 0:
        full_path = game_tracker.get_spreadsheet()
        current_time = datetime.datetime.now()
        with open(full_path, 'rb') as fp:
            await ctx.channel.send(file=discord.File(fp, f'Practice - {current_time.month}/{current_time.day} {current_time.hour}:{current_time.minute}.csv'))
        os.remove(full_path)
        full_path = game_tracker.get_player_spreadsheet(Team_A) if len(Team_B.players) == 0 else game_tracker.get_player_spreadsheet(Team_A,Team_B)
        current_time = datetime.datetime.now()
        with open(full_path, 'rb') as fp:
            await ctx.channel.send(file=discord.File(fp, f'Practice - {current_time.month}/{current_time.day} {current_time.hour}:{current_time.minute}_players.csv'))
        os.remove(full_path)
        embed = discord.Embed (
        title='Practice Stats',
        colour=	0x83e6d0,
        timestamp=datetime.datetime.now()
        )
        Team_A.players.sort(reverse=True,key=lambda x: x.total_points)
        Team_B.players.sort(reverse=True,key=lambda x: x.total_points)
        A_str = f'{Team_A.team_points} points\n{Team_A.get_ppg(tossup_num)} PP20TUH\n{Team_A.get_ppb(tossup_num)} PPB\n------------------------'
        for i,player in enumerate(Team_A.players):
            stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
            A_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}\nPP20TUH:{20*(player.total_points/tossup_num):.2f}'
        embed.add_field(name='**Team A**',value=A_str)
        B_str = f'{Team_B.team_points} points\n{Team_B.get_ppg(tossup_num)} PP20TUH\n{Team_B.get_ppb(tossup_num)} PPB\n------------------------'
        if not ffa:
            for i,player in enumerate(Team_B.players):
                stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
                B_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}\nPP20TUH:{20*(player.total_points/tossup_num):.2f}'
            embed.add_field(name='**Team B**',value=B_str)
        embed.set_footer(text='Good game!')
        await ctx.channel.send(embed=embed)
@client.command (name='join')
async def join(ctx):
    def pred(m):
        return m.channel == ctx.channel and m.author == ctx.author and m.content.casefold() in ['a','b']
    info = practice_sim_dict.get(ctx.channel.id)
    team_dict = {'a':3,'b':4}
    if info:
        ffa = info[0]
        cmd_type = info[1]
        moderator = info[2]
        if ffa == True:
            await ctx.channel.send(f'{moderator.mention} Approval for {ctx.author.name} to join? `y` or `n`.')
            def moderator_pred(m):
                return m.channel == ctx.channel and m.author == moderator and m.content.casefold() in ['y','n']
            try:
                msg = await client.wait_for('message',check=moderator_pred,timeout=20)
            except asyncio.TimeoutError:
                await ctx.channel.send('Timed out! Please try again!')
                return
            else:
                if msg.content.casefold() == 'y':
                    if cmd_type == 'sim':
                        info[3].players.append(TK_Player(ctx.author,info[3],ctx))
                        await ctx.channel.send('Joined! :white_check_mark:')
                    elif cmd_type =='practice':
                        info[3].players.append(PR_Player(ctx.author,info[3]))
                        await ctx.channel.send('Joined! :white_check_mark:')
                else:
                    await ctx.channel.send('Rejected...')
        else:
            await ctx.channel.send('Would you like to join the A team or B team? Respond with `A` or `B`')
            try:
                name_team = await client.wait_for('message',check=pred,timeout=15)
            except asyncio.TimeoutError:
                await ctx.channel.send('Timed out! Please try again!')
                return
            else:
                name_team = name_team.content.casefold()
                await ctx.channel.send(f'{moderator.mention} Approval for {ctx.author.name} to join the practice on team {name_team.capitalize()}? `y` or `n`.')
                def moderator_pred(m):
                    return m.channel == ctx.channel and m.author == moderator and m.content.casefold() in ['y','n']
                try:
                    msg = await client.wait_for('message',check=moderator_pred,timeout=20)
                except asyncio.TimeoutError:
                    await ctx.channel.send('Timed out! Please try again!')
                    return
                else:
                    if msg.content.casefold() == 'y':
                        if cmd_type == 'sim':
                            info[team_dict.get(name_team)].players.append(TK_Player(ctx.author,info[team_dict.get(name_team)],ctx))
                        elif cmd_type =='practice':
                            info[team_dict.get(name_team)].players.append(PR_Player(ctx.author,info[team_dict.get(name_team)]))
                        await ctx.channel.send('Added!')
                    else:
                        await ctx.channel.send('Rejected...')
    else:
        await ctx.channel.send('There is no practice or sim going on in this channel!')

@client.command (name='tournament')
async def tournament(ctx,*tournament):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    await ctx.channel.send('What category would you like to card? Don\'t respond or respond with `all` to card the entire tournament.')
    try:
        msg = await client.wait_for('message',timeout=10,check=pred)
    except asyncio.TimeoutError:
        category = None
    else:
        category = msg.content.lower()
        if category == 'all':
            category = None
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    if not await premium(guild_id,ctx):
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='This command is reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
        return
    if len(tournament) == 0:
        await ctx.channel.send('You used the wrong format! Use the command `m card *tournament*`, e.g. `m card PACE 2016`.')
        return
    tournament = ' '.join(tournament)
    results = await FACE.get_csv_tournament(tournament,category)
    if results == None:
        await ctx.channel.send('No tournaments found!')
        return
    elif results == 'invalid category':
        await ctx.channel.send('That is not a valid category! Use `m cats` to browse categories.')
        return
    full_path,total_cards,name = results
    with open(full_path, 'rb') as fp:
        await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {name.upper()} cards (click to download).csv'))
    await ctx.channel.send(f'Around {total_cards} cards made!')
    await asyncio.sleep(7)
    os.remove(full_path)

@client.command (name='card')
async def card(ctx,category=None,*terms):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    await add_count(guild_id)
    if category == None or terms == []:
        await ctx.channel.send('You used the wrong format! Use the command `m card *category* *[difficulty]* *term*`, e.g. `m card sci [3-7] proton` or `m card sci biology all`')#i need access to the other part plz
        return
    if ctx.author.id in carding:
        await ctx.channel.send('Please wait for your previous request to finish before starting another one.')
        return
    word = str()
    separated_terms = []
    new_numbers = []
    terms = list(terms)
    if 'filtered' in terms:
        if (not await premium(guild_id,ctx) or len(ctx.guild.members) > 50) and guild_id != 634580485951193089:
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Filtering your cards is reserved for premium servers with less than **50 members**!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            return
        raw = False
        terms.remove('filtered')
    else:
        raw = True
    new_numbers = await get_difficulty(terms,ctx,carding)
    for x in terms:
        if x[0] == '[':
            continue
        if x[-1] == ',':
            if len(word) == 0:
                word = x[:-1]
            else:
                word = word + ' ' + x[:-1]
            separated_terms.append(word)
            word = str()
        else:
            if len(word) == 0:
                word = x
            else:
                word = word + ' ' + x
    if word != '':
        separated_terms.append(word)
    if len(separated_terms) == 0:
        if not (await premium(guild_id,ctx) == True) or len(ctx.guild.members) > 50 and guild_id != 634580485951193089:
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Carding entire categories/subcategories is reserved for premium servers with **less than 50 members**! This feature is also restricted from trials.',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            return
        term_by_term = False
    else:
        term_by_term = True
    difficulty = new_numbers[:]
    carding.append(ctx.author.id)
    await ctx.channel.send(f'Beginning the carding process... Estimated time: `Up to five minutes...`')
    try:
        result = await FACE.get_csv(separated_terms,category,ctx.author.id,difficulty,term_by_term,raw)
    except:
        await ctx.channel.send('There was a problem! Please try again.')
        carding.remove(ctx.author.id)
        return
    if result == None:
        await ctx.channel.send('That is not a valid category!')
        carding.remove(ctx.author.id)
        return
    full_path, total_cards = result
    if full_path == None:
        await ctx.channel.send('That is not a valid category!')
        carding.remove(ctx.author.id)
        return
    with open(full_path, 'rb') as fp:
        try:
            await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {category} cards (click to download).csv'))
        except discord.errors.HTTPException:
            await ctx.channel.send('File size too large! Please try restricting your request (e.g. add difficulty parameters or use subcategories).')
    await ctx.channel.send(f'Around {total_cards} cards made!')
    await asyncio.sleep(7)
    os.remove(full_path)
    carding.remove(ctx.author.id)


@client.command (name='list')
async def freq(ctx,category=None,*difficulty):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    await add_count(guild_id)
    if category==None:
        await ctx.channel.send('You did not include a valid category! e.g. `m list fa`')
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m list *category* *[difficulty]*`, e.g. `m list sci [3]`')
        return
    if category == 'all':
        await ctx.channel.send('You cannot get frequency lists for `all`!')
        return
    str_version = ' '.join(list(difficulty)).strip()
    start = str_version.find('[')
    has_difficulty = False if start == -1 else True
    terms = str_version if has_difficulty == False else str_version[:start]
    difficulty = str_version[start:]
    if difficulty and difficulty[-1] != ']' and has_difficulty == True:
        await ctx.channel.send('Please specify difficulty last (e.g. `m list fa Beethoven [3]`,`m list fa [3]` or `m list fa`)')
        return
    difficulty = difficulty.strip().split(' ')
    difficulty = [x for x in difficulty if x]
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        return
    if len(difficulty) > 0:
        difficulty = await get_difficulty(list(difficulty),ctx,None)
    result = await FACE.get_frequency(category,difficulty,terms)
    if result == None:
        await ctx.channel.send('No results found!')
        return
    answers,coverage,color = result
    answers = [x for x in answers if x!=None and x!='' and x.lower()!='the']
    pages = []
    for i in range(10):
        temp_embed = discord.Embed(
            title=f'Frequency List For {category.upper()}: {len(answers)} results found (max. 50)',
            colour=	0xf7f7f7,
        )
        if color:
            temp_embed.colour = color
        slice = answers[(i)*5:(i+1)*5]
        if len(slice) == 0:
            break
        for num,x in enumerate(slice):
            temp_embed.add_field(name=f'**{(i)*5+(num+1)}.**',value=x,inline=False)
        temp_embed.set_footer(text='React with the emojis below to browse the list!')
        pages.append(temp_embed)
    if len(pages) > 0:
        browser = await ctx.channel.send(embed=pages[0])
    else:
        await ctx.channel.send('No results found :slight_frown:')
        return
    await browser.add_reaction('\u2B05')
    await browser.add_reaction('\u27A1')
    def check(reaction, user):
        nonlocal browser
        return (str(reaction.emoji) == '⬅' or str(reaction.emoji) == '➡') and user != client.user and reaction.message.id == browser.id and user.id == ctx.author.id
    start = time.time()
    page_num = 0
    if not await premium(guild_id,ctx):
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='Browsing frequency lists is reserved for premium servers (can show up to 100 answerlines instead of 5)!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
        return
    while time.time() - start < 30:
        try:
            reaction,user = await client.wait_for('reaction_add', timeout=10,check=check)
        except asyncio.TimeoutError:
            None
        else:
            if str(reaction.emoji) == '⬅':
                page_num -= 1
                if abs(page_num) > len(pages):
                    page_num = -1
            elif str(reaction.emoji) == '➡':
                page_num += 1
                if page_num >= len(pages):
                    page_num = 0
            try:
                await browser.remove_reaction(str(reaction.emoji),user)
            except:
                await ctx.channel.send('Error: Missing permissions. Please enable `manage messages` for the FACE role!')
                return
            start = time.time()
        await browser.edit(embed=pages[page_num])
    await browser.edit(content=f'{category.upper()} List closed (timed out) :lock:',embed=None)
    try:
        await browser.clear_reaction('\u2B05')
        await browser.clear_reaction('\u27A1')
    except:
        await ctx.channel.send('Please make sure the bot has `manage messages` permissions!')
@client.command (name='lookup')
async def lookup(ctx,category,*terms):
    try:
        await add_count(ctx.guild.id)
    except:
        None
    if category == None or terms == []:
        await ctx.channel.send('You used the wrong format! Use the command `m lookup *category* *[difficulty]* *term*`, e.g. `m lookup sci proton`')
        return
    term = ' '.join(terms)
    result = await FACE.lookup(term,category)
    if result == None:
        await ctx.channel.send('No results found!')
        return
    x,y = result
    plt.plot(x,y,markerfacecolor='red')
    plt.xlabel('Difficulty')
    plt.ylabel('Avg. appearence every 200 tossups)')
    plt.title(f'Frequency of {term.title()}')
    path = f'temp/{ctx.author.name}.png'
    plt.savefig(path,dpi=200)
    plt.clf()
    with open(path, 'rb') as fp:
        await ctx.channel.send(file=discord.File(fp))
    await asyncio.sleep(2)
    os.remove(path)


@client.command (name='thoth',aliases=['wizard'])
async def thoth(ctx):
    mydb,mycursor = mysql_connect() #connect to mysql
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel #for taking input
    async def take_answer(ctx): #generic function for taking input from user, returns the msg or returns false if timed out
        try:
            msg = await client.wait_for('message',check=pred,timeout=60)
        except asyncio.TimeoutError:
            return False
        else:
            return msg
    async def take_num_teams(ctx,stg_num): #function to take the number of teams at the tournament, stores in the mysql table
        await ctx.channel.send('How many teams will be at the tournament? Respond with a number.')
        msg = await take_answer(ctx)
        if msg == False: #if no message, the bot remembers what stage THOTH is on and then quits (in this case, it's on the "take number of teams" step) so that it can resume at the same step
            mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
            mydb.commit()
            return False
        else: #otherwise it stores the number of teams
            if msg.content.isnumeric():
                mycursor.execute(f'UPDATE tournament_info SET num_teams = %s',(int(msg.content),)) # %s formatting keeps us safe from mysql injection
                mydb.commit()
                await ctx.channel.send(f'{int(msg.content)} teams set :white_check_mark:')
            else:
                await ctx.channel.send('That is not a valid response! Use `m thoth` to resume the process.')
                mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
                mydb.commit()
                return False
    async def take_num_rounds(ctx,stg_num): #same structure as above function, takes the number of rounds
        await ctx.channel.send('How many rounds (Not including championship round)? Respond with a number.')
        msg = await take_answer(ctx)
        if msg == False:
            mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
            mydb.commit()
            return False
        else:
            if msg.content.isnumeric():
                mycursor.execute(f'UPDATE tournament_info SET num_rounds = %s',(int(msg.content),))
                mydb.commit()
                await ctx.channel.send(f'{int(msg.content)} rounds set :white_check_mark:')
            else:
                await ctx.channel.send('That is not a valid response! Use `m thoth` to resume the process.')
                mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
                mydb.commit()
                return False
    async def create_server(ctx,stg_num): #creates a Discord category for each room, and text + voice channels in each room for each round. The number of rooms is half of the number of teams (at any one time, two teams play each other)
        await ctx.channel.send('`Creating server...Please allow for up to 30 seconds. The bot will tell you when to continue.`')
        selection = f"SELECT num_teams,num_rounds FROM tournament_info WHERE server_id = {ctx.guild.id}"
        mycursor.execute(selection)
        num_teams,num_rounds = mycursor.fetchone()
        rooms = -(-num_teams // 2)
        try:
            for x in range(rooms):
                cat = await ctx.guild.create_category(name=f'Room {x+1}')
                for i in range(num_rounds):
                    await cat.create_text_channel(name=f'Room {x+1} Round {i+1} ')
                await cat.create_voice_channel(name=f'Room {x+1} Voice Channel')
        except discord.Forbidden:
            await ctx.channel.send('Please enable the **adminstrator permission** for FACE so that FACE can configure the server. This can be done by pressing the arrow next to the server name --> server settings --> roles --> FACE --> checking `administrator`.\n**Use `m thoth` to resume the process**')
            mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
            mydb.commit()
            return False
    async def generate_colors(ctx,stg_num): #generates 3 palettes for role colors that the user can pick from, sends the palettes and asks the user to pick one
        selection = f"SELECT num_teams FROM tournament_info WHERE server_id = {ctx.guild.id}"
        mycursor.execute(selection)
        num_teams = mycursor.fetchone()[0]
        results = [[],[],[]]
        first = (255, 255, 255)
        second = 'flor'
        third = 'neon'
        seeds = [first,second,third]
        for i in range(num_teams):
            for n,seed in enumerate(seeds):
                if seed == 'neon':
                    rand_neon = [random.randint(100,255),random.randint(100,255),0] #generates colors between 100 and 255 rgb value for red and green
                    random.shuffle(rand_neon)
                    color = tuple(rand_neon)
                elif seed == 'flor': #generates darker colors overall
                    rand_flor = [random.randint(50,255),random.randint(50,255),random.randint(50,255)]
                    random.shuffle(rand_flor)
                    color = tuple(rand_flor)
                else: #generates pastel colors by averaging the random color with (255,255,255) which is white
                    color = (int((random.randint(0,256)+seed[0])//2),int((random.randint(0,256)+seed[1])//2),int((random.randint(0,256)+seed[2])//2))
                results[n].append(color)
        paths = []
        for option,palette in enumerate(results): #generates an image with squares corresponding to the palette color, i'll send on discord
            color_photo = Image.new('RGB', (15*6, -(-num_teams//6)*15))
            col = 0
            y_cor = 0
            for row in range(-(-num_teams//6)):
                x_cor = 0
                for i in range(6):
                    if col >= len(palette):
                        break
                    color_photo.paste(Image.new('RGB', (15, 15), palette[col]),(x_cor, y_cor, x_cor + 15, y_cor + 15))
                    col += 1
                    x_cor += 15
                y_cor += 15
            path = f'temp/Tournament_{ctx.guild.id}_Option{option}.png'
            paths.append(path)
            color_photo.save(path)
        for path in paths:
            await ctx.channel.send(file=discord.File(path))
            os.remove(path)
        await ctx.channel.send('Respond with the number corresponding to the color palette you would like for the team colors! (`1`, `2`,or `3`)')
        msg = await take_answer(ctx)
        if msg == False:
            await ctx.channel.send('Timed out! Use `m thoth` to resume the process')
            mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
            mydb.commit()
            return False
        else:
            if msg.content in ['1','2','3']:
                palette = results[int(msg.content)-1]
                s = json.dumps(palette)
                mycursor.execute(f"UPDATE tournament_info SET palette = '{s}'")
                mydb.commit()
                await ctx.channel.send('Palette succesfully set! :white_check_mark:')
            else:
                await ctx.channel.send('That was not a valid response! Use `m thoth` to resume the process when you are ready.')
    async def take_teams(ctx,stg_num): #takes a spreadsheet of teams, format is https://docs.google.com/spreadsheets/d/1A_TsHtbt_qF5XUE4NwRCjnw3POz8341z0abIfF1wSGU/edit?usp=sharing
        def pred(m):
            return m.channel == ctx.channel and m.author == ctx.author
        await ctx.channel.send('Please send a spreadsheet with the team names and team members. Please use the same format as this example.')
        msg = await take_answer(ctx)
        if msg == False:
            await ctx.channel.send('Timed out! Use `m thoth` to resume the process when you are ready.')
            mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
            mydb.commit()
            return False
        else:
            path = f'temp/{ctx.author.id}_Tournament_Info.xlsx'
            spreadsheet = requests.get(msg.attachments[0].url,allow_redirects=True)
            open(path, 'wb').write(spreadsheet.content)
            df = pd.read_excel(path)
            df = df.dropna(axis = 0, how = 'all')
            columns = list(df.columns)
            if len(list(df.iterrows())):
                await ctx.channel.send('There are more teams in the spreadsheet than specified! Please alter the spreadsheet or change the number of teams using `m alter team_nums`')
                mycursor.execute(f"UPDATE tournament_info SET stage = {stg_num}")
                mydb.commit()
                return False
            for index, row in df.iterrows():
                team_header = columns[0]
                members = list(row)[1:]
                members = [x for x in members if pd.isnull(x) == False]
                str_members = ','.join(members)
                mycursor.execute(f"INSERT INTO Teams (server_id,role_id,team_name,members) VALUES ({ctx.guild.id},{index},'{row[team_header]}','{str_members}')")
            os.remove(path)
    async def make_team_roles(ctx,stg_num):
        await ctx.channel.send('`Creating roles...Please allow for up to 30 seconds. The bot will tell you when to continue.`')
        selection = f"SELECT palette FROM tournament_info WHERE server_id = {ctx.guild.id}"
        mycursor.execute(selection)
        palette = json.loads(mycursor.fetchone()[0])
        selection = f"SELECT team_name FROM Teams WHERE server_id = {ctx.guild.id}"
        mycursor.execute(selection)
        teams = mycursor.fetchall()
        for i,team_name in enumerate(teams):
            role = await ctx.guild.create_role(name=team_name, color=discord.Color(palette[i]))
            updater = f"UPDATE Teams SET role_id = {role.id}"
            mycursor.execute(updater)
        mydb.commit()
        await ctx.channel.send('Roles created! :white_check_mark:')

    stages = [take_num_teams,take_num_rounds,create_server,generate_colors,take_teams,make_team_roles] #stages of tournament set up, goes through list and picks up where it left off if error
    if is_owner(ctx) == True: #is owner for testing, public can't use
        mycursor.execute(f"SELECT * FROM tournament_info WHERE server_id = {ctx.guild.id}")
        row = mycursor.fetchone()
        if row == None: #if tournament is not in the table, it makes a new entry
            stage_num = 0
            await ctx.channel.send('Is this the server that you want to host the tournament in? `y` or `n`')
            try:
                msg = await client.wait_for('message',check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time! Please try again.')
                return
            else:
                if msg.content.lower() == 'n':
                    await ctx.channel.send('Please create a new server (the + button in the bottom left of the Discord screen) for the tournament and invite FACE to it.\n**Use `m thoth` in the new server to start the process**')
                    embed= discord.Embed(
                    title= 'Invite FACE!',
                    colour= 0xf0f0f0,
                    timestamp=datetime.datetime.now()
                    )
                    embed.add_field(name='Link',value='[invite FACE to your server](https://discord.com/oauth2/authorize?client_id=742880812961235105&scope=bot&permissions=121920)')
                    await ctx.send(embed = embed)
                    return
                elif msg.content.lower() == 'y':
                    await ctx.channel.send('**THOTH** (Tournament Hosting Overhauled to Hassle-Free) activated :writing_hand:')
                    mycursor.execute(f'INSERT INTO tournament_info (user_id,server_id) VALUES ({ctx.author.id},{ctx.guild.id})')
                    mydb.commit()
                else:
                    await ctx.channel.send('That is not a valid response! Please try again!')
                    return
        else: #tournament is already in table, resumes from last point
            stage_num = row[2]
            stage_num = 0 if stage_num == None else stage_num
            await ctx.channel.send('Resuming THOTH :writing_hand:')
            stages = stages[stage_num:]
        for i,func in enumerate(stages): #goes through stages
            result = await func(ctx,i)
            if result == False:
                return
            stage_num += 1
        mycursor.execute(f"UPDATE tournament_info SET stage = {stage_num}") #sets stage number
        mydb.commit()
@client.command (name='guilds')
async def guilds(ctx):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728:
        global our_guilds
        list_guilds = [(guild.name,guild.id) for guild in client.guilds if our_guilds.get(guild.id) != None]
        list_guilds.sort(key=lambda x:our_guilds.get(x[1]))
        list_guilds = [x[0] for x in list_guilds]
        await ctx.channel.send(list_guilds[:len(list_guilds)//4])
        await ctx.channel.send(list_guilds[len(list_guilds)//4:len(list_guilds)//2])
        await ctx.channel.send(list_guilds[len(list_guilds)//2:(3*len(list_guilds))//4])
        await ctx.channel.send(list_guilds[(3*len(list_guilds))//4:])
        # not_sent = True
        # pages = [guilds]
        # while not_sent:
        #     try:
        #         for page in pages:
        #             await ctx.channel.send(page)
        #         not_sent = False
        #     except:
        #         copy = pages.copy()
        #         pages.clear()
        #         for x in copy:
        #             pages.append(x[:len(x)//2])
        #             pages.append(x[len(x)//2:])
@client.command (name='review')
async def review(ctx):
    embed= discord.Embed(
    title= 'Card #1/10',
    colour= 0xf0f0f0,
    timestamp=datetime.datetime.now()
    )
    embed.add_field(name='This would be the front of the card.',value='\u200b')
    embed.set_footer(text='Add reactions based on what you would like to do.')
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('\u2B05')
    await msg.add_reaction('\u27A1')
    await msg.add_reaction('\U0001F534')
    await msg.add_reaction('\U0001F7E1')
    await msg.add_reaction('\U0001F7E2')

@client.event
async def on_message(msg):# we do not want the bot to reply to itself
    if msg.author == client.user:
        return
    def pred(m):
        return m.author == msg.author and m.channel == msg.channel
    await client.process_commands(msg)
#start up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global bot_guild
    global patron_role
    bot_guild = client.get_guild(767772426280894474)
    patron_role = bot_guild.get_role(767776503114366978)
    update_premium.start()
    update_trial.start()
    await client.change_presence( activity=discord.Game(name='c help',type=0), afk=False)
client.run(token)
