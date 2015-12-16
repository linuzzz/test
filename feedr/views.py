# -*- coding: utf-8 -*-

import feedparser
import json

import logging
import logging.handlers

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseForbidden

from .models import Source, Feed

from datetime import datetime

LOG_FILENAME='feedr.log'

# Set up a specific logger with our desired output level
flogger = logging.getLogger('feedr')
flogger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000, backupCount=10)
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

flogger.addHandler(handler)

flogger.info('Feedr app start')

# Create your views here.

# do not call this function "login" or it will confuse the login from django.contrib.auth 
def auth(request):
   error = ""
   
   if request.method == "POST":
      u = request.POST.getlist("user")[0]
      p = request.POST.getlist("password")[0]
      
      user = authenticate(username=u, password=p)
      if user is not None:
         if user.is_active:
            #error = "You provided a correct username and password!"
            flogger.info('Valid login from: ' + u)
            login(request,user)
            return redirect('list')
         else:
            error = "Your account has been disabled!"
            flogger.warning('Login attempt from disabled account: ' + u) 
      else:
         error = "Your username or password were incorrect." 
         flogger.warning('Invalid login from: ' + u)   
      
   elif request.method == "GET":
      pass
      
   return render(request,"login.html", {"error":error})
   
def deauth(request):
   logout(request)
   return redirect('auth')   

def list(request, cat="all", limit="10"):
   if request.user.is_authenticated():
      '''
      intlimit = int(limit)
      
      #distinct categories of feeds
      source = Source.objects.order_by('category').values('category').distinct()
      
      #get number of unread items for every source
      unread = {}
      for s in source:
         u = Feed.objects.filter(source__category=s['category']).filter(read=False).order_by('-pubDate').count()
         unread[s['category']]=u
      ###
      '''                  
      if cat == "all":
         feed = Feed.objects.filter(read=False).order_by('-pubDate')   
      else:
         feed = Feed.objects.filter(source__category=cat).filter(read=False).order_by('-pubDate')
      
      #return render(request, 'menu.html', {'feeds': feed[:intlimit], 'total': feed.count(), 'limit': intlimit, 'newlimit': intlimit + 10, 'category': cat, 'unread': unread, 'view':'list'})
      return showfeed(request,cat,limit,feed,'list')  
   else:
      return redirect('auth')   
      

def favorites(request, cat="all", limit="10"):
   if request.user.is_authenticated():
      '''      
      intlimit = int(limit)
      
      #distinct categories of feeds
      source = Source.objects.order_by('category').values('category').distinct()
      
      #get number of unread items for every source
      unread = {}
      for s in source:
         u = Feed.objects.filter(source__category=s['category']).filter(read=False).order_by('-pubDate').count()
         unread[s['category']]=u
      ###
      '''            
      if cat == "all":
         feed = Feed.objects.filter(favorite=True).order_by('-pubDate')   
      else:
         feed = Feed.objects.filter(source__category=cat).filter(favorite=True).order_by('-pubDate')
      
      ###
      #return render(request, 'menu.html', {'feeds': feed[:intlimit], 'total': feed.count(), 'limit': intlimit, 'newlimit': intlimit +10, 'category': cat, 'unread': unread, 'view':'favorites'})
      ###
      return showfeed(request,cat,limit,feed,'favorites')         
   else:
      return redirect('auth')   


#function to show list of feeds or favorites: called by the view list or favorites
#not mapped to a url
def showfeed(request, cat, limit, feed, view):
   intlimit = int(limit)
   
   #distinct categories of feeds
   source = Source.objects.order_by('category').values('category').distinct()
      
   #get number of unread items for every source
   unread = {}
   for s in source:
      u = Feed.objects.filter(source__category=s['category']).filter(read=False).order_by('-pubDate').count()
      unread[s['category']]=u
   
   #the unread dictionary contains also the category names used in the templates for the sources menu. doesn't need anymore to pass the object source   
   #feeds contains the feed in the db to display
   #total is the total number of unread article, useful for pagination
   #limit hardcoded to 10 for pagination
   #newlimit for the url in action of the "load more" button
   #category to build the url...a source category or "all"
   #unread to display bootstrap badges of unread articles
   #view to build the url action for the "load more" button
   return render(request, 'menu.html', {'feeds': feed[:intlimit], 'total': feed.count(), 'limit': intlimit, 'newlimit': intlimit +10, 'category': cat, 'unread': unread, 'view':view})


