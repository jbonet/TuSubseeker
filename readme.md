Subseeker.py
=======

Descarga subtítulos en Español e Inglés para tus series favoritas de www.tusubtitulo.com directamente desde la terminal.

Uso
=====
Folder search:
```bash
python subseeker [-f folder]
```
Default folder is current working directory.

Not folder search:
```bash
python subseeker.py -t "Título de la serie" -s Season -e Episode [-r "Release"] [-l langs...]
```
It is possible to pass more than 1 language, as a list of ISO 3166 two-letter codes.

Nota: las comillas **NO** son opcionales.

Dependencies
============
Lxml (pip install lxml)
Requests (pip install requests)
