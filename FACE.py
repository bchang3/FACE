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
}
def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)
async def get_file(query,category):
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(chrome_options = options, executable_path = 'Desktop/AVOCADO/chromedriver')

    query.replace(' ','%20')
    url = f'https://www.quizdb.org/?query={query}&category%5B0%5D={category}&search_type%5B0%5D=Answer&question_type%5B0%5D=Tossup'
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
def replace_line(file_name, term):
    testers = [r'\[[^\]]+\]', r'\(.*?\)',r'&.*']
    patterns = [r"\n\d.*\n.*\n.*\nBONUS: ", r"\n\d.*\n.*\n.*\nTOSSUP: ", r"\nANSWER: .*\n", r"##.*", r"Number.*\nNumber.*\n", "For 10 points each.*", r"\nANSWER:.*\n", r"\n\d", r"\s\n"]
    replacements = ['  ', 'No. ', 'no. ']
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
        i = i[len(term)-2:].strip()
        if i != term:
            fin = open(file_name)
            pattern=re.sub(fr'\d\.*\n.*\n.*\n.*\nANSWER: {i}','',data)
            data = pattern
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
async def get_csv(term,category):
    num = cat_dict.get(category)
    if num == None:
        return None
    file_name = await get_file(term, num)
    if file_name == None:
        return None
    replace_line(file_name, term)
    f = open(file_name)
    text = f.read()
    f.close()
    sentences = sent_tokenize(text)
    full_path = "Desktop/discordpy/temp/cards.csv"
    f = open(full_path,"x")
    f.close()
    with open(full_path, mode='w') as card_csv:
        for sentence in sentences:
            card_writer = csv.writer(card_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            card_writer.writerow([sentence,term])
    os.remove(file_name)
    return full_path
