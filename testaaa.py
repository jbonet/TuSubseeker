#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from lxml import html
import lxml
import argparse
import pycurl
import urllib2
import re
import requests
import os
import sys
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

equivalences = {
    'LOL': 'DIMENSION',
    'SYS': 'DIMENSION',
    'XII': 'IMMERSE'
}

showCodesDict = {}


def downloadSubtitle(show, season, episode, release):

    if release is not None:
        print("Iterar..., de momento me salgo e ya")
        url = "http://www.tusubtitulo.com/serie/%s/%s/%s/%s" % (
            show.lower(), season, str(int(episode)), showCodesDict[show])
        pageHtml = requests.get(url)
        tree = html.fromstring(pageHtml.text)
        for version in tree.xpath('//div[@id="version"]/div/blockquote/p/text()'):
            ve = version.lstrip()
            if ve:
                print("Este subtitulo contiene: " + ve.split(' ')[1])
                if equivalences[ve.split(' ')[1]] == release or release == ve.split(' ')[1]:
                    print("OK")
        sys.exit(0)

    if len(chapter) == 1:
        chapter = '0' + chapter
    url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
        show, season, chapter, showCodesDict[show])
    print(url)
    language_codes = {'es': 5, 'en': 1}
    search = "http://www.tusubtitulo.com/updated/5/(?P<code>[0-9]+)/0"
    search_alt = "http://www.tusubtitulo.com/updated/4/(?P<code>[0-9]+)/0"
    lang = ""

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'es-ES,es;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.tusubtitulo.com'
    }

    page_content_req = urllib2.Request(url, headers=headers)
    page_content = urllib2.urlopen(page_content_req).read()

    try:
        code = re.search(search, page_content).group(1)
        lang = "5"
    except:
        try:
            code = re.search(search_alt, page_content).group(1)
            lang = "4"
        except:
            print("No encontrado :(")

    try:
        c = pycurl.Curl()
        c.setopt(c.URL,
                 "http://www.tusubtitulo.com/updated/%s/%s/0" % (lang, code))
        c.setopt(c.HTTPHEADER, ['Accept-Encoding: gzip, deflate, sdch',
                                'Accept-Language: es-ES,es;q=0.8',
                                'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
                                'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                'Referer: %s' % (url)])
        f = open('%s-%sx%s.srt' % (show, season, chapter), 'wb')
        c.setopt(c.WRITEDATA, f)
        c.perform()
        print("Listo :)")
    except:
        print("Probando a descargar el original...")
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, "http://www.tusubtitulo.com/original/(?P<code>[0-9]+)/0")
            c.setopt(c.HTTPHEADER, ['Accept-Encoding: gzip, deflate, sdch',
                                    'Accept-Language: es-ES,es;q=0.8',
                                    'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
                                    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Referer: %s' % (url)])
            f = open('%s-%sx%s.srt' % (show, season, chapter), 'wb')
            c.setopt(c.WRITEDATA, f)
            c.perform()
            print("Listo :)")
        except:
            print("Error del todo")


def folderSearch(folder):
    print("Buscando mkv's en: " + folder)
    filename = ""
    remove = ""
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
                    print(match)
                    show = match.group('show')
                    release = mkvfile[mkvfile.rfind('-') + 1:]
                    if release.rfind('[') > -1:
                        release = release[0:release.rfind('[')]

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
                    downloadSubtitle(name, int(season), episode, release)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='TV Show', metavar="Title", default=None)
    parser.add_argument('-s', help='Season', metavar="Season", default=None)
    parser.add_argument('-c', help='Chapter', metavar="Chapter", default=None)
    parser.add_argument('-r', help='Release', metavar="Release", default=None)
    parser.add_argument('-f', help='Release', metavar="Release", default='.')
    args = parser.parse_args()

    isItFolderSearch = True
    if args.s is None and args.t is None and args.c is None:
        print("Busqueda en carpeta")
        isItFolderSearch = True
    else:
        argStatus = []
        for arg in vars(args):
            argStatus.append((arg, getattr(args, arg)))

        for arg, value in argStatus:
            if value is None and arg is not 'r':
                print ("ERROR: Faltan argumentos.")
                print("usage: testaaa.py [-t 'Title' -s Season -c Chapter] [-r Release]")
                sys.exit(-1)
        isItFolderSearch = False

    with open('dict.txt', 'r') as inf:
        showCodesDict = eval(inf.read())

    if isItFolderSearch:
        folderSearch(args.f)
    else:
        downloadSubtitle(args.t, args.s, args.c, args.r)
