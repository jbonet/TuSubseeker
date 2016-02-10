# coding=utf-8

from libs import Printer
from libs import ShowInfo
from lxml import html
import re
import requests
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


class Downloader:

    def __init__(self, languages, printer):
        self.languages = languages
        self.printer = printer

    def getEpisodeCode(self, showInfo):
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
            self.printer.errorPrint("TV Series not found, " +
                                    "have you misspelled it?")
            sys.exit(-1)
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
            tree = html.fromstring(pageHtml.text)
        except:
            self.printer.errorPrint("Exception thrown on getSuitableRelease()")
        iterations = 0
        for version in tree.xpath('//div[@id="version"]/div/blockquote/p/text()'):
            ve = version.lstrip().encode("utf-8")
            if ve:
                fetchedRls = ve.split(' ')[1]
                try:
                    if release in fetchedRls or \
                            release in release_equivalence_table[fetchedRls]:
                        self.printer.infoPrint("Found suitable encoder.")
                        return iterations
                except KeyError:
                    # Encode not known
                    pass
                iterations += 1
        self.printer.infoPrint("No release matches yours, " +
                               "default will be downloaded.")
        return 0

    def download(self, showInfo, folderSearch=False):
        """Downloads the specified subtitle"""

        show = showInfo.title
        season = showInfo.season
        episode = showInfo.episode
        release = showInfo.release
        if release is not None:
            release_code = self.getSuitableRelease(showInfo)
        else:
            release_code = 0

        code = self.getEpisodeCode(showInfo)

        for lang in self.languages:
            self.printer.debugPrint("Looking for language: " + lang_codes[lang])
            try:
                url = "http://www.tusubtitulo.com/updated/%s/%s/%s" % (
                    lang, code, str(release_code))

                self.printer.debugPrint("URL: " + url)
                self.printer.infoPrint("Subtitle for language: {} found! Downloading..."
                                       .format(lang_codes[lang]))

                r = requests.get(url, headers={'referer':
                                               'http://www.tusubtitulo.com'})
                self.printer.debugPrint("Request code: {}"
                                        .format(str(r.status_code)))
                if r.status_code > 300:
                    self.printer.errorPrint("Request returned code: {}. " +
                                            "Bad url?".format(r.status_code))
                else:
                    self.writeToSrt(showInfo, lang, r.content, folderSearch)
            except Exception as e:
                self.printer.errorPrint("Error fatal: " + str(e))

    def writeToSrt(self, showInfo, lang, text, folderSearch):
        """Writes the text to a SRT file"""

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

        with open(filename, 'wb') as subtitle:
            subtitle.write(text)
        self.printer.infoPrint("Subtitle saved as file: " + filename)
