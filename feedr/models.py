from __future__ import unicode_literals

from django.db import models
#from django.utils import timezone

# Create your models here.

class Source(models.Model):
   category = models.CharField(max_length=30)
   title = models.CharField(max_length=200)
   url = models.TextField()
   etag = models.CharField(max_length=50, blank=True, default="")
   modified = models.CharField(max_length=50, blank=True, default="")
   
   def add(self):
      #self.published_date = timezone.now()
      self.save()
   
   '''  
   @classmethod
   def create():
      return self
   '''
      
   def get_sources():
      return self.objects   

   def __str__(self):
      return self.title
      
      
class Feed(models.Model):
   source = models.ForeignKey(Source)
   title = models.TextField()
   summary = models.TextField()
   content = models.TextField(blank=True, default="")
   link = models.TextField()
   pubDate = models.CharField(max_length=50, blank=True, default="")
   read = models.BooleanField()
   favorite = models.BooleanField()
   
   def add(self):
      self.save()
      
   def __str__(self):
      return self.title