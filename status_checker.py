# coding=utf-8

from bs4 import BeautifulSoup
import requests
import sys

version = []


def getStatus(release, showInfo, html):

    url = "http://tusubtitulo.com/serie/%s/%s/%s/0" % (showInfo.title,
                                                       showInfo.season,
                                                       showInfo.episode)
    try:
        if html is None:
            pageHtml = requests.get(url)
            if pageHtml.status_code > 300:
                print("TV Series not found," +
                      " have you misspelled it?")
                sys.exit(-1)
            html = pageHtml.text
        soup = BeautifulSoup(html, 'lxml')
    except UnboundLocalError:
        print("Exception thrown")
        sys.exit(-1)

    iterations = 0
    for versiones in soup.find_all('div', id="version"):
        version.append(iterations)
        for listas in versiones.find_all('ul', class_="sslist"):
            wowo = []
            for lis in listas.contents:
                item = None
                try:
                    item = lis.contents[1]
                    item = item.text
                except:
                    wut = lis.string
                    if u"\n" != wut:
                        item = wut.replace(u"\t", "")
                        item = item.replace(u"\n", "")
                if item is not None:
                    wowo.append(item)
            version.append(wowo)
        if iterations == release:
            return version
        iterations += 1
