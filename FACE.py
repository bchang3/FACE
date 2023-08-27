import sys
import re
import time
import random
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
import csv
import asyncio
import psycopg2
from sentence_similarity import compare_sentences
import random
from asgiref.sync import sync_to_async
import matplotlib.pyplot as plt
import mysql.connector as mysql
size_db = 98934
def size():
    return size_db
def postgres_connect():
    conn = psycopg2.connect(
    host = 'localhost',
    user = 'ec2-user',
    password = 'TheCataclysm91$(*',
    database = 'quizdb'
    )
    cur = conn.cursor()
    return conn, cur
def mysql_connect():
    mydb = mysql.connect(
      host="127.0.0.1",
      user="root",
      password="Please!2",
      database="face_log"
    )
    mycursor = mydb.cursor(buffered=True)
    return mydb, mycursor
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
abbrev_dict = {
    'science': 'sci',
    'fine arts': 'fa',
    'mythology': 'myth',
    'religion': 'religion',
    'trash': 'trash',
    'social science': 'ss',
    'literature': 'lit',
    'history': 'hist',
    'geography': 'geo',
    'current events':  'ce',
    'philosophy': 'philo'
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
    'sci:biology':'Science Biology',
    'science:biology':'Science Biology',
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
mydb, mycursor = mysql_connect()
def clean_answer(ans):
    formatters = [('*',''), (';',''), ('<em>','*'), (r'</em>','*'), ('<strong>','**'), ('</strong>','**'), ('<u>','__'), ('</u>','__'), ('&lt','<'), ('&gt','>')]
    patterns = [r"\[\D.*\]",r"\&lt\D.*\&gt", r'\(.*?\)',r'\{.*?\}', r" For 10 points, .*?\w ", r"For 10 points each.*", r"\n\d"]#r'&.*'
    replacements = ['No. ', 'no. ', 'et. al.', 'et al.','Â', '►', '\(', '\)', 'Sgt.']
    for i in patterns:
        ans = re.sub(i, '', ans)
    for char in formatters:
        if char[0] in ans:
            ans = ans.replace(char[0],'')
    return ans.strip()
cat_dict = dict()
reverse_cat_dict = dict()
cur.execute('SELECT * FROM categories')
cat_rows = cur.fetchall()
for row in cat_rows:
    cat_dict[row[1].casefold()] = int(row[0])
    reverse_cat_dict[int(row[0])] = row[1]
cat_dict['all'] = 'all'

subcat_dict = dict()
reverse_subcat_dict = dict()
cur.execute('SELECT * FROM subcategories')
subcat_rows = cur.fetchall()
for row in subcat_rows:
    subcat_dict[row[1].casefold()] = int(row[0])
    reverse_subcat_dict[int(row[0])] = row[1]
cur.execute('SELECT * FROM tournaments')
tournament_rows = cur.fetchall()
difficulty_dict = dict()
total_difficulties = [0,0,0,0,0,0,0,0,0]
for row in tournament_rows:
    difficulty_dict[int(row[0])] = int(row[3])
    cur.execute(f'SELECT id FROM tossups WHERE tournament_id = {row[0]}')
    count = len(cur.fetchall())
    total_difficulties[int(row[3])-1] += count
difficulty_rankings = []
for cat in first_cat_dict.values():
    id = cat_dict.get(cat)
    executor = f"SELECT answer FROM tossups WHERE category_id = {id}"
    cur.execute(executor)
    tossups = cur.fetchall()
    tossups = [x[0] for x in tossups]
    tossups = list(map(clean_answer,tossups))
    unique_tossups = [(x,tossups.count(x)) for x in set(tossups)]
    percentage = round(len(tossups)/size_db,4) * 100
    diff = len(unique_tossups)/percentage
    redundancy = len(tossups)/len(unique_tossups)
    difficulty_rankings.append((cat,diff/redundancy))
difficulty_rankings.sort(reverse=True,key=lambda x:x[1])

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
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s)"
        values = (query,)
    elif query == None and subcategory == None:
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE category_id = %s"
        values = (category,)
    elif query == None and subcategory != None:
        executor = f"SELECT tournament_id,text,answer FROM tossups WHERE subcategory_id = %s"
        values = (subcategory,)
    else:
        query = query.replace(' ',' & ')
        if subcategory:
            executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s) AND subcategory_id = %s"
            values = (query,subcategory)
        else:
            executor = f"SELECT tournament_id,text,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s) AND category_id = %s"
            values = (query,category)
    cur.execute(executor,values)
    results = cur.fetchall()
    if difficulty and len(difficulty) > 0:
        for i,res in enumerate(results[:]):
            if difficulty_dict.get(res[0]) not in difficulty:
                if res in results:
                    results.remove(res)
    results = list(map(last_two,results))
    return results
