# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import praw 
from termcolor import colored 
import time 
#Log into PRAW with script credentials 

r = praw.Reddit('<your login credentials>')

print(colored('Logged in as: ' + str(r.user.me()), 'green'))
                     

#Generate comment for a subreddit     
#Using their flairs and wiki settings
def generateComment(subm, mins):
    template = '''This post has automatically been removed for not being flaired within {mins} minutes. When the post receives a flair it will automatically be restored. If you are on mobile, reply to this comment with one of the following commands and the bot will flair it accordingly.\n\n
Flair | Command
---|---
{flairs}
\n\n
If you believe that this removal was a mistake, please [contact the moderators.](https://www.reddit.com/message/compose?to=%2Fr%2F{subr})'''.format(mins=mins, flairs=getChoices(subm, True), subr=subm.subreddit)
    return template 
    
def generateWiki(sub):
    print('GENNNERRATTTINGGG')
    r.subreddit(sub).wiki.create('FlairTimeBot', '''#This is the configuration page for /u/FlairTimeBot. Do not adjust any of the text, only the values!
                                              \n\n**Time until posts without flair are removed (minutes):** 10
                                              \n\n**Time users have to add flair after post is removed (hours; max is 72):** 24
                                             ''', reason='Initializing Flair Time Bot')


def getSettings(subr):
    wiki = r.subreddit(subr).wiki['FlairTimeBot']
    wCon = str(wiki.content_md).split('values!')[1]
    mins = int(round(float(str(wCon.split(':')[1])[0:8].strip('**').strip(' ').replace(' ','').replace('\n','').replace('\r',''))))
    hrs = float(str(wCon.split(':')[2])[:].strip('**').strip(' ').replace(' ','').replace('\n','').replace('\r',''))
    return mins, hrs
        

def getChoices(subm, isReport):
    if isReport:
        return '\n'.join([flair['flair_text'].encode('utf-8') + ' | -' + flair['flair_text'].encode('utf-8') for flair in subm.flair.choices()])
    else:
        flist =  [flair['flair_text'].encode('utf-8') for flair in subm.flair.choices()]
        fclist = [flair['flair_css_class'].encode('utf-8') for flair in subm.flair.choices()]   
        mdict = dict(zip([x.encode('utf-8').lower().rstrip() for x in flist], fclist))
        return flist, mdict 
    
#Initialize Database 

