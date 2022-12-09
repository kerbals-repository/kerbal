from __future__ import unicode_literals
import praw,os,sys,time,openai,random
from deep_translator import GoogleTranslator
import ocrspace
from psaw import PushshiftAPI
from binary_comb import BinComb
from praw.models import Message
from prawcore.exceptions import ServerError
import secrets,warnings,numpy as np
from pathlib import Path
import json
from difflib import SequenceMatcher
import wolframalpha


client_id='ugP0pDuOKl4FuPs2h1iGiA'
client_secret='g_xMR_PCf9uqduVsKqiscCb19OkJLg'
username=''
password=''

app_id='5YTYVR-AU34H8TT5L'  # Wolframalpha API key

openai.api_key='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' # OpenAI API key

api=ocrspace.API(api_key='K86811002688957',language=ocrspace.Language.Turkish) # OCRSpace key



botrole='chatbot'
condition='sarcastic'
interval = 2400

admins=['']


preset={'nereye':'ananın amına',
        'nerede':'ananın amında',
        'nerde':'ananın amında',
        'bozuldu':'ananın amı bozuldu orospu çocuğu',
        'yarramı ye':'tüh bugün de aç kaldık :c'}



recover_botrole=str(botrole)
tr2en=GoogleTranslator(source='tr',target='en')
en2tr=GoogleTranslator(source='en',target='tr')
user_agent=f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"
reddit=praw.Reddit(client_id=client_id,client_secret=client_secret,username=username,password=password,user_agent=user_agent)
client=wolframalpha.Client(app_id)

### koyunkırpan kodu başlangıç