async def get_frequency(category,difficulty,terms):
    conn, cur = postgres_connect()
    if terms != None and len(terms) > 0:
        terms = terms.strip().casefold()
        terms = terms.replace(' ',' & ')
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
    # if category == 'all':
    #     executor = f"SELECT tournament_id,answer FROM tossups"
    #     cur.execute(executor)
    #     color = None
    if subcategory == None:
        executor = f"SELECT tournament_id,answer FROM tossups WHERE category_id = %s"
        values = [category]
        color = color_dict.get(int(category))
    elif subcategory != None:
        executor = f"SELECT tournament_id,answer FROM tossups WHERE subcategory_id = %s"
        values = [subcategory]
        color = color_dict.get(int(subcategory))
    if terms != None and len(terms) > 0:
        executor = executor + " AND to_tsvector('english',text) @@ to_tsquery('english',%s)"
        values.append(terms)
    values = tuple(values)
    cur.execute(executor,values)
    results = cur.fetchall()
    if len(difficulty) > 0:
        for i,res in enumerate(results[:]):
            if difficulty_dict.get(res[0]) not in difficulty:
                if res in results:
                    results.remove(res)
    total = len(results)
    results = [row[1] for row in results]
    results = list(map(clean_answer,results))
    answerlines = [(x,results.count(x)) for x in set(results)]
    answerlines.sort(reverse=True,key=lambda x:x[1])
    answerlines = answerlines[:50]
    only_ans = [x[0] for x in answerlines]
    # print(', '.join(only_ans))
    coverage = 0 if total == 0 else sum([val[1] for val in answerlines])/total
    return only_ans,coverage,color
async def lookup(query,category):
    orig_query = query
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
    if category == 'all' or category == 'ranked' and query != None:
        query = query.replace(' ',' & ')
        executor = f"SELECT tournament_id,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s)"
        values = (query,)
    elif query == None and subcategory == None:
        executor = f"SELECT tournament_id,answer FROM tossups WHERE category_id = %s"
        values = (category,)
    elif query == None and subcategory != None:
        executor = f"SELECT tournament_id,answer FROM tossups WHERE subcategory_id = %s"
        values = (subcategory,)
    else:
        query = query.replace(' ',' & ')
        if subcategory:
            executor = f"SELECT tournament_id,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s) AND subcategory_id = %s"
            values = (query,subcategory)
        else:
            executor = f"SELECT tournament_id,answer FROM tossups WHERE to_tsvector('english',answer) @@ to_tsquery('english',%s) AND category_id = %s"
            values = (query,category)
    cur.execute(executor,values)
    results = cur.fetchall()
    new_results = []
    for i,row in enumerate(results.copy()):
        answer = new_complete_replace_line(('',row[1]))[1]
        if orig_query.casefold() == answer.casefold() or orig_query.casefold() in answer.casefold():
            new_results.append((row[0],answer))
    results = new_results
    y = []
    x = list(range(1,10))
    for difficulty in range(1,10):
        count = 0
        for i,res in enumerate(results):
            if int(difficulty_dict.get(res[0])) == difficulty:
                if res in results:
                    count += 1
        y.append(count)
    y = [count/total_difficulties[i-1]*200 for i,count in enumerate(y)]
    return x,y
async def get_stats(category):
    conn, cur = postgres_connect()
    mydb, mycursor = mysql_connect()
    subcategory = None
    if category:
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
        return (size_db, difficulty_rankings)
    elif subcategory == None:
        full_category = True
        id = category

    else:
        full_category = False
        id = subcategory
    color = color_dict.get(int(id))
    values = (id,)
    mycursor.execute(f"SELECT num_percent_50,num_tossups,num_unique_tossups FROM stats WHERE cat_id = %s AND full_category = {full_category}",(id,))
    info = mycursor.fetchone()
    counter = info[0]
    num_tossups = info[1]
    num_unique_tossups = info[2]
    percentage = round(num_tossups/size_db,4) * 100
    return (percentage, num_unique_tossups, counter, num_tossups, color)


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
async def check_category(category):
    curly_search =  re.search(r'\{(.*?)\}',category)
    if curly_search:
        categories = curly_search.group(1).split(',')
        category_ids = list(map(get_cat_id,categories))
        if len(category_ids) == 0:
            return
        for x in category_ids.copy():
            if x == None:
                return
        conditions = category_ids
    else:
        category_ids = get_cat_id(category)
        if category_ids == None:
            return
    return True
