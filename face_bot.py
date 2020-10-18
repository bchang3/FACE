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

PREFIX = ['m ','M ']
token='NzQyODgwODEyOTYxMjM1MTA1.XzMjqw.SamNiyezNdCrzRzTQXh2h5SYsfE'
client = Bot(command_prefix=PREFIX)
client.remove_command('help')

in_pk = []
close_pk = []
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
def premium(id):
    mydb,mycursor = mysql_connect()
    mycursor.execute(f'SELECT premium FROM premium_servers WHERE server_id = {id}')
    premium = mycursor.fetchone()
    if premium:
        return True
    else:
        return False
async def get_difficulty(difficulty,ctx,in_list):
    new_numbers = []
    for x in difficulty:
        if x[0] == '[':
            if len(new_numbers) > 0:
                await ctx.channel.send('You specified difficulty twice!')
                in_list.remove(ctx.author.id)
                return
            if x[-1] != ']':
                await ctx.channel.send('Please do not use spaces when specifying difficulty!')
                in_list.remove(ctx.author.id)
                return
            else:
                numbers = x[1:-1]
                if len(numbers) == 0:
                    await ctx.channel.send('You didn\'t put anything in the brackets!')
                    in_list.remove(ctx.author.id)
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
    return new_numbers
@client.command (name='shutdown')
async def kill(ctx):
    if is_owner(ctx):
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
    embed.add_field(name="m pk", value = "m pk `category` `[optional] difficulty` `[optional] team` `[optional] comp` `[optional] timed`")
    embed.add_field(name="m tournament", value = "m tournament `tournament name`")
    await ctx.channel.send(embed=embed)
    #copy mafia embed
@client.command (name='instructions')
async def instructions(ctx,command = None):
    if command == None:
        await ctx.channel.send('Specify a command after m instructions, e.g. `m instructions card`')
    elif command == 'card':
        await ctx.channel.send('**---** Use the command `m card *category* [difficulty] *term(s)*`, e.g. `m card sci [3-5,7] proton`.\n**---** The bot will send a file that you can download and import into anki!\n**---** You can substitue `all` for either the category or for the terms if you want to card entire categories or card specific terms across categories.\n**---** Use the keyword `filtered` at the end of your command to remove similar cards and make your review more efficient. (e.g. `m card sci proton filtered`)')
    elif command == 'tournament':
        await ctx.channel.send('***---*** Use `m tournament *tournament name*`\n***---*** The cards will be from the tournament with the closest name, try to be as specific as possible.')
    elif command == 'pk':
        await ctx.channel.send('***---*** Starts a pk practice session.\n**---** m pk `category` `difficulty` `game_mode` `timed?`, e.g. `m pk sci [4-6] timed` or `m pk sci[4-6]`.\n***---*** Use `team` or `comp` to make a team pk or a competitive pk, e.g. `m pk all [3] team`, `m pk sci [4-6] comp`\n**---** Use `{}` for multiple categories, e.g. `m pk {sci,myth}`\n**---** Use `m pk end` to end the game.\n**---** Use `~` before your messages to talk during the pk. e.g. `~that was a bad question`')
@client.command (name='cats')
async def cats(ctx):
    embed = cat_embed
    embed.timestamp = datetime.datetime.now()
    await ctx.channel.send(embed=embed)
