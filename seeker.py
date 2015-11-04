#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import html
from lxml import etree
import lxml
from BeautifulSoup import BeautifulSoup
import argparse
import re
import requests
import dryscrape
import os
import sys
import threading
from libs import VideoFiles

standalone_episode_regexs = [
    # Newzbin style, no _UNPACK_
    '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',
    # standard s00e00
    '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'
]

episode_regexps = [
    # S03E04-E05
    '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)[\._ ]*([- ]?[sS](?P<secondSeason>[0-9]+))?([- ]?[Ee+](?P<secondEp>[0-9]+))?',
    # S03-03
    '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',
    # 3x03, 3x03-3x04, 3x03x04
    '(?P<show>.*?)([^0-9]|^)(?P<season>(19[3-9][0-9]|20[0-5][0-9]|[0-9]{1,2}))[Xx](?P<ep>[0-9]+)((-[0-9]+)?[Xx](?P<secondEp>[0-9]+))?',
    # SP01 (Special 01, equivalent to S00E01)
    '(.*?)(^|[\._\- ])+(?P<season>sp)(?P<ep>[0-9]{2})([\._\- ]|$)+',
    # .602.
    '(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z%]|$)'
]


def download(filename):
    url = 'http://www.tusubtitulo.com/updated/1/44122/0'
    r = requests.get(url, headers={'referer': 'http://www.tusubtitulo.com'})

    #d = r.headers['content-disposition']
    #fname = re.findall("filename=(.+)", d)
    # print fname[0][1:-1]

    with open(filename[:-len(remove)] + '.srt', 'wb') as subtitle:
        subtitle.write(r.content)


def removeNotValidLines():
    # Remove not valid
    with open('dict.txt') as f, open('dictWoSp.txt', "w") as working:
        for line in f:
            if 'Title not available' not in line:
                working.write(line)


def addCharacters():
    # Remove not valid
    with open('dict.txt') as f, open('dictWoSp.txt', "w") as working:
        for line in f:
            newline = line[:line.index(':') + 1] + "'" + line[line.index(':') + 1:-2] + "',\n"
            # print line[':']
            working.write(newline)

parsed = 0

baseUrl = "http://www.tusubtitulo.com/show/"


def testHtmlParser(start, stop):

    global parsed
    with open("dict.txt", "a") as myfile:
        for page in xrange(start, stop):
            parsed = parsed + 1
            print parsed
            # print "Parsing: %s%s" % (baseUrl, page)
            pageHtml = requests.get(baseUrl + str(page))
            tree = html.fromstring(pageHtml.text)
            title = tree.xpath('//p[@class="titulo"]/text()')
            try:
                title = unicode(title[0]).encode('utf-8')
            except IndexError:
                title = 'Title not available'
            # print "Título %s" % (title)
            try:
                string = "'%s':'%s',\n" % (title, page)
                if 'Title not available' not in string:
                    myfile.write(string)
                    print string
            except IndexError:
                string = "'%s':'%s',\n" % ('Title not available', page)
                # myfile.write(string)
                print string
            # print 'Parsed %s of 2572' #%s%% completado.' % (page, page/float(2572)*100)
    print >> sys.stderr, 'Finished OK.'
    # print '}'
    # sys.exit(0)


def startSeeking(show, season, episode):
    print "%s %sx%s" % (show, season, episode)
    print baseUrl + dict_from_file[show]
    url = "http://www.tusubtitulo.com/serie/%s/%s/%s/%s" % (
        show.lower(), season, str(int(episode)), dict_from_file[show])
    pageHtml = requests.get(url)
    tree = html.fromstring(pageHtml.text)
    for version in tree.xpath('//div[@id="version"]/div/blockquote/p/text()'):
        ve = version.lstrip()
        if ve:
            print "Este subtitulo contiene: " + ve.split(' ')[1]

    # print lxml.html.tostring(html.fromstring(pageHtml.text))
    # print pageHtml.text
    soup = BeautifulSoup(pageHtml.text)
    # print soup.find("div", {"id": "version"})

    #        print a
    # for item in session.at_xpath("//*[@id='episodes']/text()"):

    # print a
    # for items in a:
    #    print items
    # for table in span.find_all('table'):
    #    print table  # ['episodes'], span.text
    # print span
    #tree = html.fromstring(pageHtml.text)
    #title = tree.xpath('//p[@class="titulo"]/text()')

dict_from_file = {}
titles = []

if __name__ == "__main__":
    dryscrape.start_xvfb()
    parser = argparse.ArgumentParser()
    print "Execution Started"
    #folder = getFolderFromCommandLine
    folder = "."
    filename = ""
    remove = ""
    # removeNotValidLines()
    # addCharacters()

    with open('dict.txt', 'r') as inf:
        dict_from_file = eval(inf.read())
        print dict_from_file['Limitless']

    with open('titles.txt', 'r') as titlesfile:
        for line in titlesfile:
            titles.append(line)

    startSeeking("Arrow", 4, "01")

    # Key = 'Agents of'
    # try:
    #     print dict_from_file['pepe']
    # except KeyError:
    #     print "%s not found, maybe you meant: " % (Key)
    #     for line in titles:
    #         if Key in line:
    #             print line
    # with open('titles.txt','a') as titles:
    #    for key in dict_from_file:
    #        titles.write(key+'\n')

    # Coge el nombre del primer MKV que encuentra.
    x1 = False
    if x1 is True:
        fileset = set()
        already_downloaded = set()

        for file in os.listdir(folder):
            if file.endswith(".mkv"):
                filename = str(file)
                remove = os.path.splitext(os.path.basename((folder + filename)))[1]
                fileset.add(filename[:-len(remove)])
            if file.endswith(".srt"):
                filename = str(file)
                remove = os.path.splitext(os.path.basename((folder + filename)))[1]
                already_downloaded.add(filename[:-len(remove)])

        for mkvfile in fileset:
            if mkvfile not in already_downloaded:
                for rx in episode_regexps[0:-1]:
                    match = re.search(rx, mkvfile, re.IGNORECASE)
                    if match:
                        show = match.group('show')
                        # Se convierte a int para quitar los 0 de delante. El formato de
                        # tusubtitulo.com es 'Show 1x01'
                        season = match.group('season')
                        episode = match.group('ep')
                        # Clean title.
                        name, year = VideoFiles.CleanName(show)
                        if year is not None:
                            name = "%s %s" % (name, year)
                        # print "Descargaremos subtitulos de: %s Temporada: %s, Capítulo: %s" %
                        # (name, season, episode)
                        #searchString = "%s %sx%s" % (name, int(season), episode)
                        # print searchString
                        startSeeking(name, int(season), episode)
            # else:
                # print "Subtitles for: %s are already downloaded" % (mkvfile)

    # download(filename)