class runner:
	def __init__(self):self.posts=[];self.comments=[];self.commented_on=[];self.flairs=[];self.keywords=[];self.subreddit=reddit.subreddit('KGBTR');self.working_hours=['14','15','16','17','18','19','20','21','22','23'];self.forbidden_comments=['[removed]','[deleted]','',' ',None];self.abs_path=Path(__file__).parent;self.search_limit=20;self.post_limit=50;self.alike_value=1.33
	def load_commented_on(self):
		with self.abs_path.joinpath('savedata.json').open('r',encoding='utf8')as f:self.commented_on=json.load(f)
	def on_comment(self,post_id):
		if post_id:self.commented_on['ids'].append(post_id)
		with self.abs_path.joinpath('savedata.json').open('w',encoding='utf8')as json_file:json.dump(self.commented_on,json_file,indent=4,sort_keys=True)
	def load_replies(self):
		with self.abs_path.joinpath('replies.json').open('r',encoding='utf8')as f:self.replies=json.load(f)
		if len(self.replies.keys())==0:self.load_flairs()
	def load_flairs(self):
		for flair in reddit.subreddit('KGBTR').flair.link_templates:
			if flair['id']not in self.flairs:self.replies[flair['id']]={'text':flair['text'],'replies':[]}
		with self.abs_path.joinpath('replies.json').open('w',encoding='utf8')as json_file:json.dump(self.replies,json_file,indent=4,sort_keys=True)
	def check_posts(self):
		for submission in self.subreddit.new(limit=self.post_limit):
			if submission not in self.posts and submission.id not in self.commented_on['ids']and submission.link_flair_text!='Ciddi :snoo_disapproval:':self.posts.append(submission)
		for submission in self.subreddit.hot(limit=self.post_limit):
			if submission not in self.posts and submission.id not in self.commented_on['ids']and submission.link_flair_text!='Ciddi :snoo_disapproval:':self.posts.append(submission)
		print('Collected : %s posts\n'%len(self.posts))
	def select_post(self):
		for i in range(0,5):
			p=self.posts[secrets.randbelow(len(self.posts))]
			if len(p.comments)<5:continue
			else:return p
		return None
	def post_keywords(self,p):
		for word in p.title.split(' '):
			if word not in self.keywords:self.keywords.append(word.lower())
		p.comment_sort='best'
		for top_level_comment in p.comments[0:5]:
			if top_level_comment.body not in self.forbidden_comments:
				for word in top_level_comment.body.splitlines()[0].split(' '):
					if word not in self.keywords:self.keywords.append(word.lower())
		self.keywords=self.keywords[0:20]
	def find_similar(self,title,nsfw):
		try:
			if nsfw:nsfw='yes'
			else:nsfw='no'
			keywords=title.split(' ');return self.subreddit.search('%s nsfw:%s'%(' OR '.join(keywords),nsfw),limit=self.search_limit)
		except ServerError:return None
	def comment_fit(self,search_data,id):
		comments=[]
		for p in search_data:
			if p.id==id:continue
			p.comment_sort='best'
			for top_level_comment in p.comments[0:5]:
				cmt=top_level_comment.body.splitlines()[0].lower()
				if cmt not in self.forbidden_comments and len(cmt)>0:self.comments.append(cmt)
		print('Collected : %s comments\n'%len(self.comments))
	def compare_sentences(self,s1,s2):
		if type(s1)==list:words_1=s1
		else:words_1=s1.split(' ')
		if type(s2)==list:words_2=s2
		else:words_2=s2.split(' ')
		if len(words_1)>=len(words_2):words_3=words_1;words_1=words_2;words_2=words_3
		w_ij=np.zeros((len(words_1),len(words_2)),float);e_ij=np.zeros((len(words_1),len(words_2)),float)
		for i in range(0,len(words_1)):
			for j in range(0,len(words_2)):
				w_ij[i][j]+=abs(len(words_1[i])-len(words_2[j]));word_1=words_1[i];word_2=words_2[j]
				if len(word_1)>=len(word_2):word_3=word_1;word_1=word_2;word_2=word_3
				for letter in range(0,len(word_1)):
					if word_1[letter]!=word_2[letter]:e_ij[i][j]+=1
		total=np.add(w_ij,e_ij);result=0;results=[];alpha=len(words_2)/len(words_1)
		while np.count_nonzero(total==0)>0:
			for i in range(0,len(words_1)):
				for j in range(0,len(words_2)):
					if total[i][j]==0:results.append((words_1[i],words_2[j],total[i][j]));result+=total[i][j];total[i]=np.Inf;total[0][j]=np.Inf
		for i in range(0,len(words_1)):
			if total[i][0]==np.Inf:continue
			row_min=0
			for j in range(0,len(words_2)):
				if total[i][j]<total[i][row_min]:row_min=j
			results.append((words_1[i],words_2[row_min],total[i][row_min]));result+=total[i][row_min];total[i]=np.Inf;total[0][j]=np.Inf
		return result+abs(len(s1)-len(s2))
	def find_best_fit(self,post):
		if len(x.comments)>0:
			z=np.full(len(x.comments),np.inf)
			for i in range(0,len(x.comments)):z[i]=x.compare_sentences(x.comments[i],x.keywords)
			row_mins=[];row_min=0
			for i in range(0,len(x.comments)):
				if z[i]<z[row_min]:row_min=i
			for i in range(0,len(x.comments)):
				if z[i]==z[row_min]or z[i]<=round(z[row_min]*self.alike_value):row_mins.append(i)
			row_min=row_mins[secrets.randbelow(len(row_mins))];cmt=x.comments[row_min];print('Best fit (found):',cmt);return cmt
		elif post.link_flair_text!=None:
			if len(x.replies[post.link_flair_template_id]['replies'])>0:cmt=x.replies[post.link_flair_template_id]['replies'][secrets.randbelow(len(x.replies[post.link_flair_template_id]['replies']))];print('Best fit (not found):',cmt);return cmt
			else:print('No fit :(');return None
	def postComment(self,post,cmt):
		if cmt:print('Found Match:',cmt);self.on_comment(post.id);print('Commented on: %s'%post.id)
	def doComment(self,post_id):
		self.check_posts();post=self.select_post()
		if post_id:post=reddit.submission(id=post_id)
		if not post:print("Couldn't find a suitable post :(");return
		print('POST ID    : %s'%post.id);print('URL        : https://reddit.com%s\n'%post.permalink);self.post_keywords(post);print('Searching similar posts...\n');similars=self.find_similar(post.title,post.over_18)
		if similars:self.comment_fit(similars,post.id)
		cmt=self.find_best_fit(post);self.postComment(post,cmt)
	def reply_on_comment(self,keyws=''):
		api=PushshiftAPI(reddit);all_comments=[];comments=[];keywords=keyws.split();x=BinComb(keywords);searches=x.get_combinations();print('Comment:',keyws);print('Searches:',len(searches))
		for search in searches[:2]:
			print('\nStarting search %s:'%(searches.index(search)+1));comments.append([]);gen=api.search_comments(q=search,subreddit='kgbtr',limit=1500);cache=[]
			for comment in gen:
				if len(cache)>2000:break
				if comment.body=='[deleted]'or comment.body=='[removed]':continue
				if len(comment.body.split())>=len(keywords)*3:continue
				if comment not in all_comments:cache.append(comment)
			comments[searches.index(search)]+=cache;all_comments+=cache
			if len(cache)>2:break
		print('\nENDED.')
		for result in comments:
			print('Length:',len(result));c=None
			if len(result)>0:
				tries=0
				while True:
					if len(result)==0:break
					c=result[secrets.randbelow(len(result))];c.refresh()
					if len(c.replies)>=1:break
					else:result.remove(c);c=None
			if c:break
		if c:
			to_comment=[]
			for reply in c.replies:
				if reply.body not in self.forbidden_comments:to_comment.append(reply.body)
			return to_comment[secrets.randbelow(len(to_comment))].lower()

