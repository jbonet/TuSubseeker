TuSubseeker
=======

Descarga subtítulos en Español e Inglés para tus series favoritas de www.tusubtitulo.com directamente desde la terminal.

Usage
=====
Folder search:
```bash
python tusubseeker.py [-f folder] [-l langs...]
```


Episode search:
```bash
python tusubseeker.py -t "Show title" -s Season -e Episode [-r "Release"] [-l langs...]
```

Notes:
- Show title **MUST** match the title used in www.tusubtitulo.com
- Quotation marks are **NOT** optional.
- Default folder is "downloads" inside current working directory.
- Languages must be an ISO 3166 two-letter country code.

Aliases
=======
Now supports aliases. If a shows title is too long, or anything, you can add it
to **equivalences.cfg** keeping this structure:

- 1 show per line
- alias**¬**Real show title

Only works with this formatting for now.

So, if you want to search subtitles for "Marvel's Agents of S.H.I.E.L.D." before
you had to write this exactly, now you can add a line to the equivalences file like this:

```bash
shield¬Marvel's Agents of S.H.I.E.L.D.
```

And now writting just "shield" would do the trick

Dependencies
============
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) (pip install beautifulsoup4)
- [Lxml](http://www.lxml.de) (pip install lxml)
- [Requests](http://docs.python-requests.org/en/master) (pip install requests)
