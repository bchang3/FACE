import sys
import re
import time
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import csv
import asyncio
import psycopg2
from sentence_similarity import compare_sentences
import random
from asgiref.sync import sync_to_async

def postgres_connect():
    conn = psycopg2.connect(
    host = 'localhost',
    user = 'ec2-user',
    password = 'TheCataclysm91$(*',
    database = 'quizdb'
    )
    cur = conn.cursor()
    return conn, cur
color_dict = {
    17:0x34cf53, #science
    15:0xc73232, #literature
    21:0xbd93db, # finearts
    14:0x2e1242, #myth
    18:0xfaed61, #history
    20:0x997b53, #geography
    16:0x9da4ab, #trash
    26:0x1882ed, #current events
    25: 0xf0ddb9, #philosophy
    22:0xf576be, # social sciences
    19:0xf7f5f6 #religion
}
first_cat_dict = {
    'sci': 'science',
    'fa': 'fine arts',
    'myth': 'mythology',
    'religion': 'religion',
    'trash': 'trash',
    'ss': 'social science',
    'lit': 'literature',
    'hist': 'history',
    'geo': 'geography',
    'ce':  'current events',
    'philo': 'philosophy'
}
first_subcat_dict = {
    'ce:usa': 'Current Events American',
    'ce:o': 'Current Events Other',
    'fa:audiovisual': 'Fine Arts Audiovisual',
    'fa:av': 'Fine Arts Audiovisual',
    'fa:american': 'Fine Arts American',
    'fa:usa': 'Fine Arts American',
    'fa:auditory': 'Fine Arts Auditory',
    'fa:a': 'Fine Arts Auditory',
    'afa': 'Fine Arts Auditory',
    'fa:british': 'Fine Arts British',
    'fa:brit': 'Fine Arts British',
    'fa:european': 'Fine Arts European',
    'fa:euro': 'Fine Arts European',
    'fa:opera': 'Fine Arts Opera',
    'fa:op': 'Fine Arts Opera',
    'fa:other': 'Fine Arts Other',
    'fa:o': 'Fine Arts Other',
    'ofa': 'Fine Arts Other',
    'fa:world': 'Fine Arts World',
    'fa:visual': 'Fine Arts Visual',
    'fa:v': 'Fine Arts Visual',
    'vfa': 'Fine Arts Visual',
    'geography:usa': 'Georgaphy American',
    'geo:usa': 'Geography American',
    'geography:world': 'Geography World',
    'geo:world': 'Geography World',
    'history:usa': 'History American',
    'hist:usa': 'History American',
    'history:brit': 'History British',
    'hist:brit': 'History British',
    'history:c': 'History Classical',
    'hist:c': 'History Classical',
    'history:euro': 'History European',
    'hist:euro': 'History European',
    'history:o': 'History Other',
    'hist:o': 'History Other',
    'history:world': 'History World',
    'hist:world': 'History World',
    'literature:usa': 'Literature American',
    'lit:usa': 'Literature American',
    'literature:brit': 'Literature British',
    'lit:brit': 'Literature British',
    'literature:c': 'Literature Classical',
    'lit:c': 'Literature Classical',
    'literature:euro': 'Literature European',
    'lit:euro': 'Literature European',
    'literature:o': 'Literature Other',
    'lit:o': 'Literature Other',
    'literature:world': 'Literature World',
    'lit:world': 'Literature World',
    'mythology:usa': 'Mythology American',
    'myth:usa': 'Mythology American',
    'mythology:cn': 'Mythology Chinese',
    'myth:cn': 'Mythology Chinese',
    'mythology:eg': 'Mythology Egyptian',
    'myth:eg': 'Mythology Egyptian',
    'mythology:gr': 'Mythology Greco-Roman',
    'myth:gr': 'Mythology Greco-Roman',
    'mythology:in': 'Mythology Indian',
    'myth:in': 'Mythology Indian',
    'mythology:jp': 'Mythology Japanese',
    'myth:jp': 'Mythology Japanese',
    'mythology:no': 'Mythology Norse',
    'myth:no': 'Mythology Norse',
    'mythology:oea': 'Mythology Other East Asian',
    'myth:oea': 'Mythology Other East Asian',
    'mythology:o': 'Mythology Other',
    'myth:o': 'Mythology Other',
    'philosophy:usa': 'Philosophy American',
    'philo:usa': 'Philosophy American',
    'philosophy:c': 'Philosophy Classical',
    'philo:c': 'Philosophy Classical',
    'philosophy:ea': 'Philosophy East Asian',
    'philo:ea': 'Philosophy East Asian',
    'philosophy:euro': 'Philosophy European',
    'philo:euro': 'Philosophy European',
    'philosophy:o': 'Philosophy Other',
    'philo:o': 'Philosophy Other',
    'religion:usa': 'Religion American',
    'reli:usa': 'Religion American',
    'religion:ch': 'Religion Christianity',
    'reli:ch': 'Religion Christianity',
    'religion:ea': 'Religion East Asian',
    'reli:ea': 'Religion East Asian',
    'religion:islam': 'Religion Islam',
    'reli:islam': 'Religion Islam',
    'reli:juda': 'Religion Judaism',
    'religion:juda': 'Religion Judaism',
    'religion:o': 'Religion Other',
    'reli:o': 'Religion Other',
    'science:usa': 'Science American',
    'sci:usa': 'Science American',
    'science:bio': 'Science Biology',
    'sci:bio': 'Science Biology',
    'science:chem': 'Science Chemistry',
    'sci:chem': 'Science Chemistry',
    'sci:cs': 'Science Computer Science',
    'science:cs': 'Science Computer Science',
    'sci:math': 'Science Math',
    'science:math': 'Science Math',
    'science:o': 'Science Other',
    'sci:o': 'Science Other',
    'science:physics': 'Science Physics',
    'sci:physics': 'Science Physics',
    'science:world': 'Science World',
    'sci:world': 'Science World',
    'ss:usa': 'Social Science American',
    'ss:econ': 'Social Science Economics',
    'ss:economics': 'Social Science Economics',
    'ss:linguistics': 'Social Science Linguistics',
    'ss:lang': 'Social Science Linguistics',
    'ss:o': 'Social Science Other',
    'ss:psychology': 'Social Science Psychology',
    'ss:psych': 'Social Science Psychology',
    'ss:sociology': 'Social Science Sociology',
    'ss:soci': 'Social Science Sociology',
    'trash:usa': 'Trash American',
    'trash:music': 'Trash Music',
    'trash:o': 'Trash Other',
    'trash:sports': 'Trash Sports',
    'trash:tv': 'Trash Television',
    'trash:vg': 'Trash Video Games',
}
conn, cur = postgres_connect()