#toggle favorite status      
def fav(request, feedid):
   if not request.user.is_authenticated():   
      return HttpResponseForbidden()
      
   f = Feed.objects.filter(id=feedid)
      
   if getattr(f[0],'favorite'):    
      f.update(favorite=False)
   else:
      f.update(favorite=True)

   json_data = json.dumps({"result":"True"})
   return HttpResponse(json_data, content_type="application/json")


#toggle mark as read status      
def read(request, feedid):
   if not request.user.is_authenticated():   
      return HttpResponseForbidden()
      
   f = Feed.objects.filter(id=feedid)
      
   if getattr(f[0],'read'):    
      f.update(read=False)
   else:
      f.update(read=True)

   json_data = json.dumps({"result":"True"})
   return HttpResponse(json_data, content_type="application/json")


#toggle mark as read status for many     
def readall(request):
   if not request.user.is_authenticated():   
      return HttpResponseForbidden()
      
   if request.method == 'POST':
      for r in request.POST:
         try:
            #valid id articles to be marked as read are integers
            ir = int(request.POST.get(r))
            f = Feed.objects.filter(id=ir)
            f.update(read=True)
         except:
            #this is to filter out csrf token that is not an integer id for an article feed
            #csrf has to be passed manually by jquery post because of django csrf protection
            pass         
   
   json_data = json.dumps({"result":"True"})
   return HttpResponse(json_data, content_type="application/json")

            
def refresh(request):
   if not request.user.is_authenticated():   
      return HttpResponseForbidden()
   
   flogger.info("refreshing...")  
   
   source = Source.objects.all()

   news = 0   
   for s in source:
      url = s.url 
      
      #bandwidth saving with etag and last-modified (http headers)
      if s.etag != "":
         feed = feedparser.parse(url, etag=s.etag)
      elif s.modified != "":
         feed = feedparser.parse(url, modified=s.modified)
      else:
         feed = feedparser.parse(url)
           
      if feed.has_key('etag'):
         s.etag = feed.etag
         s.save()
      if feed.has_key('modified'):
         s.modified = feed.modified
         s.save()
         
      #feed status == 200 to load new items
      #feed status == 301 permanently moved
      if feed.has_key('status'):
      	if feed.status == 301:
      		flogger.warning("feed url permanently moved, please check new url:" + feed.href) 
      	elif feed.status != 200:
      	   flogger.debug("feed already loaded - {} - {} ".format(feed.href,feed.status))
      	   continue
      else:
         flogger.warning("Error loading source feed, please check url:" + feed.href)
                 
      
      for f in feed.entries:
         #some feeds doesn't have a link...pass
         if f.has_key('link'):
            pass
         else:
            continue
            
         #verifico che l'articolo non sia gia presente
         try:
            old = Feed.objects.get(link=f.link)
            #already in db...go to next article
            continue
         except:
            news = news + 1
         
         #datetime in formato che sqlite gradisce
         if f.has_key('published_parsed'):         
            p = f.published_parsed
            pdate = datetime(p[0], p[1], p[2], p[3], p[4])
            pubDate = datetime.strftime(pdate,"%Y-%m-%dT%H:%M")
         elif f.has_key('updated_parsed'):
            p = f.updated_parsed
            pdate = datetime(p[0], p[1], p[2], p[3], p[4])
            pubDate = datetime.strftime(pdate,"%Y-%m-%dT%H:%M")
         else:
            pubDate = datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M")
                        
         mylist = []
         mylist.append(f.description)
         mylist.append(f.summary)
         try:
            mylist.append(f.content[0]['value'])
         except:
            mylist.append("")
            
         #get the longest text between summary, description and content: differents feeds has different fields         
         contenuto = max(mylist, key=len)
            
         feed = Feed(source=s, title=f.title, summary=f.summary, content=contenuto, link=f.link, pubDate=pubDate, read=False, favorite=False)
         feed.save()
   
   flogger.info(str(news) + ' new feeds!!!')
   
   response_data = {}
   response_data['result'] = 'True'
   response_data['news'] = str(news)
   json_data = json.dumps(response_data)
   return HttpResponse(json_data, content_type="application/json")
   
def logs(request):
   if not request.user.is_authenticated():   
      return HttpResponseForbidden()
         
   f = open(LOG_FILENAME, 'r')
   logs = ''
   for line in f:
      logs = logs + "<p>" + line + "</p>"
   
   f.close   
   return HttpResponse(logs)
   