### koyunkırpan kodu bitiş

condition=" "+condition
pulldata=runner()
completion=openai.Completion()
forbidden_comments=['[removed]','[deleted]','',' ',None]
non_bmp_map=dict.fromkeys(range(65536,sys.maxunicode+1),65533)
trans=lambda x:x.translate(non_bmp_map)
personality='Kerbal'
proh=['ataturk','erdogan','recep','tayip','tayyip','rte ','feto','fetullah','hdp','ocalan','demirtas','selahattin','teror','hukumet','sex','seks','yarra',' amı','got']
cont=''

def similar(a,b):return SequenceMatcher(None,a,b).ratio()
def checkmath(inp):
	if'!recset'in inp:return False
	mlist=['limit','derivative','integral','function','plot','polynomial','tangent','divide','substract','factorial','factoriel','?w']+list('π√~∞≠≈=');return any([i in inp for i in mlist])
def check_swears(inp):
	inp=fixer(inp);swords=['amk','amq','mal','salak',' sik',' oç ',' oc ',' ana',' ami','amcik','kancik','yarak','yarra',' got','serefsiz','hayvan',' oro',' ors','sex','seks']
	for i in swords:
		if i in inp:return True
	return False
def fixer(inp):
	dict_={'ü':'u','ı':'i','ö':'o','ş':'s','ğ':'g','ç':'c'}
	for i in inp:
		if i in dict_:inp=inp.replace(i,dict_[i])
	return inp