cat_dict = dict()
cur.execute('SELECT * FROM categories')
cat_rows = cur.fetchall()
for row in cat_rows:
    cat_dict[row[1].casefold()] = int(row[0])
cat_dict['all'] = 'all'

subcat_dict = dict()
cur.execute('SELECT * FROM subcategories')
subcat_rows = cur.fetchall()
for row in subcat_rows:
    subcat_dict[row[1].casefold()] = int(row[0])

cur.execute('SELECT * FROM tournaments')
tournament_rows = cur.fetchall()
difficulty_dict = dict()
for row in tournament_rows:
    difficulty_dict[int(row[0])] = int(row[3])

def last_two(arr):
    new = (arr[1],arr[2])
    return new

async def get_tossup(query,category,difficulty):
    conn, cur = postgres_connect()
    subcategory = category
    if first_cat_dict.get(category.casefold()):
        category = first_cat_dict.get(category.casefold())
    elif first_subcat_dict.get(category.casefold()):
        subcategory = first_subcat_dict.get(category.casefold())
    orig_category = category
    category = cat_dict.get(category.casefold())
    orig_subcategory = subcategory
    subcategory = subcat_dict.get(subcategory.casefold())
    if category == None and subcategory == None:
        return None
    if category == 'all' and query != None:
        query = query.replace(' ',' & ')
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english','{query}')"
    elif query == None and subcategory == None:
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE category_id = '{category}'"
    elif query == None and subcategory != None:
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE subcategory_id = '{subcategory}'"
    else:
        query = query.replace(' ',' & ')
        if subcategory:
            executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english','{query}') AND subcategory_id = '{subcategory}'"
        else:
            executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english','{query}') AND category_id = '{category}'"
    cur.execute(executor)
    results = cur.fetchall()
    if len(difficulty) > 0:
        for i,res in enumerate(results[:]):
            if difficulty_dict.get(res[0]) not in difficulty:
                if res in results:
                    results.remove(res)
    results = list(map(last_two,results))
    return results
