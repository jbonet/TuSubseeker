# coding=utf-8

from libs import Printer
from libs import ShowInfo
from lxml import html
import json
import os
import re
import requests
import status_checker
import sys

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

lang_to_unicode = {
    '1': u'English',
    '5': u'Español (España)',
    '6': u'Español (Latinoamérica)'
}


class Downloader:

    def __init__(self, languages, printer):
        self.languages = languages
        self.printer = printer
        self.page_html = None
        self.alias = None

    def getAliasFromFile(self, alias):
        """Gets show real title from alias if specified"""

        with open("aliases.json") as alias_file:
            aliases = json.load(alias_file)

        for show in aliases["shows"]:
            if alias == show["alias"]:
                return show["title"]
        return None

    def doRequest(self, showInfo, checkMode=False):
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

        season = showInfo.season if not checkMode else str(1)
        episode = showInfo.episode if not checkMode else str(1)

        url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
            showInfo.title, season, episode, 0)
        return requests.get(url, headers=headers)

    def checkIfExists(self, showInfo):
        """Checks if the show exists on the website by requesting the first
        episode"""

        page_content_req = self.doRequest(showInfo, checkMode=True)
        return False if page_content_req.status_code > 300 else True

    def tryWithAliases(self, showInfo):
        """If supplied title not found on the website, does the
        request again, but using the alias"""

        self.printer.infoPrint("Title not found, checking " +
                               "aliases for a match")
        showInfo.title = self.getAliasFromFile(showInfo.title)
        if showInfo.title is None:
            self.printer.infoPrint("Match not found. Unknown show.")
            sys.exit(-1)
        else:
            self.alias = showInfo.title
        page_content_req = self.doRequest(showInfo)
        if page_content_req.status_code > 300:
            if not self.checkIfExists(showInfo):
                self.printer.errorPrint("TV Series not found, " +
                                        "have you misspelled it?")
            else:
                self.printer.errorPrint("TV Series found, but " +
                                        "episode or season not aired yet")
            sys.exit(-1)
        self.printer.infoPrint("Match found, new title: " + showInfo.title)
        return page_content_req

    def getEpisodeCode(self, showInfo):
        """Extracts the show's unique code from the HTML"""

        show = showInfo.title
        season = showInfo.season
        episode = showInfo.episode
        search = "http://www.tusubtitulo.com/original/(?P<code>[0-9]+)/0"
        url = 'http://www.tusubtitulo.com/serie/%s/%s/%s/%s' % (
            show, season, episode, 0)

        page_content_req = self.doRequest(showInfo)

        if page_content_req.status_code > 300:
            page_content_req = self.tryWithAliases(showInfo)
        page_content = page_content_req.text

        try:
            code = re.search(search, page_content).group(1)
        except:
            self.printer.errorPrint("Subtitle code not found")
            sys.exit(-1)

        self.printer.debugPrint("Codigo: " + code)
        return code

    def getSuitableRelease(self, showInfo):
        """Gets the index of the release if specified, else returns 0."""

        show = showInfo.title
        season = showInfo.season
        episode = showInfo.episode
        release = showInfo.release

        try:
            url = "http://www.tusubtitulo.com/serie/%s/%s/%s/0" % (
                show.lower(), season, str(int(episode)))
            pageHtml = requests.get(url)
            if pageHtml.status_code > 300:
                self.printer.errorPrint("TV Series not found," +
                                        " have you misspelled it?")
                sys.exit(-1)
            self.page_html = pageHtml.text
            tree = html.fromstring(pageHtml.text)
        except:
            self.printer.errorPrint("Exception thrown on getSuitableRelease()")
        iterations = 0
        for version in tree.xpath('// div[@id="version"]' +
                                  '/div / blockquote / p / text()'):
            ve = version.lstrip().encode("utf-8")
            if ve:
                fetchedRls = ve.split(' ')[1]
                try:
                    if release in fetchedRls or \
                            release in release_equivalence_table[fetchedRls]:
                        self.printer.infoPrint("Found suitable encoder.")
                        return iterations
                except KeyError:
                    pass  # Encode not known
                iterations += 1
        self.printer.infoPrint("No release matches yours, " +
                               "default will be downloaded.")
        return 0

    def checkIfAvailable(self, lang, info):
        """Checks for the status of the translation, returns"""

        status = []
        for translation in info:
            if not isinstance(translation, int):
                if translation[0] == lang_to_unicode[lang]:
                    if u"%" in translation[1]:
                        status.append(False)
                        status.append(translation[1][:translation[1]
                                                     .index(u"%")])
        if not status:
            status.append(True)
        return status

    def download(self, showInfo, folderSearch=False):
        """Downloads the specified subtitle"""

        show = showInfo.title
        season = showInfo.season
        episode = showInfo.episode
        release = showInfo.release
        code = self.getEpisodeCode(showInfo)

        if self.alias is not None:
            show = self.alias
            showInfo.show = show

        if release is not None:
            release_code = self.getSuitableRelease(showInfo)
        else:
            release_code = 0

        info = status_checker.getStatus(release_code, showInfo, self.page_html)

        subtitles = []

        for lang in self.languages:
            self.printer.debugPrint("Looking for language: " +
                                    lang_codes[lang])

            status = self.checkIfAvailable(lang, info)
            if not status[0]:
                not_completed_yet = "Subtitle is not ready yet. " + \
                    str(status[1]) + "% translated."
                self.printer.infoPrint(not_completed_yet)
                sys.exit(-1)

            try:
                url = "http://www.tusubtitulo.com/updated/%s/%s/%s" % (
                    lang, code, str(release_code))

                self.printer.debugPrint("URL: " + url)
                self.printer.infoPrint("Subtitle for language: {} " +
                                       "found! Downloading..."
                                       .format(lang_codes[lang]))

                r = requests.get(url, headers={'referer':
                                               'http://www.tusubtitulo.com'})
                self.printer.debugPrint("Request code: {}"
                                        .format(str(r.status_code)))
                if r.status_code > 300:
                    self.printer.errorPrint("Request returned code: {}. " +
                                            "Bad url?".format(r.status_code))
                else:
                    subtitles.append((showInfo, lang, r.content, folderSearch))
            except Exception as e:
                self.printer.errorPrint("Error fatal: " + str(e))

        return subtitles

    def writeToSrt(self, subtitle):
        """Writes the text to an SRT file"""
        showInfo = subtitle[0]
        lang = subtitle[1]
        text = subtitle[2]
        folderSearch = subtitle[3]
        show = showInfo.title
        season = showInfo.season
        episode = showInfo.episode
        release = showInfo.release if showInfo.release is not None \
            else "Default"

        if not folderSearch:
            release = "" if release in "Default" else "-" + release
            filename = "{} - {}x{}{}.{}.srt".format(
                show, str(season), str(episode), release, lang_codes[lang])
        else:
            filename = "{}.{}.srt".format(folderSearch, lang_codes[lang])

        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        with open("downloads/" + filename, 'wb') as subtitle:
            subtitle.write(text)
        self.printer.infoPrint("Subtitle saved as file: " + filename)
