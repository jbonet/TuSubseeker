#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from libs import Parser
from libs import ShowInfo
from libs import Printer
from lxml import html
import argparse
import codecs
import os
import re
import requests
import sys
import time


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


def getSuitableRelease(showInfo):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release

    try:
        url = "http://www.tusubtitulo.com/serie/%s/%s/%s/0" % (
            show.lower(), season, str(int(episode)))
        pageHtml = requests.get(url)
        if pageHtml.status_code > 300:
            printer.errorPrint("TV Series not found, have you misspelled it?")
            sys.exit(-1)
        tree = html.fromstring(pageHtml.text)
    except:
        pass
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
                        printer.infoPrint("Found suitable encoder.")
                    return iterations
            except KeyError:
                # Encode not known
                pass
        iterations += 1
    printer.infoPrint(
        "No se encontró ninguna versión que se corresponda con su archivo.\n \
         Descargaremos la versión " + releases[0])
    return 0


def writeSubtitleToFile(showInfo, lang, text, folderSearch):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release if showInfo.release is not None else "Default"

    if not folderSearch:
        release = "" if release in "Default" else "-" + release
        filename = "{} - {}x{}{}.{}.srt".format(
            show, str(season), str(episode), release, lang_codes[lang])
    else:
        filename = "{}.{}.srt".format(folderSearch, lang_codes[lang])

    with open(filename, 'wb') as subtitle:
        subtitle.write(text)
    printer.infoPrint("Subtitle saved as file: " + filename)


def getEpisodeCode(showInfo):
    """Extracts the unique code from the page's HTML"""

    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    search = "http://www.tusubtitulo.com/original/(?P<code>[0-9]+)/0"
    url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
        show, season, episode, 0)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.1' +
        '1  (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.' +
        '9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'es-ES,es;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'www.tusubtitulo.com'
    }

    page_content_req = requests.get(url, headers=headers)
    if page_content_req.status_code > 300:
        printer.errorPrint("TV Series not found, have you misspelled it?")
        sys.exit(-1)
    page_content = page_content_req.text

    try:
        code = re.search(search, page_content).group(1)
    except:
        printer.errorPrint("Subtitle code not found")

    if code is None:
        sys.exit(-1)
    printer.debugPrint("Codigo: " + code)
    return code


def downloadSubtitle(showInfo, folderSearch=False):
    show = showInfo.title
    season = showInfo.season
    episode = showInfo.episode
    release = showInfo.release
    release_code = getSuitableRelease(showInfo) if release is not None else 0

    code = getEpisodeCode(showInfo)

    for lang in langsToLook:
        printer.debugPrint("Looking for language: " + lang_codes[lang])
        try:
            url = "http://www.tusubtitulo.com/updated/%s/%s/%s" % (
                lang, code, str(release_code))

            printer.debugPrint("URL: " + url)
            printer.infoPrint("Subtitle for language: {} found! Downloading..."
                              .format(lang_codes[lang]))

            r = requests.get(url, headers={'referer':
                                           'http://www.tusubtitulo.com'})
            printer.debugPrint("Request code: {}".format(str(r.status_code)))
            if r.status_code > 300:
                printer.errorPrint("Request returned code: {}. Bad url?"
                                   .format(r.status_code))
            else:
                writeSubtitleToFile(showInfo, lang, r.content, folderSearch)
        except Exception as e:
            printer.errorPrint("Error fatal: " + str(e))


def folderSearch(folder):
    printer.warningPrint("Feature not finished. May be (it sure is) buggy.")
    printer.infoPrint("Buscando mkv's en: " + folder)
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

    if len(fileset) == 0:
        printer.infoPrint("No files left to process or the " +
                          "folder does not contain any mkv")

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--title', metavar="Title",
                        default=None)
    parser.add_argument('-s', '--season', metavar="Season",
                        default=None)
    parser.add_argument('-e', '--episode', metavar="Episode",
                        default=None)
    parser.add_argument('-r', '--release', help='Encoder of the release',
                        metavar="Release", default=None)
    parser.add_argument('-f', '--folder', help='Folder that contains ' +
                        'the mkv files', metavar="Folder", default='.')
    parser.add_argument('-l', '--languages', help='Languages in which the ' +
                        'subtitles are going to be downloaded', nargs='+',
                        metavar="Lang", default=["es"])
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enables Debug mode (Verbose)', default=False)
    args = parser.parse_args()

    printer = Printer.Printer(args.debug)

    if len(sys.argv) > 1 and args.folder is ".":
        printer.debugPrint("Normal mode detected")
        printer.debugPrint("Checking all required arguments are present")
        isItFolderSearch = False
        argStatus = []
        for arg in vars(args):
            if getattr(args, arg) is None and arg is not 'release':
                parser.error("Argument '--{}' is required for normal search"
                             .format(arg))
                sys.exit(-1)
    else:
        printer.debugPrint("Folder Search mode detected")
        isItFolderSearch = True

    selectLanguages(args.languages)

    if isItFolderSearch:
        folderSearch(args.folder)
    else:
        episode = args.episode
        if len(args.episode) == 1:
            episode = '0' + episode
        showInfo = ShowInfo.ShowInfo(args.title, args.season,
                                     episode, args.release)
        downloadSubtitle(showInfo)
