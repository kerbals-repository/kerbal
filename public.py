import praw
import os
import sys
import time
import openai
import random
import deep_translator
from deep_translator import GoogleTranslator, MyMemoryTranslator
from PyYandexOCR import PyYandexOCR

ocr = PyYandexOCR(20)

tr2en = GoogleTranslator(source='tr', target='en')
en2tr = GoogleTranslator(source='en', target='tr')

##tr2en = MyMemoryTranslator(source='tr', target='en')
##en2tr = MyMemoryTranslator(source='en', target='tr')


client_id = ""
client_secret = ""
username = ""
password = ""
user_agent = f"User-Agent: linux:com.{username}s.runner:v1.0 (by /u/{username}s)"

reddit = praw.Reddit(client_id = client_id,
                     client_secret = client_secret,
                     username = username,
                     password = password,
                     user_agent = user_agent)

openai.api_key = ""

#openai.api_base = "https://api.goose.ai/v1"

completion = openai.Completion()

forbidden_comments = ['[removed]', '[deleted]', '', ' ', None]

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
trans = lambda x: x.translate(non_bmp_map)

personality = "Kerbal"

proh = ["hentai","porno","porn","parti","akp","chp","ataturk","erdogan","recep","tayip","tayyip","rte","feto","fetullah","hdp","ocalan","teror","hukumet","pkk"]


def check_swears(inp):
    inp = fixer(inp)
    swords = ["amk","amq","mal","salak"," sik"," oç "," oc ","anan"," ami","amcik","kancik","yarak","yarra"," got",
    "serefsiz","hayvan"," oro"," ors"]
    for i in swords:
        if i in inp:
            return True
    return False

def fixer(inp):
	dict_ = {"ü":"u",
                "ı":"i",
                "ö":"o",
                "ş":"s",
                "ğ":"g",
                "ç":"c"}
	for i in inp:
		if i in dict_:
			inp = inp.replace(i,dict_[i])
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
    return arranger

def tokenize(inp):
	punc = set('\\\'@#₺_&-+()/*:;!?",.1234567890')
	return [''.join(char for char in word if char not in punc) for word in inp.split()]

def ask(question, chat_log, defprompt, deftemp=1, recprompt=None, ocrimg=None):
    global personality
    model = "text-davinci-002"
    if chat_log == None: chat_log = ""
    if ocrimg == None: prompt = f'{personality} is a philospher.\n\n{chat_log}Human:{question}\n{personality}:'
    else: prompt = f'{personality} is a philospher. Human shows an image to {personality} and they talk about it.\n\nText in the image: {ocrimg}\n\n{chat_log}Human:{question}\n{personality}:'
    if recprompt != None:
        prompt = recprompt
    response = completion.create(
        prompt=prompt, engine=model, stop=['\nHuman',f'\n{personality}','Human:',  f'{personality}:'], temperature=deftemp,#0.9
        top_p=0.75, presence_penalty = 1.2, frequency_penalty=1.9,  max_tokens=200)

##        daha yüksek temperature         = daha yaratıcı cevaplar (model eğitilirken kullanılan veriden daha bağımsız)
##        daha yüksek top_p               = daha standart(yapay) cevaplar
##        çok düşük top_p                 = insansı ama anlamsız cevaplar
##        daha yüksek presence_penalty    = daha az tekrar(sentiment tabanlı)
##        daha yüksek frequency_penalty   = daha az tekrar(kelime tabanlı)
        
    answer = response.choices[0].text.strip()
    for i in ['\nHuman',f'\n{personality}','Human:',  f'{personality}:','\n']:
        answer = answer.strip(i)
    return answer


revel = 0
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []
else:
    with open("posts_replied_to.txt", "r") as f:
       posts_replied_to = f.read()
       posts_replied_to = posts_replied_to.split("\n")
       posts_replied_to = list(filter(None, posts_replied_to))

print("Initializing...")

begin = time.monotonic()-2401


admins = ["anancilikyapma"]
customrep = {"anancilikyapma":"\n\n(◍•ᴗ•◍)❤"}

neden_rand = ["kaplumbağa deden","anana sor","kurtlar vadisi 95. bölüm 43:17"]
good_bot_rand = [":)"]
bad_bot_rand = ["siktir git o zaman"]


subreddit = reddit.subreddit("KGBTR")