async def get_bonus(category,difficulty,to_retrieve=4):#soccer
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
        conditions = category_ids
    else:
        category_ids = get_cat_id(category)
        if category_ids == None:
            return
        conditions = [category_ids]
    results = []
    executions = []
    if category == 'all':
        executor =  f"SELECT tournament_id,id,leadin,category_id FROM bonuses TABLESAMPLE BERNOULLI(0.5) LIMIT 1000"
        executions.append(executor)
        category = 'ALL'
    else:
        for x in conditions:
            executor = f"SELECT tournament_id,id,leadin,category_id FROM bonuses WHERE " + x
            executions.append(executor)
    for executor in executions:
        cur.execute(executor)
        results.append(cur.fetchall())#what is question a and s it's the question and the answer
    if len(difficulty) > 0:
        for result in results:
            for i,res in enumerate(result.copy()):
                if difficulty_dict.get(res[0]) not in difficulty:
                    if res in result:
                        result.remove(res)
    sampled = []
    num_bonuses = 0
    try:
        for result in results:
            num_bonuses += len(result)
            sampled = sampled + random.sample(result,to_retrieve)
    except:
        return 'not enough'
    results = sampled
    random.shuffle(results)
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
        if x[0] == None:
            return
        executor = f"SELECT name FROM tournaments WHERE id = {x[0]}"
        cur.execute(executor)
        name = cur.fetchone()[0]
        try:
            bonuses.append(((leadin,name,difficulty_dict.get(x[0]),color),parts[0],parts[1],parts[2]))
        except:
            return
    misc = (num_bonuses,category.capitalize())
    bonuses.append(misc)
    return bonuses
async def get_tk_tossup(category,difficulty,to_retrieve=4):
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
        conditions = category_ids
    else:
        category_ids = get_cat_id(category)
        if category_ids == None:
            return
        conditions = [category_ids]
    executions = []
    if category == 'all':
        executor = f"SELECT tournament_id,formatted_text,formatted_answer,id,category_id,subcategory_id FROM tossups TABLESAMPLE BERNOULLI(0.5) LIMIT 5000"
        executions.append(executor)
    else:
        for x in conditions:
            executor = f"SELECT tournament_id,formatted_text,formatted_answer,id,category_id,subcategory_id FROM tossups WHERE " + x
            executions.append(executor)
    results = []
    for executor in executions:
        cur.execute(executor)
        results.append(cur.fetchall())
    if len(difficulty) > 0:
        for result in results:
            for i,res in enumerate(result.copy()):
                if difficulty_dict.get(res[0]) not in difficulty:
                    if res in result:
                        result.remove(res)
    sampled = []
    num_tossups = 0
    try:
        for result in results:
            num_tossups += len(result)
            sampled = sampled + random.sample(result,to_retrieve)
    except:
        return 'not enough'
    results = sampled
    random.shuffle(results)
    results = list(map(lambda x: (difficulty_dict.get(x[0]),x[1],x[2],x[3],x[4],x[5]),results))
    results = list(map(new_complete_replace_line_tk,results))
    if 'error' in results:
        return 'error'
    for i,question in enumerate(results):
        q = question[0]
        words = q.split()
        sentences = sent_tokenize(q)
        max_words = max([len(word_tokenize(x)) for x in sentences])
        num_sent = len(sentences)
        results[i] = (question,max_words,words,num_sent)
    return results[:to_retrieve]
async def get_tournament(tournament,category):
    subcategory = None
    if category != None:
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
            return 'invalid category'
    conn, cur = postgres_connect()
    tournament = tournament.replace(' ',' & ')
    executor = f"SELECT id,name FROM tournaments WHERE to_tsvector('english',name) @@ to_tsquery('english',%s)"
    values = (tournament,)
    cur.execute(executor,values)
    results = cur.fetchall()
    try:
        id = results[0][0]
        name = results[0][1]
    except:
        return None
    if category == None and subcategory == None:
        executor = f"SELECT text,answer FROM tossups WHERE tournament_id = {id}"
    elif subcategory == None:
        executor = f"SELECT text,answer FROM tossups WHERE tournament_id = {id} AND category_id = {category}"
    else:
        executor = f"SELECT text,answer FROM tossups WHERE tournament_id = {id} AND subcategory_id = {subcategory}"
    cur.execute(executor)
    results = cur.fetchall()
    return results,name
