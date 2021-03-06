# Author: Anshuman kumar
# Name: moodleFunction.py
# It syncs all the file from your moodle to a directory in your computer

#    Copyright (C)  2014 Anshuman kumar

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


import urllib, urllib2, cookielib
from bs4 import BeautifulSoup
import ast
history = {}
def getCourseList(openlink,url):
    """
        This function takes the login instance of moodle and get all
        the course name and link
        @input open moodle link instance , url of moodle website
        @output The dictionary consisting of course name and its instance. 
    """
    courseList = {}
    mainPage = openlink.open(url)
    mainPageB = BeautifulSoup(mainPage)
    courseDataList = mainPageB.find_all('h3','coursename')
    for courseData in courseDataList:
        linktoCoursePage = courseData.find('a').get('href',None)
        courseName =  str(courseData.find('a').contents[0])
#        if (courseName == 'CS 663-2015-1 Fundamentals of Digital Image Processing'):
        courseList[courseName] = linktoCoursePage
    return courseList

def getCourseContent(courselink,openlink):
    coursePage = openlink.open(courselink)
    coursePageB = BeautifulSoup(coursePage)
    coursePageB = coursePageB.find('div', 'course-content')
    forumInfo =  coursePageB.find('li', 'modtype_forum') 
    forumLink = forumInfo.find('a').get('href',None)
    forumPage = openlink.open(forumLink)
    #print(forumPage.info())
    forumPage = BeautifulSoup(openlink.open(forumLink))
    linkForum = forumPage.find_all('td', 'topic')
    linkInfo = coursePageB.find_all('li', ['modtype_resource','modtype_url'])
    length = len(linkInfo)
    i = 0
    while(i <length):
        linkInfo[i] = linkInfo[i].find('a').get('href',None)
        if '/mod/url' in linkInfo[i]:
            tempPage = openlink.open(linkInfo[i])
            tempPageB = BeautifulSoup(tempPage);
            tempinfo = tempPageB.find_all('div', 'urlworkaround')
            for k in range(0,len(tempinfo)):
                linkInfo.append(tempinfo[k].find('a').get('href',None))
            del linkInfo[i];
            length = length -1
            i = i-1
        #print(linkInfo[i])
        i=i+1

    for i in range(0,len(linkForum)):
        linkForum[i] = linkForum[i].find('a').get('href',None)
        topicPage = BeautifulSoup(openlink.open(linkForum[i]))
        attacInfo = topicPage.find_all('div', 'attachments')
        for attac in attacInfo:
            attac = attac.find('a').get('href',None)
            linkInfo.append(attac)
    return linkInfo

def openHistory(dirName):
    global history
    try:
        f = open(dirName +'/history','r')
        history = ast.literal_eval(f.read())
        f.close()
    except IOError:
        history = {}

def saveFiles(filelist,dirname,openlink):
    for files in filelist:
        if files in history:
            print("Already Saved")
            continue
        print(files)
        try:
            openfile = openlink.open(files)
        except urllib2.HTTPError:
            continue
        global history
        try:
            history[files] = openfile.info()['Last-Modified']
        except KeyError:
            continue
        if  openfile.info()['Content-Type']!="text/html; charset=utf-8":
            #print(openfile.info())
            try:
                current = openfile.info()['content-disposition'].split('=')[1].replace('"','')
            except KeyError:
                current = files.split('/')[-1]
            if current != '':
                f = open(dirname +'/'+str(current), 'wb')
                f.write(openfile.read())
                f.close()

def saveHistory(dirName):
    f = open(dirName + '/history','w')
    f.write(str(history))
    f.close()
