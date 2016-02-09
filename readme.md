tusubtitulo.py
=======

Descarga subtítulos en Español e Inglés para tus series favoritas de www.tusubtitulo.com directamente desde la terminal.

Usage
=====
Folder search:
```bash
python tusubtitulo.py [-f folder] [-l langs...]
```


Episode search:
```bash
python tusubtitulo.py -t "Show title" -s Season -e Episode [-r "Release"] [-l langs...]
```

Notes:
- Show title **MUST** match the title used in www.tusubtitlo.com
- Quotation marks are **NOT** optional.
- Default folder is current working directory.
- Languages must be an ISO 3166 two-letter country code.

Dependencies
============
- [Lxml](http://www.lxml.de) (pip install lxml)
- [Requests](http://docs.python-requests.org/en/master) (pip install requests)
