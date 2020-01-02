# xml-c14n

Модуль предназначен для приведения XML-документов к унифицированному (каноническому) виду, определенному в спецификации ["Canonical XML Version 1.0"](https://www.w3.org/TR/2001/REC-xml-c14n-20010315).

## Установка
```bash
$ pip install https://github.com/WoolenSweater/xml-c14n.git
```

## Зависимости
* [lmxl](https://github.com/lxml/lxml)

## Использование
```python
from lxml.etree import fromstring
from c14n import canonicalize

xml = fromstring('''
    <a:foo xmlns:a="http://a" xmlns:b="http://b" xmlns:c="http://c">
        <b:bar/>
        <b:bar/>
        <a:bar b:att1="val"/>
    </a:foo>''')
xml_c14n = canonicalize(xml)
```