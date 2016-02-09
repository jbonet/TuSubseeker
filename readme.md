Subseeker.py
=======

Descarga subtítulos en Español e Inglés para tus series favoritas de www.tusubtitulo.com directamente desde la terminal.

Uso
=====
Folder search:
```bash
python subseeker [-f folder] [-l langs...]
```


Episode search:
```bash
python tusubtitulo.py -t "Show title" -s Season -e Episode [-r "Release"] [-l langs...]
```

Notes:
- Quotation marks are **NOT** optional.
- Default folder is current working directory.
- Languages must be an ISO 3166 two-letter country code.

Dependencies
============
- Lxml (pip install lxml)
- Requests (pip install requests)