def rearrange(arranger):arranger=arranger.replace('aq','amk');arranger=arranger.replace('amk','');arranger=arranger.replace(' oc',' ');arranger=arranger.replace(' oç',' ');arranger=arranger.replace(' sg','siktir git');arranger=arranger.replace(' bot',' yapay zeka');arranger=arranger.replace('bot ','yapay zeka ');arranger=arranger.replace('kes lan','kapa çeneni');arranger=arranger.replace('flood','kısa hikaye');arranger=arranger.replace('yarra ','yarrağı');arranger=arranger.replace('31','mastürbasyon');return arranger.capitalize()
def tokenize(inp):punc=set('\\\'@#₺_&-+()/*:;!?",.1234567890');return[''.join((char for char in word if char not in punc))for word in inp.split()]
def ask(question,chat_log,defprompt,deftemp=1,recprompt=None,ocrimg=None):
	global personality,botrole;model='text-davinci-003'
	default_prompt = f'{personality} is a{condition} {botrole}. \n\n{chat_log}Human: {question}\n{personality}:'
	ocr_prompt = f'{personality} is a{condition} {botrole}. Human shows a picture to {personality} and they talk about it.\n\nThe text in the picture: {ocrimg}\n\n{chat_log}Human: {question}\n{personality}:'
	wolframalpha_prompt = f'Natural language to Wolfra Alpha query.\n\nInput: What is the integral value of x²+6x+7 between 2 and 6\nOutput: integral of x²+6x+7 from 2 to 6\n\nInput: sine of x factorial times square root of x plot\nOutput: plot sin(x!)√x\n\nInput: what is the 3rd derivative of x+√(x³-3)\nOutput: third derivative of x+√(x³-3)\n\nInput: {question}\nOutput:'
	if chat_log==None:chat_log=''
	if ocrimg==None:prompt=default_prompt
	else:prompt=ocr_prompt
	if recprompt!=None:prompt=recprompt
	try:prompt=''.join(prompt.split('None'))
	except:pass
	print('\n'+'-'*30);top_p=1
	if checkmath(prompt):question=question.replace('?w','');prompt=wolframalpha_prompt;deftemp=0.2;top_p=0.9;chm=True;max_tokens=200
	else:deftemp=0.85;chm=False;max_tokens=600
	response=completion.create(prompt=prompt,engine=model,stop=['Human',f"{personality}",'Human:',f"{personality}:"],temperature=deftemp,top_p=top_p,presence_penalty=1.3,frequency_penalty=1.6,max_tokens=max_tokens);answer=response.choices[0].text.strip()
	if'not'in answer and'sure'in answer:answer=response.choices[1].text.strip()
	if not chm:
		for i in ['\nHuman',f"\n{personality}",'Human:',f"{personality}:",'\n']:answer=answer.strip(i)
		if answer.count('Human:'):answer=answer.split('Human:')[0]
		if answer.count('human:'):answer=answer.split('human:')[0]
		if answer.count('insan'):answer=answer.split('insan:')[0]
		answer=en2tr.translate(prompt+answer).lower();answer=answer.split('insan:')[-1];answer=answer.split('kerbal:')[-1];answer=answer.split('kerbel:')[-1];answer='#'+answer;answer=answer.replace('#orada','#');answer=answer.replace('#!','#');answer=answer.replace('#o,','#no,');answer=answer.replace('#o','#no');answer=answer.replace('#y,','#');answer=answer.replace('#y ','#');answer=answer.replace('#,','#');answer=answer.replace('#','')
		if answer[0]in",.':;!?":answer=answer[1:]
		elif answer[1]in",.':;!?":answer=answer[2:]
		print('\n',prompt+answer,'\n')
	else:
		print('wolfram alpha activated:',answer)
		try:res=client.query(answer);answer=next(res.results).text;answer=answer.replace('^','\\^')
		except:return'emin değilim ama: '+answer
	return answer
