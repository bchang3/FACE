import sys
import re
import time
from fake_useragent import UserAgent
import pickle
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import csv
import asyncio
import psycopg2
from sentence_similarity import compare_sentences
import random

def postgres_connect():
    conn = psycopg2.connect(
    host = 'localhost',
    user = 'KevinChang',
    database = 'quizdb'
    )
    cur = conn.cursor()
    return conn, cur
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
    'religion:christianity': 'Religion Christianity',
    'religion:c': 'Religion Christianity',
    'science:computer-science': 'Science Computer Science',
    'sci:cs': 'Science Computer Science',
    'science:cs': 'Science Computer Science'
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

async def get_tossup(query,category,subcategory,difficulty):
    conn, cur = postgres_connect()
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
async def get_bonus(category,difficulty):
    conn, cur = postgres_connect()
    subcategory = category
    if first_cat_dict.get(category.casefold()):
        category = first_cat_dict.get(category.casefold())
    elif first_subcat_dict.get(category.casefold()):
        subcategory = first_subcat_dict.get(category.casefold())
    category = cat_dict.get(category.casefold())
    subcategory = subcat_dict.get(subcategory.casefold())
    if category == None and subcategory == None:
        return None
    sub_num = None
    if category == 'all':
        executor = f"SELECT tournament_id,id,leadin FROM bonuses WHERE category_id = {category} LIMIT 1000"
    elif subcategory == None:
        executor = f"SELECT tournament_id,id,leadin FROM bonuses WHERE category_id = {category}"
    else:
        executor = f"SELECT tournament_id,id,leadin FROM bonuses WHERE subcategory_id = {subcategory}"
    cur.execute(executor)
    results = cur.fetchall()
    if len(difficulty) > 0:
        for i,res in enumerate(results[:]):
            if difficulty_dict.get(res[0]) not in difficulty:
                if res in results:
                    results.remove(res)
    results = random.sample(results,5)
    bonuses = []
    for x in results:
        executor = f"SELECT text,answer FROM bonus_parts WHERE bonus_id = {x[1]}"
        cur.execute(executor)
        parts = cur.fetchall()
        parts = list(map(new_complete_replace_line_bonus,parts))
        executor = f"SELECT name FROM tournaments WHERE id = {x[0]}"
        cur.execute(executor)
        name = cur.fetchone()[0]
        print(name)
        bonuses.append(((x[2],name),parts[0],parts[1],parts[2]))
    return bonuses
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
    if ';' in a:
        a = a.replace(';','')
    final = (s, orig_a.strip(),a.strip())
    return final
async def get_csv(terms,category,id, difficulty,term_by_term,raw):
    def write_csv(tossups,term,raw):
        clues = []
        global total_cards
        questions = list(map(new_complete_replace_line,tossups))
        for question,answer in questions:
            if term.casefold() not in answer.casefold():
                continue
            sentences = sent_tokenize(question)
            with open(full_path, mode='a') as card_csv:
                for sentence in sentences:
                    sentence = sentence.replace('  ', ' ')
                    if sentence == '':
                        continue
                    duplicate = False
                    if raw == False:
                        for clue in clues:
                            score = compare_sentences(clue,sentence)
                            if  score > 0.43:
                                # print(f'**{score}**',sentence,'**vs.**',clue)
                                duplicate = True
                                break
                        if duplicate == True:
                            continue
                    card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    card_writer.writerow([sentence,answer])
                    clues.append(sentence)
                    total_cards += 1
    global total_cards
    total_cards = 0
    full_path = f"Desktop/discordpy/temp/{category}{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    f.close()
    if first_cat_dict.get(category.casefold()):
        category = first_cat_dict.get(category.casefold())
    num = cat_dict.get(category.casefold())
    sub_num = None
    if num == None:
        return None
    if term_by_term == True:
        for term in terms:
            tossups = await get_tossup(term, num, sub_num,difficulty)
            write_csv(tossups,term,raw)
    else:
        tossups = await get_tossup(None, num, sub_num, difficulty)
        write_csv(tossups,term,raw)
    return full_path, total_cards

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_bonus(17,None,[4,5,6]))
    # result = loop.run_until_complete(get_csv(['Albert Einstein'],'Science',5,[],True))
if __name__ == '__main__':
    main()
