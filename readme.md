TuSubseeker
=======
[![Codacy Badge](https://api.codacy.com/project/badge/grade/5df1f966326e465abb2a2fc7f6cf9bb7)](https://www.codacy.com/app/jbl4/TuSubseeker)
Descarga subtítulos en Español e Inglés para tus series favoritas de www.tusubtitulo.com directamente desde la terminal.

Usage
=====
Rename aliases.json.sample to aliases.json and define your aliases. Alias specification on next section.


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
- Language is one (or more if want to download more than one) of these:
    "en", "es" or "es-la". Each one corresponding with "English", "Spanish (Spain)" and "Spanish (Latin America)"

Aliases
=======
Now supports aliases. If a shows title is too long, or too complex to be written every single time, you can add it as a show in
**aliases.json** keeping as a JSON Object inside the shows array.


```bash
{
    "shows":[
        {
            "alias":"yourAlias",
            "title":"TheShowWithTheLongAndAnnoying.Ti.Tle"
        },
        .
        .
    ]
}
```

Dependencies
============
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) (pip install beautifulsoup4)
- [Lxml](http://www.lxml.de) (pip install lxml)
- [Requests](http://docs.python-requests.org/en/master) (pip install requests)