def get_cat_id(category_name):
    category = category_name
    if category_name in first_cat_dict:
        category = first_cat_dict.get(category_name).casefold()
    id = cat_dict.get(category)
    if id == None:
        if category_name in first_subcat_dict:
            category = first_subcat_dict.get(category_name).casefold()
        id = subcat_dict.get(category)
        if id:
            return f'subcategory_id = {id}'
        else:
            return None
    else:
        return f'category_id = {id}'
async def get_bonus(category,difficulty):
    conn, cur = postgres_connect()
    curly_search =  re.search(r'\{(.*?)\}',category)
    if curly_search:
        categories = curly_search.group(1).split(',')
        category_ids = list(map(get_cat_id,categories))
        if len(category_ids) == 0:
            return
        for x in category_ids.copy():
            if x == None:
                return
        conditions = ' OR '.join(category_ids)
    else:
        category_ids = get_cat_id(category)
        if category_ids == None:
            return
        conditions = category_ids
    if category == 'all':
        executor =  f"SELECT tournament_id,id,leadin,category_id FROM bonuses TABLESAMPLE BERNOULLI(0.5) LIMIT 1000"
        category = 'ALL'
    else:
        executor = f"SELECT tournament_id,id,leadin,category_id FROM bonuses WHERE " + conditions
    cur.execute(executor)
    results = cur.fetchall()#what is question a and s it's the question and the answer
    if len(difficulty) > 0:
        for i,res in enumerate(results[:]):
            if difficulty_dict.get(res[0]) not in difficulty:
                if res in results:
                    results.remove(res)
    num_bonuses = len(results)
    results = random.sample(results,5)
    bonuses = []
    for x in results:
        leadin = x[2]
        color = color_dict.get(int(x[3]))
        formatters = [('*',''), (';',''), ('<em>','*'), (r'</em>','*'), ('<strong>','**'), ('</strong>','**'), ('<u>','__'), ('</u>','__'), ('&lt','<'), ('&gt','>')]
        for char in formatters:
            leadin = leadin.replace(char[0],char[1])
        executor = f"SELECT formatted_text,formatted_answer FROM bonus_parts WHERE bonus_id = {x[1]} ORDER BY number"
        cur.execute(executor)
        parts = cur.fetchall()
        parts = list(map(new_complete_replace_line_bonus,parts))
        executor = f"SELECT name FROM tournaments WHERE id = {x[0]}"
        cur.execute(executor)
        name = cur.fetchone()[0]
        bonuses.append(((leadin,name,difficulty_dict.get(x[0]),color),parts[0],parts[1],parts[2]))
    misc = (num_bonuses,category.capitalize())
    bonuses.append(misc)
    return bonuses
async def get_tournament(tournament):
    conn, cur = postgres_connect()
    tournament = tournament.replace(' ',' & ')
    executor = f"SELECT id FROM tournaments WHERE to_tsvector('english',name) @@ to_tsquery('english','{tournament}')"
    cur.execute(executor)
    results = cur.fetchall()
    try:
        id = results[0][0]
    except:
        return None
    executor = f"SELECT text,answer FROM tossups WHERE tournament_id = {id}"
    cur.execute(executor)
    results = cur.fetchall()
    return results
def new_complete_replace_line(question):
    s = question[0]
    a = question[1]
    #divide between {} and ## in arr
    patterns = [r"\[\D.*\]",r"\&lt\D.*\&gt;", r'\(.*?\)',r'\{.*?\}', r" For 10 points, .*?\w ", r"For 10 points each.*", r"\n\d"]#r'&.*'
    replacements = ['No. ', 'no. ', 'et. al.', 'et al.','Â', '►', '\(', '\)', 'Sgt.']
    for i in patterns:
        replacement = re.sub(i, ' ', s)
        if i == " For 10 points, .*?\w ":
            replacement = re.sub(i, ' Name ', s)
        s = replacement
    for i in patterns:
        replacement = re.sub(i, ' ', a)
        a = replacement
    for x in range(len(replacements)):
        replacement = re.sub(replacements[x], ' ', s)
        if replacements[x]=='No.' or replacements[x]=='no.':
            replacement = re.sub(replacements[x], '#', s)
        elif replacements[x]=='et. al.' or replacements[x]=='et al.':
            replacement = re.sub(replacements[x], 'and others', s)
        elif replacements[x]=='Sgt.':
            replacement = re.sub(replacements[x], '', s)
        s = replacement
    s = re.sub(r"\s\n",'',s).strip().replace('  ', '')
    if ';' in a:
        a = a.replace(';','')
    final = (s, a.strip())
    return final