import sqlite3
conn = sqlite3.connect('genposts.db');
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS rposts (id TEXT, created TEXT, parentId TEXT, isremoved TEXT);''')

#rposts --> id, created, isremoved


#get id, time created, and removal status from post if it exists
#otherwise, return False 
def getInfo(ident):
    t = (ident,)
    for row in c.execute('''SELECT * FROM rposts WHERE id=?''', t):
        postId = row[0]
        time_created = row[1]
        isRemoved = row[2]
        return [postId, time_created, isRemoved]
    return False

#list all posts in the database 
def listAll():
    for row in c.execute('''SELECT * FROM rposts'''):
        print(row)
  
#add a post for the first time when removing it     
def addPost(ident, timec, parId, isRem):
    c.execute('''INSERT INTO rposts VALUES ({}, {}, {}, {})'''.format(ident, timec, parId ,isRem))
    

#delete all posts (only used for bugfixing)
def deleteAll():
    c.execute('''DELETE FROM rposts''')

#delete post with specific id from database 
def deleteSpec(ident):
     t = (ident,)
     c.execute('''DELETE FROM rposts WHERE id=?''', t)
 
 
#return the age of a post in minutes 
def checkAge(post):
    print('Started age check')
    ctime = time.time() + 28800
    difference =  float(ctime) - post.created
    print('Checked age')
    return difference/60
    
#second main function; check for old, unflaired posts 

def checkForOld(post, qmins):
    if checkAge(post)>qmins and post.link_flair_text == None and getInfo(post.id) == False:
        myComment = post.reply(generateComment(post, qmins))
        myComment.mod.distinguish(how='yes', sticky=True)
        post.mod.remove()
        addPost(post.id, str(post.created), myComment.id, 'true')
    print('Checked for old')
#third main function; database checker/complex question checking 

def checkDatabase():
    for row in c.execute('''SELECT * FROM rposts'''):
        postId = row[0]
        postCreated = row[1]
        parId = row[2]
        postRemoved = row[3]
        actualPost = r.submission(id=postId)
        qmins, fmins = getSettings(str(actualPost.subreddit))
        fmins *= 60 
        if str(actualPost.author) == 'None':
            deleteSpec(actualPost.id)
            r.comment(id=parId).edit('This post has been deleted and can no longer be restored.')
        elif postRemoved == 'true': 
            if checkAge(actualPost) > fmins:
                r.comment(id=parId).edit('This post is older than {} hours and can no longer be reapproved. Please resubmit and flair in time.'.format(fmins/60))
                deleteSpec(actualPost.id)
            elif actualPost.link_flair_text != None:
                r.comment(id=parId).delete()
                actualPost.mod.approve()
                deleteSpec(actualPost.id)

def correctPerms(subr):
    for moderator in r.subreddit(subr).moderator():
        if str(moderator).lower() == 'flairtimebot':
            mperms = moderator.mod_permissions
            if 'all' in mperms:
                return True
            elif 'wiki' not in mperms or 'posts' not in mperms or 'flair' not in mperms:
                return False
            else:
                return True

def checkInvites():
    for message in r.inbox.unread(limit=5):
        message.mark_read()
        if message.body.startswith('**gadzooks!') and message.subreddit != None:
            try:
                r.subreddit(str(message.subreddit)).mod.accept_invite()
                if not correctPerms(str(message.subreddit)):
                    r.subreddit(str(message.subreddit)).moderator.leave()
                    message.reply('Error: Incorrect permissions. This bot requires the wiki, post, and flair permissions to function properly. Please re-invite it accordingly.')
                else:
                    generateWiki(str(message.subreddit))
                    print('GenXd Page')
                    message.reply('Setup successful. Thank you for using /u/FlairTimeBot! You can access the configuration here: https://www.reddit.com/r/{}/wiki/flairtimebot\n\nAny complaints or bug reports should be sent to the developer.'.format(str(message.subreddit)))
            except:
                message.reply('There was an error joining the subreddit. Please try again or contact the developer for support.')
                try:
                    r.subreddit(str(message.subreddit)).moderator.leave()
                except:
                    pass
        elif message.body.startswith('**gadzooks!')  and message.subreddit == None:
            message.reply('Nice try, I\'m uncrashable ;)')
        

def checkComments():
    for comment in r.inbox.comment_replies(limit=30):
        if comment.id not in open('dcomments.txt', 'r').read().split('\n') and comment.body.encode('utf-8')[0] == '-' and str(comment.author).lower() == str(comment.parent().parent().author).lower():
            if  'older than' in comment.parent().body.encode('utf-8'):
                r.redditor(str(comment.author)).message('Unable to assign flair to post.', '**Error:** Post is no longer eligible to be flaired (too old).')
                return False 
            subm = comment.parent().parent()
            pflair = comment.body.encode('utf-8').strip('-').rstrip()
            print(pflair.lower())
            flair_list, fdict = getChoices(subm, False)
            if pflair.lower() in [x.encode('utf-8').lower().rstrip() for x in flair_list]:
                subm.mod.flair(text=flair_list[[x.encode('utf-8').lower().rstrip() for x in flair_list].index(pflair.encode('utf-8').lower())], css_class=fdict[pflair.lower().rstrip()])
                comment.mod.remove()
                open('dcomments.txt','a').write(comment.id + '\n')
            else:
                r.redditor(str(comment.author)).message('Unable to assign flair to your post.', '**Error:** Invalid flair option ({}).'.format(pflair))

def checkInbox():
    checkInvites()
    checkComments()

def runTimeBot():
    cmdict = {}
    x = 0
    for post in [y for y in r.subreddit('mod').new(limit=50) if y.link_flair_text == None]:
        print(colored('Going for time {}'.format(x), 'green'))
        x+=1
        try:
            mlist = cmdict[str(post.subreddit)]
        except:
            print('Nope')
            mlist = [str(mod) for mod in r.subreddit(str(post.subreddit)).moderator] 
            cmdict[str(post.subreddit)] = mlist
        print('Got moderators')
        if str(post.author).lower() != "automoderator" and str(post.author) not in mlist and post.link_flair_text == None:
            mins, hrs = getSettings(str(post.subreddit))
            checkForOld(post, mins)
    checkInbox()
    checkDatabase() 
    conn.commit()
    


while True:
    try:
        runTimeBot()
    except Exception as e:
        print(str(e))
