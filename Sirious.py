#!/usr/bin/python
import dbus
import json
import urllib
import subprocess
import os,sys
import time
import bleach

# Clipboard content from Ctrl+C or middle-click or just selection is given for search

try :
    clipboard_content = subprocess.check_output(["xclip", "-o"])
except subprocess.CalledProcessError as e:
    returncode = e.returncode
    if returncode != 0 :
        print "String not found"
        exit()
clipboard_content = clipboard_content.replace("\n","")
clipboard_content = clipboard_content.replace("  ","")
clipboard_content = clipboard_content.replace("\""," ")

if clipboard_content == "" or len(clipboard_content) <2 :
    print "String found is less the typical search length"
    exit()

#------- DBus Notification setup
    
bus = dbus.SessionBus()
notifications = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
interface = dbus.Interface(notifications, 'org.freedesktop.Notifications')

#------- DuckDuckGo API --

link = "http://api.duckduckgo.com/?q=" + urllib.quote_plus(clipboard_content) + "&format=json&pretty=1"
response = urllib.urlopen(link)
json_response = response.read()

#--- No reply from API case
search_content = "Check Net Connection"
if json_response == "" :
    interface.Notify('Sirious',12,"/home/harish/Sirious/Sirious.png",title,search_content,'','',-1)#change
    exit()

data_unicode = json.loads(json_response)
scan = "\n"
scan += data_unicode["AbstractSource"] + "  "
scan += data_unicode["AbstractURL"]
url = data_unicode["Image"]
filename = url.split('/')[-1]#image name
location = os.getcwd()
search_content = "Try refining the search term" #searchresult

#--- Image retrieve and resize
import PIL
from PIL import Image
size = 128, 128
location = location + "/" + filename
if url != "":
    urllib.urlretrieve(url,filename)
    try:
        im = Image.open(filename)
        im = im.resize(size,PIL.Image.ANTIALIAS)
        im.save(filename)
    except IOError:
        print "cannot create imageresize for '%s' " % filename
    dict = {'image-path':location};#change location
else:
    dict = {'image-path':'/home/harish/Sirious/DDG.png'};#change location


#--- Parsing JSON
if data_unicode["Type"] == 'D' :
    search_content = data_unicode["RelatedTopics"][0]["Text"]
    
if data_unicode["Type"] == 'A' :
    search_content = data_unicode["AbstractText"]
    
if data_unicode["AnswerType"] != "":
    search_content = bleach.clean(data_unicode["Answer"])
    
if data_unicode["AnswerType"] == "color_code":
    search_content = "Try refining the search term"
    
if data_unicode["Type"] == 'C' :
    title = "Sirious : " + str(data_unicode["Heading"])
    for item in data_unicode["RelatedTopics"]:
        search_content = item["Text"]
        interface.Notify('Sirious',12,"/home/harish/Sirious/Sirious_icon.png",title,search_content,'',dict,10000)#change icon image location
    exit()

#--- Display as Notification    
search_content = search_content + scan + str("\n\n\t\t\t\t-Results from DuckDuckGo")
title = "Sirious : " + str(data_unicode["Heading"])
interface.Notify('Sirious',12,"/home/harish/Sirious/Sirious_icon.png",title,search_content,'',dict,10000)#change icon image location)
time.sleep(2)
#---Remove temporary image file
if url != "":
    os.remove(location)