while True:
    try:
        if round(time.monotonic()-begin) > 420:
            for i in subreddit.new(limit=5):
                if i.author not in forbidden_comments and not i.over_18 and i.id not in posts_replied_to:
                    url = i.url
                    text = None
                    if url.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        try:
                            text = tr2en.translate(ocr.get_ocr(url,"tr"))
                            text = "\n".join(text.split("\n"))
                        except: pass
                    elif random.randint(0,80)>10:continue
                    #if text != None: print("OCR metini algıladı.")
                    begin = time.monotonic()
                    print("Replying to:",trans(i.title))
                    if i.selftext not in forbidden_comments:
                        arranger = str(i.title)+"\n"+str(i.selftext)
                    else:
                        arranger = str(i.title)+"\n"
                    arranger = arranger.lower()
                    sc = check_swears(arranger)
                    arranger = rearrange(arranger)
                    arranger = tr2en.translate(arranger)

                    out = ask(arranger, None, None, ocrimg=text)
                    out = out.lower().replace("no.","hayır.") #???

                    out = en2tr.translate(out).strip(".")

                    posts_replied_to.append(i.id)

                    i.reply(out.lower())

                    break
                
            with open("posts_replied_to.txt", "w") as f:
                if len(posts_replied_to) > 0:
                    for post_id in posts_replied_to:
                        f.write(post_id + "\n")
  

        time.sleep(20)
        revel += 1

        for item in subreddit.stream.comments():
            if revel%40>0: break
            revel = 0
            if len(item.body)<20: continue
            cont = item.body.strip().split("u/kerbal_galactic")
            cont = " ".join(cont)
            arranger = cont.lower()
            if "good bot" in arranger:
                item.reply(random.choice(good_bot_rand))
                continue
            elif "bad bot" in arranger:
                item.reply(random.choice(bad_bot_rand))
                continue
            sc = check_swears(arranger)
            if sc: item.downvote()
            else: item.upvote()
            arranger = rearrange(arranger)
            cont = tr2en.translate(arranger)


            out = ask(cont, None, None)
            out = out.lower().replace("no.","hayır.")
            out = en2tr.translate(out).strip(".")

            nc = item.reply(out.lower())
            ntext = nc.body.strip()
            if "![img]" in ntext: nc.edit(" "+ntext+" ")
            break

        for item in list(reddit.inbox.unread(limit=5))[::-1]:
            item.mark_read()
            plist = [personality, "Human"]
            prev = ""
            asc = 0
            parent = item
            while True:
                person = plist[asc%2]
                asc += 1
                if asc > 20: break
                try:
                    parent = parent.parent()
                    try: check = " ".join(parent.body.strip().split("\n"))
                    except: break
                    if "u/kerbal_galactic" in check: break
                    try: check = tr2en.translate(rearrange(check))
                    except:
                        try: check = tr2en.translate(rearrange(parent.title+"\n"+str(parent.selftext)))
                        except: pass
                except: check = None
                try: prev = "{}:".format(person)+check+"\n"+prev
                except: break
            if prev == "": prev = None
            print("-"*20+"\n",prev,"-"*20)
            cont = item.body.strip().split("u/kerbal_galactic")
            cont = " ".join(cont)
            arranger = cont.lower().strip()
            tokens = tokenize(arranger)
            if tokens[0]=="neden" and len(tokens)==1:
                item.reply(random.choice(neden_rand))
                continue
            if arranger == "!remove" and item.author.name.lower() in admins:
            	try: item.parent().delete()
            	except: pass
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
                print("Skipping political comment")
                continue

            cont = tr2en.translate(arranger)
            newprompt = f'{personality} is a philosopher.\n\n{prev}Human:{cont}\n{personality}:'

            if " " in item.body: #??? Test amaçlıydı if bloğu direk kaldırılabilir(?)
                nparent = item.parent()
                while True:
                    print("Ascending")
                    try:
                        ntitle = nparent.title
                        break
                    except: pass
                    nparent = nparent.parent()
                url = nparent.url
                text = None
                if url.endswith(('.jpg', '.png', '.gif', '.jpeg')):
                    try: ocrtext = ocr.get_ocr(url, "tr")
                    except:
                        try: ocrtext = ocr.get_ocr(url, "en")
                        except: text= None
                    if text != None: text = tr2en.translate(ocrtext)
                if text == None: pass
                elif text.strip()=="": text = None
                if text != None:
                    text = "\n".join(text.split("\n"))
                    #text = " ".join(tokenize(text))
                    print(text)
                    newprompt = f'{personality} is a philosopher. Human shows an image to {personality}.\n\nText in the image: {text}\n\n{prev}Human:{cont}\n{personality}:'
                else: newprompt = f'{personality} is a philosopher.\n\n{prev}Human:{cont}\n{personality}:'

            print("-"*20)
            print(newprompt, end="")

            out = ask(cont, prev, None, deftemp=deftemp, recprompt=newprompt)
            out = out.lower().replace("no.","hayır.")
            try:
                out = en2tr.translate(newprompt+out+" ").strip(".")
                out = out.split(f"{personality[-1]}:")[-1]
            except: out = en2tr.translate(out).strip(".")

            
            try: repseq = customrep[item.author.name.lower()]
            except: repseq = ""
            
            if item.parent().body.strip().lower() != out.lower():
                
                print(out)
                print("-"*20)
                
                nc = item.reply(out.lower()+repseq)
                ntext = nc.body.strip()
                if "![img]" in ntext: nc.edit(ntext)
                time.sleep(20)




    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

