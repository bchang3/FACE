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
import asyncio

cat_dict = {
    'sci': 17,
    'fa': 21,
    'myth': 14,
    'religion': 19,
    'trash': 16,
    'ss': 22,
    'lit': 15,
    'hist': 18,
    'geo': 20,
    'ce':  26,
    'all': 'all',
}
difficulty_dict = {
    1: 'middle_school',
    2: 'easy_high_school',
    3: 'regular_high_school',
    4: 'hard_high_school',
    5: 'national_high_school',
    6: 'easy_college',
    7: 'regular_college',
    8: 'hard_college',
    9: 'open'
}
def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)#hey hey
async def get_file(query,category, difficulty):
    query.replace(' ','%20')
    if category == 'all':
        url = f'https://www.quizdb.org/?query={query}&search_type%5B0%5D=Answer&question_type%5B0%5D=Tossup'
    else:
        url = f'https://www.quizdb.org/?query={query}&category%5B0%5D={category}&search_type%5B0%5D=Answer&question_type%5B0%5D=Tossup'
    if len(difficulty) > 0:
        for i,x in enumerate(difficulty):
            phrase = difficulty_dict.get(x)
            url = url + f'&difficulty%5B{i}%5D={phrase}'
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(chrome_options = options, executable_path = 'Desktop/AVOCADO/chromedriver')
    driver.get(url)
    content = driver.page_source
    await asyncio.sleep(6)
    # load_button = driver.find_element_by_xpath("*//button[@class='ui button' and text()='Load All']")
    try:
        download_button = driver.find_element_by_xpath("*//*[@id='quizdb-page']/div/div[3]/div/div[1]/div[1]/div/div[2]/a[1]")
    except:
        driver.quit()
        return None
    download_button.click()
    await asyncio.sleep(7)
    file_name = newest('Downloads')
    os.rename(file_name,f"Downloads/{query.replace(' ','_')}.txt")
    driver.quit()
    file_name = f"Downloads/{query.replace(' ','_')}.txt"
    return file_name
def complete_replace_line(file_name):
    arr = [r"\[\D.*\]",r'&.*',r'\(.*?\)',r'\{.*?\}']
    patterns=[r'\d\.\n.*\n.*\nTossup:.', r"##.*",r'Number.*\nNumber.*\n']
    for i in arr:
        fin = open(file_name, "rt")
        data = fin.read()
        replacement = re.sub(i, '', data)
        data = replacement
        fin.close()
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
    for x in range(len(patterns)):
        fin = open(file_name, "rt")
        data = fin.read()
        replacement = re.sub(patterns[x], ' ', data)
        data = replacement
        fin.close()
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
    fin = open(file_name, "rt")
    data = fin.read()
    p = data.strip("\n").split("ANSWER: ")
    fin.close()
    print(p)

def replace_bonus(file_name, term=None):
    arr = [r"\[\D.*\]",r'&.*']
    testers = [r""]
    for i in arr:
        fin = open(file_name, "rt")
        data = fin.read()
        replacement = re.sub(i, '', data)
        data = replacement
        fin.close()
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
def replace_line(file_name, term):
    term = term.strip().replace('.', '')
    testers = [r'\[[^\]]+\]', r'\(.*?\)',r'\{.*?\}',r'&.*']
    patterns = [r"\n\d.*\n.*\n.*\nBONUS: ", r"\n\d.*\n.*\n.*\nTOSSUP: ", r"\nANSWER: .*\n", r"##.*", r"Number.*\nNumber.*\n", r"For 10 points, .*?\w ", r"For 10 points each.*", r"\nANSWER:.*\n", r"\n\d", r"\s\n"]
    replacements = ['  ', 'No. ', 'no. ', 'et. al.', 'et al.','Â', '►']
    for x in range(len(testers)):
        fin = open(file_name, "rt")
        data = fin.read()
        replacement = re.sub(testers[x], '', data)
        data = replacement
        fin.close()
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
    fin = open(file_name,"rt")
    data = fin.read()
    ans = re.findall(r'ANSWER:.*', data)
    for i in ans:
        orig_i = i[7:].strip()
        i = i[7:].strip().replace('.', '').casefold()
        if i == term.casefold():
            continue
        if i != term.casefold() and i != term.casefold()+"s":
            # print(i)
            print(orig_i)
            patterns_2=[fr'\d\.*\n.*\n.*\n.*\nANSWER:.*{i}', fr'\d\.*\n.*\n.*\n.*\nANSWER:.*{i}'+'s']
            for j in patterns_2:
                fin = open(file_name)
                p=re.sub(j,'',data)
                data = p
                fin.close()
                fin = open(file_name, "wt")
                fin.write(data)
                fin.close()
    for x in range(len(replacements)):
        fin = open(file_name, "rt")
        data = fin.read()
        replacer=data.replace(replacements[x],' ')
        if replacements[x] == 'No. ' or replacements[x] == 'no. ':
            replacer = data.replace(replacements[x],"#")
        elif replacements[x] == 'et. al.' or replacements[x]=='et al.':
            replacer = data.replace(replacements[x],'and others')
        data=replacer
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
    for x in range(len(patterns)):
        fin = open(file_name, "rt")
        data = fin.read()
        replacement = re.sub(patterns[x], ' ', data)
        data = replacement
        fin.close()
        fin = open(file_name, "wt")
        fin.write(data)
        fin.close()
    # tokenizer = nltk.data.load('tokenizers/punkt/PY3/english.pickle')
    # data = tokenizer.tokenize(data)
    # print(data)
async def get_csv(terms,category,id, difficulty,ctx):
    total_cards = 0
    full_path = f"Desktop/discordpy/temp/{category}{id}_cards.csv"
    try:
        f = open(full_path,"x")
    except:
        os.remove(full_path)
        f = open(full_path,"x")
    f.close()
    num = cat_dict.get(category)
    if num == None:
        return None
    for term in terms:
        file_name = await get_file(term, num, difficulty)
        if file_name == None:
            await ctx.channel.send(f'Error on {term}.')
            continue
        replace_line(file_name, term)
        f = open(file_name)
        text = f.read()
        f.close()
        sentences = sent_tokenize(text)
        with open(full_path, mode='a') as card_csv:
            for sentence in sentences:
                card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                card_writer.writerow([sentence,term])
                total_cards += 1
        os.remove(file_name)
    return full_path, total_cards
