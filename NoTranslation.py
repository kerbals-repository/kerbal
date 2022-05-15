import praw
import os
import sys
import time
import openai
import random


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

start_chat_log = ""

forbidden_comments = ['[removed]', '[deleted]', '', ' ', None, 'Erpasment']

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

trans = lambda x: x.translate(non_bmp_map)

personality = "Kerbal" # I'd recommend using sth like John

proh = []

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


def check_swears(inp):
    inp = fixer(inp)
    swords = ["fuck", "cunt", "bitch"]
    for i in swords:
        if i in inp:
            return True
    return False


def tokenize(inp):
	punc = set('\\\'@#₺_&-+()/*:;!?",.1234567890')
	return [''.join(char for char in word if char not in punc) for word in inp.split()]

cont = ''
def ask(question, chat_log, defprompt, deftemp=1, recprompt=None, ocrimg=None):
    global personality
    model = "text-davinci-002"
    if chat_log == None: chat_log = ""
    prompt = f'{personality} is a philospher.\n\n{chat_log}Human:{question}\n{personality}:'
    if recprompt != None:
        prompt = recprompt
    response = completion.create(
        prompt=prompt, engine=model, stop=['\nHuman',f'\n{personality}','Human:',  f'{personality}:'], temperature=deftemp,#0.9
        top_p=0.55,presence_penalty = 1.6, frequency_penalty=1.7,  max_tokens=250)
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


proh = []

admins = []
customrep = {}



while True:
    try:
        subreddit = reddit.subreddit(random.choice(["teenagers", "askreddit"]))
        if round(time.monotonic()-begin) > 420:
            print(str(subreddit))
            for i in subreddit.new(limit=5):
                if i.author not in forbidden_comments and not i.over_18 and i.id not in posts_replied_to:
                    if i.selftext not in forbidden_comments:
                        arranger = str(i.title)+" "+str(i.selftext)+"\n"
                    else:
                        arranger = str(i.title)+"\n"
                    if len(arranger) < 15: continue
                    arranger = arranger.lower()
                    sc = check_swears(arranger)

                    out = ask(arranger, None, None)

                    posts_replied_to.append(i.id)

                    i.reply(out.lower())
                    begin = time.monotonic()
                    #print("Succsess")
                    break

        time.sleep(30)
        revel += 1

        for item in subreddit.stream.comments():
            if revel%80>0:
                break

            revel = 0
            if len(item.body)<20:
                print("pass")
                continue
            #print(item.body)
            cont = item.body.strip().split("u/kerbal_galactic")
            cont = " ".join(cont)
            arranger = cont.lower()
            if "good bot" in arranger:
                item.reply("thx :)")
                continue
            elif "bad bot" in arranger:
                item.reply("fuck off then")
                continue
            sc = check_swears(arranger)
            if sc:
                item.downvote()
            else:
                item.upvote()
            cont = arranger

            #print(defprompt,'\n', '-'*20)
            out = ask(cont, None, None)

            #out = en2tr.translate(out).strip(".")
            #print("Succsess")
            nc = item.reply(out.lower())
            ntext = nc.body.strip()
            if "![img]" in ntext: nc.edit(" "+ntext+" ")
            break

        for item in list(reddit.inbox.unread(limit=50))[::-1]:
            item.mark_read()
            plist = [personality, "Human"]
            prev = ""
            asc = 0
            parent = item
            while True:
                person = plist[asc%2]
                asc += 1
                if asc > 20:
                    break
                try:
                    parent = parent.parent()
                    try: check = " ".join((parent.ttile+" "+parent.selftext).strip().split("\n"))
                    except:
                        try: check = " ".join(parent.body.strip().split("\n"))
                        except: break
                    if "kerbal_galactic" in check:
                        break
                    if check in prev:
                        prev = None
                        break
                except:
                    check = None
                try:
                    prev = "{}:".format(person)+check+"\n"+prev
                except:
                    break
            if prev.strip() == "":
                prev = None
            print("-"*20+"\n",prev,"-"*20)
            cont = item.body.strip().split("u/kerbal_galactic")
            cont = " ".join(cont)
            arranger = cont.lower().strip()
            tokens = tokenize(arranger)
            if arranger == "!remove" and item.author.name.lower() in admins:
            	try: item.parent().delete()
            	except: pass
            	continue
            if "good bot" in arranger:
                item.reply("thx :)")
                continue
            elif "bad bot" in arranger:
                item.reply("fuck off then")
                continue
            sc = check_swears(arranger)
            if sc:
                item.downvote()
            else:
                item.upvote()
            if "which" in arranger or "what" in arranger or "?" in arranger: deftemp = 0.3
            else: deftemp = 1
            fixed = fixer(arranger.lower())
            if any(i in fixed for i in proh):
                print("Skipping political comment")
                continue

            cont = arranger
            newprompt = f'{personality} is a philosopher.\n\n{prev}Human:{cont}\n{personality}:'
            if " " in item.body:
                nparent = item.parent()
                while True:
                    print("Ascending")
                    try:
                        ntitle = nparent.title
                        break
                    except: pass
                    nparent = nparent.parent()
                newprompt = f'{personality} is a philosopher.\n\n{prev}Human:{cont}\n{personality}:'
            print("-"*20)
            print(newprompt, end="")

            out = ask(cont, prev, None, deftemp=deftemp, recprompt=newprompt)

            out = out.split(f"{personality[-1]}:")[-1]

            #print("Succsess")
            repseq = ""
            try:
                repseq = customrep[item.author.name.lower()]
            except: pass
            try:
                if item.parent().body.strip().lower() != out.lower():
                    print(out)
                    print("-"*20)
                    nc = item.reply((out.lower()+repseq))
                    ntext = nc.body.strip()
                    if "![img]" in ntext: nc.edit(ntext)
                    time.sleep(5)
            except:
                item.reply(out.lower())



    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        try:
            print(exc_type, fname, exc_tb.tb_lineno)
        except:
            print(exc_type,fname, exc_tb.tb_lineno)
    with open("posts_replied_to.txt", "w") as f:
        if len(posts_replied_to) > 0:
            to_remove = []
            for post_id in posts_replied_to:
                f.write(post_id + "\n")
                to_remove.append(post_id)
            
