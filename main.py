from __future__ import unicode_literals
import praw
import os
import sys
import time
import openai
import random
from deep_translator import GoogleTranslator, MyMemoryTranslator
import ocrspace
from psaw import PushshiftAPI
from binary_comb import BinComb
from praw.models import Message
from prawcore.exceptions import ServerError
import secrets
import warnings
import numpy as np
from pathlib import Path
from difflib import SequenceMatcher

job =  'philosopher'
condition = 'n'


forced_topp = None
forced_temp = None

openai.api_key = ""


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

api = ocrspace.API(api_key='', language=ocrspace.Language.Turkish)



tr2en = GoogleTranslator(source='tr', target='en')
en2tr = GoogleTranslator(source='en', target='tr')


client_id = ""
client_secret = ""
username = ""
password = ""



user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"

reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)


class runner:
    def __init__(self):
        self.posts = []
        self.comments = []
        self.commented_on = []
        self.flairs = []
        self.keywords = []
        self.subreddit = reddit.subreddit('KGBTR')
        self.forbidden_comments = ['[removed]', '[deleted]', '', ' ', None]
        self.abs_path = Path(__file__).parent
        self.search_limit = 20
        self.post_limit = 50
        self.alike_value = 1.37


 
    def reply_on_comment(self, keyws=""):

        api = PushshiftAPI(reddit)

        all_comments = []
        comments = []
        keywords = keyws.split()
        keywords.sort(key=lambda x: -len(x))
        keywords = keywords[:6] #max keywords
        x = BinComb(keywords)
        searches = x.get_combinations()

        print("Comment:", keyws)
        print("Searches:", len(searches))

        for search in searches[:2]: #searches:

            print("\nStarting search %s:" % (searches.index(search) + 1))
            comments.append([])

            gen = api.search_comments(q=search, subreddit='kgbtr',limit=1000)
            cache = []

            for comment in gen:
                if len(cache) > 1000:
                    break
                if comment.body == '[deleted]' or comment.body == '[removed]':
                    continue
                if len(comment.body.split()) >= len(keywords) * 3:
                    continue
                if comment not in all_comments:
                    cache.append(comment)

            comments[searches.index(search)] += cache
            all_comments += cache
            if len(cache) > 2:
                break

        print("\nENDED.")

        for result in comments:
            print("Length:", len(result))
            c = None
            if len(result) > 0:
                tries = 0
                while True:
                    if len(result) == 0:
                        break
                    c = result[secrets.randbelow(len(result))]
                    c.refresh()
                    if len(c.replies) >= 1:
                        break
                    else:
                        result.remove(c)
                        c = None
            if c:
                break

        if c:
            to_comment = []
            for reply in c.replies:
                if reply.body not in self.forbidden_comments:
                    to_comment.append(reply.body)
            return to_comment[secrets.randbelow(len(to_comment))].lower()


pulldata = runner()


completion = openai.Completion()

start_chat_log = ""

forbidden_comments = ['[removed]', '[deleted]', '', ' ', None, 'Erpasment']

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

trans = lambda x: x.translate(non_bmp_map)

personality = "Kerbal"

proh = [
    "parti", "akp", "chp", "ataturk", "erdogan", "recep", "tayip", "tayyip",
    "rte ", "feto", "fetullah", "hdp", "ocalan", "demirtas", "selahattin",
    "teror", "hukumet"
]


def check_swears(inp):
    inp = fixer(inp)
    swords = [
        "amk", "amq", "mal", "salak", " sik", " oç ", " oc ", "anan", " ami",
        "amcik", "kancik", "yarak", "yarra", " got", "serefsiz", "hayvan",
        " oro", " ors"
    ]
    for i in swords:
        if i in inp:
            return True
    return False


def fixer(inp):
    dict_ = {"ü": "u", "ı": "i", "ö": "o", "ş": "s", "ğ": "g", "ç": "c"}
    for i in inp:
        if i in dict_:
            inp = inp.replace(i, dict_[i])
    return inp


def rearrange(arranger):
    arranger = arranger.replace("aq", "amk")
    arranger = arranger.replace("amk", "amına koyayım")
    arranger = arranger.replace(" oc", " orospu çocuğu")
    arranger = arranger.replace(" oç", " orospu çocuğu")
    arranger = arranger.replace(" sg", "siktir git")
    arranger = arranger.replace(" bot", " yapay zeka")
    arranger = arranger.replace("bot ", "yapay zeka ")
    arranger = arranger.replace("kes lan", "kapa çeneni")
    arranger = arranger.replace("flood", "kısa hikaye")
    arranger = arranger.replace("yarra ", "yarrağı")
    arranger = arranger.replace("31", "mastürbasyon")
    return arranger.capitalize()


