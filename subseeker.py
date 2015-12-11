#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from lxml import html
import lxml
import argparse
import codecs
# import pycurl
# import urllib2
import re
import requests
import os
import sys
from libs import Parser
from libs import ShowInfo

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

release_equivalence_table = {
    'LOL': 'DIMENSION',
    'SYS': 'DIMENSION',
    'XII': 'IMMERSE',
    'PROPER': 'LOL,DIMENSION',
    'DIMENSION': 'LOL'
}

lang_codes = {
    '1': 'en',
    '5': 'es',
    '6': 'es-la'
}

lang_codes_rev = {
    'en': '1',
    'es': '5',
    'es-la': '6'
}

showCodesDict = {}

langsToLook = []


def getSuitableRelease(showInfo):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release
    if release is not None:
        try:
            url = "http://www.tusubtitulo.com/serie/%s/%s/%s/0" % (
                show.lower(), season, str(int(episode)))
            pageHtml = requests.get(url)
            tree = html.fromstring(pageHtml.text)
        except:
            print("No existe la serie.")
        iterations = 0
        releases = []
        for version in tree.xpath('//div[@id="version"]/div/blockquote/p/text()'):
            ve = version.lstrip().encode("utf-8")
            if ve:
                fetchedRls = ve.split(' ')[1]
                releases.append(fetchedRls)
                try:
                    if release == fetchedRls:
                        print("OK")
                    elif release in release_equivalence_table[fetchedRls]:
                        print("OK")
                    return iterations
                except KeyError:
                    # Encode not known
                    pass
            iterations += 1
        print("No se encontró ninguna versión que se corresponda con su archivo.\n\
              Descargaremos la versión " + releases[0])
        return 0


def writeSubtitleToFile(showInfo, lang, text):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release
    with open(show + str(season) + 'x' + str(episode) + "." + lang_codes[lang] + '.srt', 'wb') as subtitle:
        subtitle.write(text)


def downloadSubtitle(showInfo):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release
    release_code = getSuitableRelease(showInfo) if release is not None else 0

    if len(episode) == 1:
        episode = '0' + episode
    url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
        show, season, episode, 0)

    # print(langsToLook)

    for lang in langsToLook:
        print("looking for language: " + lang_codes[lang])
        search = "http://www.tusubtitulo.com/updated/%s/(?P<code>[0-9]+)/0" % (str(lang))
        search_alt = "http://www.tusubtitulo.com/original/(?P<code>[0-9]+)/0"

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'es-ES,es;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.tusubtitulo.com'
        }

        # urllib2.Request(url, headers=headers)
        page_content_req = requests.get(url, headers=headers)
        page_content = page_content_req.text
        orig_or_updated = 0

        try:
            code = re.search(search, page_content).group(1)
            orig_or_updated = "updated"
        except:
            try:
                code = re.search(search_alt, page_content).group(1)
                orig_or_updated = "original"
            except:
                print("Language not found.")

        try:
            print("Language: " + str(lang))
            print("Sub code: " + code)
            url = None
            if orig_or_updated == "updated":
                url = "http://www.tusubtitulo.com/updated/%s/%s/%s" % (
                    lang, code, str(release_code))
            elif orig_or_updated == "original":
                print("Probando a descargar el original...")
                url = "http://www.tusubtitulo.com/original/%s/%s" % (code, release_code)
            r = requests.get(url, headers={'referer': 'http://www.tusubtitulo.com'})
            # print(r.status_code)
            writeSubtitleToFile(showInfo, lang, r.content)
            print("Listo :)")
        except Exception as e:
            print("Error fatal: " + str(e))


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
                    show = match.group('show')
                    release = mkvfile[mkvfile.rfind('-') + 1:]
                    if release.rfind('[') > -1:
                        release = release[0:release.rfind('[')]

                    # Se convierte a int para quitar los 0 de delante. El formato de
                    # tusubtitulo.com es 'Show 1x01'
                    season = match.group('season')
                    episode = match.group('ep')
                    # Clean title.
                    name, year = Parser.cleanName(show)
                    if year is not None:
                        name = "%s %s" % (name, year)
                    # print "Descargaremos subtitulos de: %s Temporada: %s, Capítulo: %s" %
                    # (name, season, episode)
                    # searchString = "%s %sx%s" % (name, int(season), episode)
                    # print searchString
                    showInfo = ShowInfo.ShowInfo(name, int(season), episode, release)
                    for lang in langsToLook:
                        downloadSubtitle(showInfo, lang)


def selectLanguages(langs):
    if not isinstance(langs, list):
        langsToLook.append(lang_codes_rev[langs])
    else:
        for language in langs:
            langsToLook.append(lang_codes_rev[language])

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='TV Show', metavar="Title", default=None)
    parser.add_argument('-s', help='Season', metavar="Season", default=None)
    parser.add_argument('-e', help='Episode', metavar="Episode", default=None)
    parser.add_argument('-r', help='Release', metavar="Release", default=None)
    parser.add_argument('-f', help='Folder', metavar="Folder", default='.')
    parser.add_argument('-l', help='Language', metavar="Language", default=["en"])  # , "es"])
    args = parser.parse_args()

    isItFolderSearch = True
    if args.s is None and args.t is None and args.e is None:
        print("Busqueda en carpeta")
        isItFolderSearch = True
    else:
        argStatus = []
        for arg in vars(args):
            argStatus.append((arg, getattr(args, arg)))

        for arg, value in argStatus:
            if value is None and arg is not 'r':
                print ("ERROR: Faltan argumentos.")
                print("usage: testaaa.py [-t 'Title' -s Season -e Episode] [-r Release]")
                sys.exit(-1)
        isItFolderSearch = False

    selectLanguages(args.l)

    with open('dict.txt', 'r') as inf:
        showCodesDict = eval(inf.read())

    if isItFolderSearch:
        folderSearch(args.f)
    else:
        showInfo = ShowInfo.ShowInfo(args.t, args.s, args.e, args.r)
        downloadSubtitle(showInfo)