@client.command(name='subcats')
async def subcats(ctx,cat=None):
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
@client.command (name='pk')
async def pk(ctx,category=None,*difficulty):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    def close(id):
        global close_pk
        if id not in close_pk:
            return False
        return True
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith('~')
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
            if comp_pk:
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
            else:
                embed.add_field(name='**PPB**:',value=f'{ppb:.3f}')
                embed.add_field(name='30 30 30:',value=f'{self.thirties}',inline = True)
                embed.add_field(name='Total Points:',value=f'{self.total_points}',inline = True)
            embed.add_field(name='Avg diff.', value=f'{self.get_diff():.2f}')
            embed.add_field(name='Category',value=f'{category}')
            embed.add_field(name='Bonuses Seen:',value=f'{self.bonuses_heard}',inline = True)
            if premium(guild_id):
                for player in self.members:
                    await self.get_cards(player.answerlines_missed,player)
            if is_team == True:
                for player in self.members:
                    embed.add_field(name=f'{player.author.name}:',value =f'{player.points} total points',inline=False)
            return embed
        async def get_cards(self,cards,player):
            full_path = await FACE.make_bonus_cards(cards,player.author.id)
            await ctx.channel.send(f'{player.author.mention},Would you like PK review cards? Respond with `n` for no and `y` for yes.')
            try:
                msg = await client.wait_for('message',check=pred,timeout=20)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time. Deleting PK cards...')
            else:
                if msg.content != 'n':
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
    if ctx.author.id in in_pk:
        if category == 'end':
            close_pk.append(ctx.author.id)
            await ctx.channel.send('Ending the pk...')
        elif category == 'end--force':
            if ctx.author.id in close_pk:
                close_pk.remove(ctx.author.id)
            in_pk.remove(ctx.author.id)
        else:
            await ctx.channel.send('You are already in a pk! Use `m pk end` to end a pk.')
        return
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
    team = [Player(ctx.author,pred)]
    if 'team' in difficulty:
        if not premium(guild_id):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Team PKs are reserved for premium servers!',value='Access exclusive perks [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLj65iUKyj0nV8hP7hjZ9-XDJ3dpL4LRmm&ab_channel=RickAstleyVEVO)!')
            await ctx.channel.send(embed=embed)
            in_pk.remove(ctx.author)
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
                    in_pk.remove(ctx.author)
                    return
    elif 'comp' in difficulty:
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
                comp_pk = True
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
    else:
        num_bonuses = bonuses[-1][0]
        await ctx.channel.send(f'{num_bonuses} bonuses found!')
        category = bonuses[-1][1]
        game_end = False
        id = ctx.author.id
        team = Team(team)
        first_time = True
        while True and game_end == False and close(id) == False:
            if not first_time:
                bonuses = await FACE.get_bonus(orig_category,difficulty)
            if bonuses == None:
                await ctx.channel.send('There was an error :slight_frown:. Ending the pk.')
                close_pk.append(id)
                break
            for i in range(4):
                if comp_pk == True:
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
                            underlined_portion = re.search('\*\*__(.*)__\*\*',formatted_answer)
                            if underlined_portion:
                                underlined_portion = underlined_portion.group(1).casefold()
                            else:
                                underlined_portion = re.search('\*\*(.*)\*\*',formatted_answer)
                                if underlined_portion:
                                    underlined_portion = underlined_portion.group(1).casefold()
                            no_response = 0
                            similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                            await ctx.channel.send(underlined_portion)
                            if similarity > 75 or msg.content.casefold() == underlined_portion:
                                ans_player.points += 10
                                points += 10
                                await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                correct = True
                            else:
                                await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                ans_player.answerlines_missed.append((question,raw_answer))
                                correct = False
                            await ctx.channel.send(f'ANSWER: {formatted_answer}')
                            if (25 <= similarity <= 75 or (msg.content.casefold() in formatted_answer.casefold())) and correct == False:   #;  where should this go follow m
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
                    await asyncio.sleep(1)
                if id not in close_pk and skip == False:
                    player_up.update(points,pk_difficulty)
                    await asyncio.sleep(2)
            first_time = False
        if id in close_pk:
            close_pk.remove(id)
            embed = await team.get_embed(category,comp_pk,is_team,guild_id)
            await ctx.channel.send(embed=embed)
        if id in in_pk:
            in_pk.remove(id)