def tokenize(inp):
    punc = set('\\\'@#₺_&-+()/*:;!?",.1234567890')
    return [
        ''.join(char for char in word if char not in punc)
        for word in inp.split()
    ]


cont = ''


def ask(question,
        chat_log,
        defprompt,
        deftemp=1,
        recprompt=None,
        ocrimg=None):

    model = "text-davinci-002"
    
    if chat_log == None: chat_log = ""
    if ocrimg == None: prompt = f'{personality} is a{condition} {job}. \n\n{chat_log}Human: {question}\n{personality}:'
    else: prompt = f'{personality} is a{condition} {job}. Human shows a picture to {personality} and they talk about it.\n\nThe text in the picture: {ocrimg}\n\n{chat_log}Human: {question}\n{personality}:'
    if recprompt != None: prompt = recprompt
    try: prompt = "".join(prompt.split("None"))
    except: pass
    huh = fixer(prompt).lower()
    breaktheloop = 0
    for a in personality_keyw:
        lists = personality_keyw[a]
        for words in lists:
            if words in huh:  #words in tokenized:
                print(words, end=' ')
                prompt = a + prompt
                breaktheloop = 1
                
        if breaktheloop: break

    # ne boktan yazmışım ben burayı amk

    print('\n'+'-'*30)
    prompt = prompt.replace("kerbal ", "kerbal, ")
    prompt = prompt.replace("Kerbal ", "Kerbal, ")

    top_p = 0.75

    if forced_topp != None:
        top_p = forced_topp

    if forced_temp != None:
        deftemp = forced_topp

    response = completion.create(
        prompt=prompt,
        engine=model,
        stop=['Human', f'{personality}', 'Human:', f'{personality}:'],
        temperature=deftemp,  #0.9
        top_p=top_p,
        presence_penalty=1.7,
        frequency_penalty=2,
        max_tokens=600)
    answer = response.choices[0].text.strip()
    for i in ['\nHuman', f'\n{personality}', 'Human:', f'{personality}:']:
        answer = answer.strip(i)
    if answer.count("Human:"): answer = answer.split("Human:")[0]
    if answer.count("human:"): answer = answer.split("human:")[0]
    if answer.count("insan"): answer = answer.split("insan:")[0]
    answer = en2tr.translate(prompt + answer).lower()
    answer = answer.split("insan:")[-1]
    answer = answer.split("kerbal:")[-1]
    answer = answer.split("kerbel:")[-1]
    answer = "#" + answer
    answer = answer.replace("#o,", "#no,")
    answer = answer.replace("#o", "#no")
    answer = answer.replace("#y,", "#")
    answer = answer.replace("#", "")
    #answer = answer.split(".")
    #answer = ".".join([i.capitalize() for i in answer])+"."
    print('\n',prompt+answer,'\n')
    return answer




personality_keyw = {
    "Kerbal hates refugees. ": ["Turkey","turkey","Afghan","Afghanistan","Syria",
                                "Syrian","refugee","refugees","immigrant","immigrants",
                                "rape","rapist","nude","street","streets","protest",
                                "government","ümit","hope","özdağ","imam","din","akp"],
}


revel = -1


print("Initializing...")




comment_interval = 420




begin = time.monotonic() - (comment_interval+1)

admins = []
customrep = {}