revel=-1
print('Initializing...')
begin=time.monotonic()-(interval+10) #proximity -> 10
customrep={}
colids=[]
while revel+2:
	try:
		subreddit=reddit.subreddit('kgbtr')
		if round(time.monotonic()-interval)>interval:
			for i in subreddit.new(limit=5):
				if i.author not in forbidden_comments and not i.over_18 and i.id not in colids:
					url=i.url;text=None
					if url.endswith(('.jpg','.png','.gif','.jpeg')):
						try:text=tr2en.translate(str(api.ocr_url(url)));text='\n'.join(text.split('\n'))
						except:pass
					elif random.randint(0,80)>10:continue
					begin=time.monotonic()
					if text!=None:print('OCR metini algıladı.')
					begin=time.monotonic();print('Replying to:',trans(i.title))
					if i.selftext not in forbidden_comments:arranger=str(i.title)+'\n'+str(i.selftext)
					else:arranger=str(i.title)+'\n'
					arranger=arranger.lower();sc=check_swears(arranger);arranger=rearrange(arranger);arranger=tr2en.translate(arranger)
					try:out=ask(arranger,None,None,ocrimg=text)
					except:continue
					out=out.lower().replace('no.','hayır.');print(out)
					if out==None or out=='':continue
					i.reply(out.lower());colids.append(i.id);break
		time.sleep(20);revel+=1
		if revel%30==0:
			for item in reddit.redditor(username).comments.new(limit=100):
				if item.score<-2:print('removing');item.delete()
		for item in list(reddit.inbox.unread(limit=50))[::-1]:
			botrole=recover_botrole;item.mark_read()
			if item.submission.over_18:continue
			if str(item.subreddit).lower()=='evrimagaci':continue
			plist=[personality,'Human'];prev='';asc=0;parent=item;comment_author=item.author.name
			while True:
				person=plist[asc%2];asc+=1
				if asc>8:break
				if len(tokenize(prev))>400:break
				try:
					parent=parent.parent()
					try:check=parent.body.strip()
					except:
						try:check=' '.join((parent.title.strip()+' '+parent.selftext.strip()).split('\n'))
						except:break
					if username in check:break
					if'[deleted]'in check:asc-=1;continue
					if'!recset'in check:check=check.split('!recset')[-1];print('Executing:',check);exec(check)
					if parent.author.name.lower()!=username and comment_author!=parent.author.name:
						if'!load'not in check:asc=9
				except:check=None
				try:prev='{}: '.format(person)+rearrange(check.strip().capitalize())+'\n'+prev
				except:pass
			acqprev=prev
			try:prev=tr2en.translate(rearrange(prev))
			except:prev=''
			prev=prev.replace('human:','Human: ');prev=prev.replace('  ',' ');cont=item.body.strip().split('u/'+username)
			cont=' '.join(cont);arranger=cont.lower().strip();tokens=arranger.lower();tknized=tokenize(arranger)
			breakit=0
			for pre in preset:
				if pre in tknized and len(tknized)<5:item.reply(preset[pre]);breakit=1;break
			if breakit:continue
			if arranger=='!remove'and item.author.name.lower()in admins:
				try:item.parent().delete()
				except:pass
				continue
			elif arranger=='!stop'and item.author.name.lower()in admins:sys.exit(0)
			elif '!set' in arranger and item.author.name.lower()in admins:exec(arranger.split('!set')[-1].strip());item.reply('Değişiklik yapıldı.');continue
			if 'good bot' in arranger:item.reply(':)');continue
			elif 'bad bot' in arranger:item.reply('siktir git o zaman');continue
			sc=check_swears(arranger)
			if sc:item.downvote();continue
			else:item.upvote()
			if 'listele' in arranger or 'nedir' in arranger:deftemp=0.3
			else:deftemp=1
			arranger=rearrange(arranger);fixed=fixer(arranger.lower())
			if any((i in fixed for i in proh)):print('Prohibited content detected.');continue
			cont=tr2en.translate(arranger);newprompt=f"{personality} is a{condition} {botrole}. \n\n{prev}\nHuman: {cont}\n{personality}:";out=ask(cont,prev,None,deftemp=deftemp,recprompt=newprompt);out=out.lower().replace('no.','hayır.')
			try:
				if out in prev:continue
			except:pass
			repseq=''
			try:repseq=customrep[item.author.name.lower()]
			except:pass
			try:
				if item.parent().body.strip().lower()!=out.lower():
					print(out);print('-'*20);toreply=out.lower()+repseq
					if toreply in acqprev or similar(toreply,item.parent().body.strip())>0.7 or similar(toreply,item.body.strip())>0.7 or'neden bahsettiğini'in toreply or'üzgünüm'in toreply:toreply=pulldata.reply_on_comment(item.body.strip())
					nc=item.reply(toreply);ntext=nc.body.strip()
					if'![img]'in ntext:nc.edit(ntext)
					elif'![gif]'in ntext:nc.edit(ntext)
					time.sleep(3)
			except:
				toreply=out.lower()+repseq
				try:
					if toreply in acqprev or similar(toreply,item.parent().body.strip())>0.7 or similar(toreply,item.body.strip())>0.7 or'neden bahsettiğini'in toreply or'üzgünüm'in toreply:toreply=pulldata.reply_on_comment(item.body.strip())
				except AttributeError:pass
				nc=item.reply(toreply)
	except Exception as e:
		exc_type,exc_obj,exc_tb=sys.exc_info();fname=os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		try:print(exc_type,fname,exc_tb.tb_lineno)
		except:print(exc_type,fname,exc_tb.tb_lineno)
