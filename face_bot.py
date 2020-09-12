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
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

PREFIX = 'm '
token='NzQyODgwODEyOTYxMjM1MTA1.XzMjqw.SamNiyezNdCrzRzTQXh2h5SYsfE'
client = Bot(command_prefix=PREFIX)
client.remove_command('help')

in_pk = []
close_pk = []

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
    embed= discord.Embed(
    title= 'Help',
    colour= 0x00ff00,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
    embed.add_field(name="m instructions `name of command`", value="In depth instructions on a specific command. e.g. `m instructions card`", inline=False)
    embed.add_field(name="m cats", value="Displays the abbreviations used for categories", inline=False)
    embed.add_field(name="m card", value="m card `category` `difficulty` `term`")
    embed.add_field(name="m pk", value = "m pk `category` `difficulty` `timed`")
    await ctx.channel.send(embed=embed)


    #copy mafia embed
@client.command (name='instructions')
async def instructions(ctx,command = None):
    if command == None:
        await ctx.channel.send('Specify a command after m instructions, e.g. `m instructions card`')
    elif command == 'card':
        await ctx.channel.send('**---** Use the command `m card *category* [difficulty] *term(s)*`, e.g. `m card sci [3-5,7] proton`.\n**---** The bot will send a file that you can download and import into anki!\n**---** You can substitue `all` for either the category or for the terms if you want to card entire categories or card specific terms across categories.')
    elif command == 'pk':
        await ctx.channel.send('**---** m pk `category` `difficulty` `timed?`, e.g. `m pk sci [4-6] timed` or `m pk sci[4-6]`.\n***---*** Starts a pk practice session.\n **---** Use `m pk end` to end the game.')
@client.command (name='cats')
async def cats(ctx):
    await ctx.channel.send('`sci`, `fa`,`hist`,`geo`,`lit`,`ss`,`ce`,`myth`,`religion`,`trash`')
@client.command (name='pk')
async def pk(ctx,category=None,*difficulty):
    def close(id):
        global close_pk
        if id not in close_pk:
            return False
        return True
    global in_pk
    global close_pk
    if ctx.author.id in in_pk:
        if category == 'end':
            close_pk.append(ctx.author.id )
        else:
            await ctx.channel.send('You are already in a pk! Use `m pk end` to end a pk.')
        return
    in_pk.append(ctx.author.id)
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728 or ctx.guild.id == 634580485951193089:
        if category == None:
            await ctx.channel.send('You used the wrong format! Use the command `m pk *category* *[difficulty]*, e.g. `m pk sci [3-7]` or `m pk biology [1-9]`')
    new_numbers = []
    if 'timed' in difficulty:
        difficulty.remove('timed')
        timed = True
    else:
        timed = False
    for x in difficulty:
        if x[0] == '[':
            if len(new_numbers) > 0:
                await ctx.channel.send('You specified difficulty twice!')
                in_pk.remove(ctx.author.id)
                return
            if x[-1] != ']':
                await ctx.channel.send('Please do not use spaces when specifying difficulty!')
                in_pk.remove(ctx.author.id)
                return
            else:
                numbers = x[1:-1]
                if len(numbers) == 0:
                    await ctx.channel.send('You didn\'t put anything in the brackets!')
                    in_pk.remove(ctx.author.id)
                    return
                numbers = numbers.split(',')
                for entry in numbers:
                    if '-' in entry:
                        for num in list(range(int(entry[0]),int(entry[-1])+1)):
                            new_numbers.append(num)
                    else:
                        new_numbers.append(entry)
                new_numbers = list(map(int,new_numbers))
                new_numbers = list(set(new_numbers))
    difficulty = new_numbers[:]
    bonuses = await FACE.get_bonus(category,difficulty)
    if bonuses == None:
        await ctx.channel.send('That is not a valid category!')
        in_pk.remove(ctx.author.id)
        return
    else:
        game_end = False
        total_points = 0
        bonuses_heard = 0
        id = ctx.author.id
        while True and game_end == False and close(id) == False:
            bonuses = await FACE.get_bonus(category,difficulty)
            no_response = 0
            for i in range(5):
                if game_end == True or close(id) == True:
                    break
                points = 0
                possible_points = 0
                for num in range(3):
                    if game_end == True or close(id) == True:
                        break
                    possible_points += 10
                    embed = discord.Embed (
                    title=f'Question {i+1} ~ {bonuses[i][0][1]}',
                    colour=	0x56cef0,
                    timestamp=datetime.datetime.now()
                    )
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    if num == 0:
                        embed.add_field(name='\u200b',value = f'{bonuses[i][0][0]}')
                    embed.add_field(name='\u200b',value = f'**---**         {bonuses[i][num+1][0]}',inline=False)
                    if timed == True:
                        embed.set_footer(text='You have 16 seconds...')
                    await ctx.channel.send(embed=embed)
                    try:
                        if timed == True:
                            msg = await client.wait_for('message', check=pred,timeout=16)
                        else:
                            msg = await client.wait_for('message', check=pred,timeout=300)
                    except asyncio.TimeoutError:
                        await ctx.channel.send(bonuses[i][num+1][1])
                        if no_response >= 4:
                            embed = discord.Embed (
                            title=f'PK RESULTS:',
                            colour=	0x303845,
                            timestamp=datetime.datetime.now()
                            )
                            embed.set_thumbnail(url=ctx.author.avatar_url)
                            if bonuses_heard == 0:
                                ppb = 0
                            else:
                                ppb = total_points/bonuses_heard
                            embed.add_field(name='**PPB**:',value=f'{ppb:.3f}')
                            await ctx.channel.send(embed=embed)
                            game_end = True
                            break
                        no_response += 1
                    else:
                        no_response = 0
                        similarity = fuzz.ratio(bonuses[i][num+1][2].casefold(),msg.content.casefold())
                        if similarity > 75:
                            points += 10
                            await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                            correct = True
                        else:
                            await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                            correct = False
                        await ctx.channel.send(f'ANSWER: {bonuses[i][num+1][1]}')
                        if 20 <= similarity <= 75:   #;  where should this go follow m
                            await ctx.channel.send('Were you correct? Respond with `y` or `n`')
                            try:
                                msg = await client.wait_for('message', check=pred,timeout=10)
                            except asyncio.TimeoutError:
                                None
                            else:
                                if msg.content.lower().startswith('n'):
                                        await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                elif msg.content.lower().startswith('y'):
                                    points += 10
                                    await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                else:
                                    await ctx.channel.send('Not a valid response!')
                        await ctx.channel.send(f'Similarity is {fuzz.ratio(bonuses[i][num+1][2].casefold(),msg.content.casefold())}')
                    await asyncio.sleep(1)
                total_points += points
                await asyncio.sleep(5)
                bonuses_heard += 1
                # embed.add_field(name = f'{num+1}.',value = f'{bonuses[i][num+1][1]}',inline=False)
        if id in close_pk:
            close_pk.remove(id)
            embed = discord.Embed (
            title=f'PK RESULTS:',
            colour=	0x303845,
            timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            if bonuses_heard == 0:
                ppb = 0
            else:
                ppb = total_points/bonuses_heard
            embed.add_field(name='**PPB**:',value=f'{ppb:.3f}')
            await ctx.channel.send(embed=embed)
        if id in in_pk:
            in_pk.remove(id)
@client.command (name='practice')
async def practice(ctx):
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == ':b:' or str(reaction.emoji) == ':regional_indicator_b:' or str(reaction.emoji) == ':a:' or str(reaction.emoji) == ':regional_indicator_a:'

@client.command (name='card')
async def card(ctx,category=None,*terms):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728 or ctx.guild.id == 634580485951193089:
        if category == None or terms == None:
            await ctx.channel.send('You used the wrong format! Use the command `m card *category* *[difficulty]* *term*`, e.g. `m card sci [3-7] proton` or `m card sci biology all`')#i need access to the other part plz
        word = str()
        separated_terms = []
        new_numbers = []
        terms = list(terms)
        if 'all' in terms:
            await ctx.channel.send('`all` has been temporarily disabled')
            return
            # term_by_term = False
            # terms.remove('all')
        else:
            term_by_term = True
        if 'raw' in terms:
            raw = True
            terms.remove('raw')
        else:
            raw = False
        for x in terms:
            if x[0] == '[':
                if len(new_numbers) > 0:
                    await ctx.channel.send('You specified difficulty twice!')
                    return
                if x[-1] != ']':
                    await ctx.channel.send('Please do not use spaces when specifying difficulty!')
                    return
                else:
                    numbers = x[1:-1]
                    if len(numbers) == 0:
                        await ctx.channel.send('You didn\'t put anything in the brackets!')
                        return
                    numbers = numbers.split(',')
                    for entry in numbers:
                        if '-' in entry:
                            for num in list(range(int(entry[0]),int(entry[-1])+1)):
                                new_numbers.append(num)
                        else:
                            new_numbers.append(entry)
                    new_numbers = list(map(int,new_numbers))
                    new_numbers = list(set(new_numbers))
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
            term_by_term = False
        difficulty = new_numbers[:]
        await ctx.channel.send(f'Beginning the carding process... Estimated time: `{len(separated_terms)/8.6:.4f} seconds`')
        # try:
        result = await FACE.get_csv(separated_terms,category,ctx.author.id,difficulty,term_by_term,raw)
        if result == None:
            await ctx.channel.send('That is not a valid category!')
            return
        full_path, total_cards = result
        # except:
        #     await ctx.channel.send('There was a problem! Please try again.')
        #     return
        if full_path == None:
            await ctx.channel.send('That is not a valid category!')
            return
        with open(full_path, 'rb') as fp:
            await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {category} cards (click to download).csv'))
        await ctx.channel.send(f'Around {total_cards} cards made!')
        await asyncio.sleep(7)
        os.remove(full_path)
    else:
        await ctx.channel.send('Sorry, this command is reserved. :peach:')
@client.command (name='info',aliases=['details'])
async def info(ctx):
    embed = discord.Embed (
    title='FACE',
    colour=	0x7d99ff,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
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
    await client.change_presence( activity=discord.Game(name='m help',type=0), afk=False)
client.run(token)