while True:
    try:
        subreddit = reddit.subreddit("")

        
        if round(time.monotonic() - begin) > comment_interval:
            for i in subreddit.new(limit=5):
                if i.author not in forbidden_comments and (not i.over_18):
                    url = i.url
                    text = None
                    if url.endswith(('.jpg', '.png', '.jpeg')):
                        try:
                            text = tr2en.translate(str(api.ocr_url(url)))
                            text = "\n".join(text.split("\n"))
                        except:
                            pass

                    elif random.randint(0, 80) > 10:
                        continue
                    begin = time.monotonic()
                    if text != None:
                        print("OCR metini algıladı.")
                    begin = time.monotonic()
                    print("Replying to:", trans(i.title))
                    if i.selftext not in forbidden_comments:
                        arranger = str(i.title) + "\n" + str(i.selftext)
                    else:
                        arranger = str(i.title) + "\n"
                    arranger = arranger.lower()
                    sc = check_swears(arranger)
                    arranger = rearrange(arranger)
                    arranger = tr2en.translate(arranger)

                    out = ask(arranger, None, None, ocrimg=text)
                    out = out.lower().replace("no.", "hayır.")


                    print(out)
                    if out == None or out == "":
                        continue
                    i.reply(out.lower())
                    #print("Succsess")
                    break

        time.sleep(20)
        revel += 1

        if revel % 30 == 0:
            for item in reddit.redditor(username).comments.new(limit=100):
                if item.score < 1:
                    print("removing")
                    item.delete()



        for item in list(reddit.inbox.unread(limit=50))[::-1]:
            item.mark_read()
            if item.submission.over_18: continue
            plist = [personality, "Human"]
            prev = ""
            asc = 0
            parent = item
            comment_author = item.author.name
            while True:
                person = plist[asc % 2]
                asc += 1
                if asc > 8:
                    break
                if len(tokenize(prev)) > 200:
                    break
                try:
                    parent = parent.parent()
                    try:
                        check = parent.body.strip()
                    except:
                        try:
                            check = " ".join((parent.title.strip() + " " +
                                              parent.selftext.strip()).split("\n"))
                        except:
                            break
                    if "kerbal_galactic" in check:
                        break
                    if "[deleted]" in check:
                        asc -= 1
                        continue
                    if parent.author.name != "kerbal_galactic" and comment_author != parent.author.name:
                        if "!load" not in check: asc = 9 #a clever way of breaking with delay :)
                except:
                    check = None
                try:
                    prev = "{}: ".format(person) + check.strip() + "\n" + prev
                except:
                    pass
            acqprev = prev
            try: prev = tr2en.translate(rearrange(prev))  
            except: prev = ""  #ananı sikeyim translate >:(
            prev = prev.replace("human:", "Human: ")
            prev = prev.replace("  ", " ")


            cont = item.body.strip().split("u/kerbal_galactic")
            
            cont = " ".join(cont)
            arranger = cont.lower().strip()

            if arranger == "!remove" and item.author.name.lower() in admins:
                try:
                    item.parent().delete()
                except:
                    pass
                continue
            elif arranger == "!stop" and item.author.name.lower() in admins: sys.exit(0)
            elif "!set" in arranger and item.author.name.lower() in admins:
                exec(arranger.split('!set')[-1].strip())
                item.reply("Değişiklik yapıldı.")
                continue
            if "good bot" in arranger:
                item.reply(":)")
                continue
            elif "bad bot" in arranger:
                item.reply("siktir git o zaman")
                continue
            sc = check_swears(arranger)
            if sc:
                item.downvote()
            else:
                item.upvote()
            if "listele" in arranger or "nedir" in arranger: deftemp = 0.3
            else: deftemp = 1
            arranger = rearrange(arranger)
            fixed = fixer(arranger.lower())
            if any(i in fixed for i in proh):
                print("oof")
                continue

            cont = tr2en.translate(arranger)
            newprompt = f'{personality} is a{condition} {job}. \n\n{prev}\nHuman: {cont}\n{personality}:'



            out = ask(cont, prev, None, deftemp=deftemp, recprompt=newprompt)
            #out = out.lower().replace("no.", "hayır.") #???
            
            try: repseq = customrep[item.author.name.lower()]
            except: repseq = ""
            
            try:
                if item.parent().body.strip().lower() != out.lower():
                    print(out)
                    print("-" * 20)
                    toreply = out.lower() + repseq
                    if toreply in acqprev or similar(toreply, item.parent().body.strip()) > 0.6 or similar(toreply, item.body.strip()) > 0.7:
                        toreply = pulldata.reply_on_comment(
                            item.body.strip())
                    nc = item.reply(toreply)
                    ntext = nc.body.strip()
                    if "![img]" in ntext: nc.edit(ntext)
                    elif "![gif]" in ntext: nc.edit(ntext)
                    time.sleep(3)
            except:
                toreply = out.lower() + repseq
                try:
                    if toreply in acqprev or similar(toreply, item.parent().body.strip()) > 0.5 or similar(toreply, item.body.strip()) > 0.7:
                        toreply = pulldata.reply_on_comment(item.body.strip())
                except AttributeError:
                    pass
                nc = item.reply(toreply)


    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)





