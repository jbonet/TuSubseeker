TuSubseeker
=======
[![Codacy Badge](https://api.codacy.com/project/badge/grade/5df1f966326e465abb2a2fc7f6cf9bb7)](https://www.codacy.com/app/jbl4/TuSubseeker)

Download www.tusubtitulo.com subtitles for your favorite shows from CLI.

Usage
=====
First of all rename aliases.json.sample and languages.json.sample to aliases.json and languages.json, then define your aliases. Alias specification on next section.


### Episode search:
```bash
python tusubseeker.py -t "Show title" -s Season -e Episode [-r "Release"] [-l langs...]
```

Folder search (WIP):
```bash
python tusubseeker.py [-f folder] [-l langs...]
```

### Notes:
- Show title **MUST** match the title used in www.tusubtitulo.com
- Default download folder is "downloads" inside current working directory.
- Define the default languages in the **languages.json** file for downloading those languages by default. If you want you want to download the subtitles in some specific language, use the argument "--language"
- Only accepted language values are:
    - "en" for "English"
    - "es" for "Spanish (Spain)"
    - "es-la" for "Spanish (Latin America)"

Aliases
=======
If a shows title is too long, or too complex to be written every single time, you can add it as a show in
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
Can be installed with pip: pip install -r requirements

- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) (pip install beautifulsoup4)
- [Lxml](http://www.lxml.de) (pip install lxml)
- [Requests](http://docs.python-requests.org/en/master) (pip install requests)