def new_complete_replace_line(question):
    s = question[0]
    a = question[1]
    #divide between {} and ## in arr
    patterns = [r"Question:.*?\d\.", r"\[\D.*\]",r"\&lt\D.*\&gt;", r'\(.*?\)',r'\{.*?\}', r" For 10 points, .*?\w ", r"For 10 points each.*", r"\n\d"]#r'&.*',
    replacements = [' No. ', ' no. ', 'et. al.', 'et al.','Â', '►', '\(', '\)', 'Sgt.', 'For 10 points.']
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
        if replacements[x]==' No. ' or replacements[x]==' no. ':
            replacement = s.replace(replacements[x],'#')
            #re.sub(replacements[x], '#', s)
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
    replacements = ['et. al.', 'et al.','Â', '►', '\(', '\)', 'Sgt.']
    for i in patterns:
        replacement = re.sub(i, ' ', s)
        s = replacement
    for i in patterns:
        replacement = re.sub(i, ' ', a)
        a = replacement
    s = re.sub(r"\s\n",'',s).strip().replace('  ', '')
    for char in formatters:
        if char[0] in a:
            a = a.replace(char[0],'')
        if char[0] in s:
            s = s.replace(char[0],char[1])
    final = (s, orig_a.strip(),a.strip())
    return final
def new_complete_replace_line_tk(question):
    diff = question[0]
    s = question[1]
    a = question[2]
    if len(question) > 3:
        id = question[3]
        category = reverse_cat_dict.get(question[4])
        subcategory = reverse_subcat_dict.get(question[5])
    orig_a = a
    formatters = [('<em>','*'), (r'</em>','*'), ('<strong>','**'), ('</strong>','**'), ('<b>','**'), ('</b>','**'),('<u>','__'), ('</u>','__'), ('&lt','<'), ('&gt','>')]
    for char in formatters:
        if char[0] in a:
            orig_a = orig_a.replace(char[0],char[1])
        if char[0] in s:
            s = s.replace(char[0],'')
    patterns = [r"\[\D.*\]",r"\&lt\D.*\&gt", r'\(.*?\)',r'\{.*?\}', r"\n\d"]
    replacements = ['Â', '►', 'Sgt.']
    for i in patterns:
        replacement = re.sub(i, ' ', a)
        a = replacement
    s = re.sub(r"\s\n",'',s).strip().replace('  ', '')
    for char in formatters:
        if char[0] in a:
            a = a.replace(char[0],'')
        if char[0] in s:
            s = s.replace(char[0],char[1])
    try:
        if a.strip()[-1] == ';':
            a = a.strip()[:-1]
    except:
        return 'error'
    if len(question) > 3:
        final = (s, orig_a.strip(),a.strip(),diff,id,category,subcategory)
    else:
        final = (s, orig_a.strip(),a.strip(),diff)
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
async def get_csv(terms,category,id, difficulty,term_by_term,raw, num_sentences,num_limit=0):
    async def write_csv(tossups,raw,num_sentences,term=None):
        clues = []
        writing = []
        excess = 0
        nonlocal total_cards
        questions = list(map(new_complete_replace_line,tossups))
        for question,answer in questions:
            if term != None and term.casefold() not in answer.casefold():
                continue
            try:
                sentences = await sync_to_async(sent_tokenize)(question) #tokenzied sentences in a tossup
            except:
                continue
            num_sentences = num_sentences if num_sentences else len(sentences)
            for sentence in sentences[:num_sentences]: #iterating over each sentence
                orig_sentence = sentence
                if sentence == '':
                    continue
                # sentence = sentence.replace('  ', ' ')
                # sentence = ' '.join([w for w in word_tokenize(sentence) if w not in stopwords.words('english')])
                duplicate = False
                if raw == False:
                    for clue in clues: #list of clues being built, each new clue is compared to all old clues before it
                        if clue[1] == answer:
                            score = await sync_to_async(compare_sentences)(clue[0],sentence)
                            if score > 0.55:
                                excess += 1
                                duplicate = True
                                break
                    if duplicate == True:
                        continue
                writing.append([orig_sentence, answer])
                clues.append((sentence,answer))
                total_cards += 1
        with open(full_path, mode='a') as card_csv:
            if num_limit > 0 and num_limit < total_cards:
                writing = random.choices(writing, k=num_limit)
            for packet in writing:
                card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                card_writer.writerow(packet)
            total_cards = len(writing)

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
            await write_csv(tossups,raw,num_sentences,term)
    else:
        tossups = await get_tossup(None,category,difficulty)
        if tossups == None:
            return None
        await write_csv(tossups,raw,num_sentences)
    return full_path, total_cards
async def get_csv_tournament(tournament,category):
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
    tossups,name = await get_tournament(tournament,category)
    if tossups == None:
        return None
    full_path = f"temp/{name}{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    f.close()
    write_csv_tournament(tossups)
    return full_path, total_cards,name
def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_csv(['Max Planck'],'SCI',123, [3,4,5],True,False))#did you test it
    print(result)#
    # result = loop.run_until_complete(get_csv_tournament('ANFORTAS'))
    # result = loop.run_until_complete(lookup('Rautavaara','fa'))
    # result = loop.run_until_complete(get_csv(['Albert Einstein'],'Science',5,[],True))
if __name__ == '__main__':
    main()