def new_complete_replace_line_bonus(question):
    s = question[0]
    a = question[1]
    orig_a = a
    formatters = [('*',''), (';',''), ('<em>','*'), (r'</em>','*'), ('<strong>','**'), ('</strong>','**'), ('<u>','__'), ('</u>','__'), ('&lt','<'), ('&gt','>')]
    for char in formatters:
        if char[0] in a:
            orig_a = orig_a.replace(char[0],char[1])
        if char[0] in s:
            s = s.replace(char[0],char[1])
    patterns = [r"\[\D.*\]",r"\&lt\D.*\&gt", r'\(.*?\)',r'\{.*?\}', r" For 10 points, .*?\w ", r"For 10 points each.*", r"\n\d"]#r'&.*'
    replacements = ['No. ', 'no. ', 'et. al.', 'et al.','Â', '►', '\(', '\)', 'Sgt.']
    for i in patterns:
        replacement = re.sub(i, ' ', s)
        s = replacement
    for i in patterns:
        replacement = re.sub(i, ' ', a)
        a = replacement
    for x in range(len(replacements)):
        replacement = re.sub(replacements[x], ' ', s)
        if replacements[x]=='No.' or replacements[x]=='no.':
            replacement = re.sub(replacements[x], '#', s)
        elif replacements[x]=='et. al.' or replacements[x]=='et al.':
            replacement = re.sub(replacements[x], 'and others', s)
        elif replacements[x]=='Sgt.':
            replacement = re.sub(replacements[x], '', s)
        s = replacement
    s = re.sub(r"\s\n",'',s).strip().replace('  ', '')
    for char in formatters:
        if char[0] in a:
            a = a.replace(char[0],'')
        if char[0] in s:
            s = s.replace(char[0],char[1])
    final = (s, orig_a.strip(),a.strip())
    return final
async def make_bonus_cards(cards,id):
    full_path = f"temp/pk_{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    f.close()
    with open(full_path, mode='a') as card_csv:
        for question,answer in cards:
            card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            card_writer.writerow([question,answer])
    return full_path
async def get_csv(terms,category,id, difficulty,term_by_term,raw):
    async def write_csv(tossups,raw,term=None):
        clues = []
        excess = 0
        nonlocal total_cards
        questions = list(map(new_complete_replace_line,tossups))
        for question,answer in questions:
            if term != None and term.casefold() not in answer.casefold():
                continue
            sentences = await sync_to_async(sent_tokenize)(question)
            with open(full_path, mode='a') as card_csv:
                for sentence in sentences:
                    sentence = sentence.replace('  ', ' ')
                    if sentence == '':
                        continue
                    duplicate = False
                    if raw == False:#open thebotfile
                        for clue in clues:
                            if clue[1] == answer:
                                score = await sync_to_async(compare_sentences)(clue[0],sentence)
                                if  score > 0.43:
                                    excess += 1
                                    duplicate = True
                                    break
                        if duplicate == True:
                            continue
                    card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    card_writer.writerow([sentence,answer])
                    clues.append((sentence,answer))
                    total_cards += 1
    total_cards = 0
    full_path = f"temp/{category}{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    f.close()
    if term_by_term == True:
        for term in terms:
            tossups = await get_tossup(term,category,difficulty)
            if tossups == None:
                return None
            await write_csv(tossups,raw,term)
    else:
        tossups = await get_tossup(None,category,difficulty)
        if tossups == None:
            return None
        await write_csv(tossups,raw)
    return full_path, total_cards
async def get_csv_tournament(tournament):
    def write_csv_tournament(tossups):
        clues = []
        global total_cards
        questions = list(map(new_complete_replace_line,tossups))
        for question,answer in questions:
            sentences = sent_tokenize(question)
            with open(full_path, mode='a') as card_csv:
                for sentence in sentences:
                    sentence = sentence.replace('  ', ' ')
                    if sentence == '':
                        continue
                    card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    card_writer.writerow([sentence,answer])
                    clues.append(sentence)
                    total_cards += 1
    global total_cards
    total_cards = 0
    full_path = f"temp/{tournament}{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    tossups = await get_tournament(tournament)
    if tossups == None:
        return None
    write_csv_tournament(tossups)
    return full_path, total_cards


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_bonus(17,None,[4,5,6]))
    # result = loop.run_until_complete(get_csv(['Albert Einstein'],'Science',5,[],True))
if __name__ == '__main__':
    main()