@client.command (name='practice')
async def practice(ctx):
    def pred(m):
        return m.author == ctx.author
    def check(reaction, user):
        nonlocal msg
        return (str(reaction.emoji) == '🇧' or str(reaction.emoji) == '🅰️') and user != client.user and reaction.message.id == msg.id
    class Team():
        def __init__(self, captain, players, name):
            self.captain = captain
            self.players = players
            self.name = name
            self.team_points = 0
        class Player():
            def __init__(self,author,pred):
                self.author = author
                self.total_points = 0
                self.tossups_heard = 0
                self.powers = 0
                self.tens = 0
                self.negs = 0
            def update(self,points):
                self.total_points += points
                self.difficulties.append(pk_difficulty)
                self.tossups_heard += 1
                if points == 15:
                    self.powers += 1
                elif points == 10:
                    self.tens += 1
                elif points == -5:
                    self.negs += 1

    start = time.time()
    A_members = []
    B_members = []
    A_points = 0
    B_points = 0
    moderator = ''
    game = True
    msg = await ctx.channel.send('React to this message to join a team!')
    await msg.add_reaction('🅰️')
    await msg.add_reaction('🇧')
    #await msg.add_reaction('')
    while time.time() - start < 10:#make 30
        try:
            reaction,user = await client.wait_for('reaction_add', timeout=10,check=check)
        except asyncio.TimeoutError:
            None
        else:
            if user not in A_members and user not in B_members:
                if str(reaction.emoji) == '🅰️':
                    A_members.append(user)
                else:
                    B_members.append(user)
            else:
                await msg.remove_reaction(str(reaction.emoji),user)
    A_string = '```A TEAM: '
    B_string = '```B TEAM: '
    for x in A_members:
        A_string = A_string + f'\n{x.name} A' # append to string with new line
    for x in B_members:
        B_string = B_string + f'\n{x.name} B'
    await ctx.channel.send(A_string+'```')
    await ctx.channel.send(B_string+'```')
    await ctx.channel.send('Ping moderator')
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await client.wait_for('message', check=pred, timeout=30.0)
        await ctx.channel.send('Thirty seconds to ping mod.')
    except asyncio.TimeoutError:
        await channel.send('Took too long')
    else:
        moderator=msg.mentions[0]
        await ctx.channel.send(f'{moderator.name[0:-5]} is now the moderator.')
        await ctx.channel.send('here')
    def pred(m):
            return m.author == moderator and m.channel == ctx.channel and m.content.startswith('~')
    game=True
    while game:
        try:
            msg = await client.wait_for('message', check=pred, timeout=30.0)
        except asyncio.TimeoutError:
            await channel.send('Too too long')
        else:
            if msg[0]=='~':
                None
            elif msg[0:1].casefold()=='tu':
                None
            elif msg[0:4].casefold()=='bonus':
                None
            elif msg[0:2].casefold()=='neg':
                None
@client.command (name='tournament')
async def tournament(ctx,*tournament):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    if not premium(guild_id):
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='This command is reserved for premium servers!',value='Access exclusive perks [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLj65iUKyj0nV8hP7hjZ9-XDJ3dpL4LRmm&ab_channel=RickAstleyVEVO)!')
        await ctx.channel.send(embed=embed)
        return
    if len(tournament) == 0:
        await ctx.channel.send('You used the wrong format! Use the command `m card *tournament*`, e.g. `m card PACE 2016`.')
        return
    tournament = ' '.join(tournament)
    result = await FACE.get_csv_tournament(tournament)
    results = result
    if results == None:
        await ctx.channel.send('No tournaments found!')
        return
    full_path,total_cards = results
    with open(full_path, 'rb') as fp:
        await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {tournament} cards (click to download).csv'))
    await ctx.channel.send(f'Around {total_cards} cards made!')
    await asyncio.sleep(7)
    os.remove(full_path)

@client.command (name='card')
async def card(ctx,category=None,*terms):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728 or ctx.guild.id == 634580485951193089:
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
            if not premium(guild_id):
                embed = discord.Embed (
                title='FACE Bot',
                colour=	0x7dffba,
                )
                embed.add_field(name='Filtering your cards is reserved for premium servers!',value='Access exclusive perks [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLj65iUKyj0nV8hP7hjZ9-XDJ3dpL4LRmm&ab_channel=RickAstleyVEVO)!')
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
            if not premium(guild_id):
                embed = discord.Embed (
                title='FACE Bot',
                colour=	0x7dffba,
                )
                embed.add_field(name='Carding entire categories/subcategories is reserved for premium servers!',value='Access exclusive perks [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLj65iUKyj0nV8hP7hjZ9-XDJ3dpL4LRmm&ab_channel=RickAstleyVEVO)!')
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

    #copy mafia embed
@client.event
async def on_message(msg):# we do not want the bot to reply to itself
    if msg.author == client.user:
        return
    # if msg.guild.id == 634580485951193089 or msg.channel.id == 742885307304902727:
    #     test1 = client.get_channel(742885307304902727)
    #     if len(msg.mentions)>0:
    #         # await msg.channel.send(f'{msg.author.mention} pinged')
    #         await test1.send(f'{msg.author.mention} pinged')
    if msg.content == 'm':
        stockm = ['\U0001F1F8','\U0001F1F9','\U0001F1F4','\U0001F1E8','\U0001F1F0','\u24c2']
        for reaction in stockm:
            await msg.add_reaction(reaction)

    def pred(m):
        return m.author == msg.author and m.channel == msg.channel
    # if ctx.author.id==248640104606859264:
    #     await ctx.channel.send(ctx.author.mention+' STOP') KEVIN STOP
    await client.process_commands(msg)

#start up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence( activity=discord.Game(name='m help',type=0), afk=False)
client.run(token)
