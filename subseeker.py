#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from lxml import html
# import lxml
import argparse
import codecs
# import pycurl
# import urllib2
import re
import requests
import os
import sys
import time
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


langsToLook = []
debug = False


def getSuitableRelease(showInfo):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release

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
                if release in fetchedRls or \
                        release in release_equivalence_table[fetchedRls]:
                    if debug:
                        print("Found suitable encoder.")
                    return iterations
            except KeyError:
                # Encode not known
                pass
        iterations += 1
    print(
        "No se encontró ninguna versión que se corresponda con su archivo.\n \
         Descargaremos la versión " + releases[0])
    return 0


def writeSubtitleToFile(showInfo, lang, text, folderSearch):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release if showInfo.release is not None else "Default"

    if not folderSearch:
        filename = "{} - {}x{}-{}.{}.srt".format(
            show, str(season), str(episode), release, lang_codes[lang])
    else:
        filename = "{}.{}.srt".format(folderSearch, lang_codes[lang])

    with open(filename, 'wb') as subtitle:
        subtitle.write(text)
    print("Saved as: " + filename)


def downloadSubtitle(showInfo, folderSearch=False):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release
    release_code = getSuitableRelease(showInfo) if release is not None else 0

    url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
        show, season, episode, 0)

    for lang in langsToLook:
        if debug:
            print("Looking for language: " + lang_codes[lang])
        search = "http://www.tusubtitulo.com/updated/%s/(?P<code>[0-9]+)/0" % \
            (str(lang))
        search_alt = "http://www.tusubtitulo.com/original/(?P<code>[0-9]+)/0"

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11' +
            '  (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.' +
            '9,image/webp,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'es-ES,es;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.tusubtitulo.com'
        }

        page_content_req = requests.get(url, headers=headers)
        page_content = page_content_req.text

        try:
            code = re.search(search, page_content).group(1)
        except:
            try:
                code = re.search(search_alt, page_content).group(1)
            except:
                pass

        try:
            url = "http://www.tusubtitulo.com/updated/%s/%s/%s" % (
                lang, code, str(release_code))
            print("Found! Downloading...")

            if debug:
                debugPrint(url)

            r = requests.get(url, headers={'referer':
                                           'http://www.tusubtitulo.com'})
            writeSubtitleToFile(showInfo, lang, r.content, folderSearch)
        except Exception as e:
            print("Error fatal: " + str(e))


def folderSearch(folder):
    print("Buscando mkv's en: " + folder)
    filename = ""
    remove = ""
    fileset = set()
    already_downloaded = set()
    languages = ["en", "es"]

    for file in os.listdir(folder):
        if file.endswith(".mkv"):
            filename = str(file)
            remove = os.path.splitext(os.path.basename((folder + filename)))[1]
            fileset.add(filename[:-len(remove)])
        if file.endswith(".srt"):
            filename = str(file)
            remove = os.path.splitext(os.path.basename((folder + filename)))[1]
            filename = filename[:-len(remove)]

            for item in languages:
                if filename.endswith('.' + item):
                    remove = 3
                    filename = filename[:-remove]
                    already_downloaded.add(filename)

    for mkvfile in fileset:
        if mkvfile not in already_downloaded:
            for rx in episode_regexps[0:-1]:
                match = re.search(rx, mkvfile, re.IGNORECASE)
                if match:
                    show = match.group('show')
                    release = mkvfile[mkvfile.rfind('-') + 1:]
                    if release.rfind('[') > -1:
                        release = release[0:release.rfind('[')]

                    # Se convierte a int para quitar los 0 de delante.
                    # El formato de tusubtitulo.com es 'Show 1x01'
                    season = match.group('season')
                    episode = match.group('ep')
                    # Clean title.
                    name, year = Parser.cleanName(show)
                    if year is not None:
                        name = "%s %s" % (name, year)
                    showInfo = ShowInfo.ShowInfo(name, int(season),
                                                 episode, release)
                    downloadSubtitle(showInfo, mkvfile)


def selectLanguages(langs):
    if not isinstance(langs, list):
        langsToLook.append(lang_codes_rev[langs])
    else:
        for language in langs:
            langsToLook.append(lang_codes_rev[language])


def debugPrint(string):
    msg = "{} DEBUG -> {}".format(str(time.strftime("%H:%M:%S")), string)
    print(msg)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='TV Show', metavar="Title", default=None)
    parser.add_argument('-s', help='Season', metavar="Season", default=None)
    parser.add_argument('-e', help='Episode', metavar="Episode", default=None)
    parser.add_argument('-r', help='Release', metavar="Release", default=None)
    parser.add_argument('-f', help='Folder', metavar="Folder", default='.')
    parser.add_argument('-l', help='Language', nargs='+', metavar="Lang",
                        default=["es"])
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable Debug mode')
    args = parser.parse_args()

    if args.debug:
        debug = True

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
                print ("ERROR: Missing arguments.")
                print("Usage: python " + sys.argv[0] +
                      " [-t 'Title' -s Season -e Episode] [-r Release]" +
                      " [-l Langs...]")
                sys.exit(-1)
        isItFolderSearch = False

    selectLanguages(args.l)

    if isItFolderSearch:
        folderSearch(args.f)
    else:
        episode = args.e
        if len(args.e) == 1:
            episode = '0' + episode
        showInfo = ShowInfo.ShowInfo(args.t, args.s, episode, args.r)
        downloadSubtitle(showInfo)
