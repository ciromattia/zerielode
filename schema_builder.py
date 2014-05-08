#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'


import sys
from os.path import dirname, realpath
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

# define default source
DEFAULT_SOURCES = {
    # dirname(realpath(__file__)) + "/catalog/fzeri_F_2014_03_11_163504_test.xml",
    dirname(realpath(__file__)) + "/catalog/fzeri_F_2014_03_11_163504.xml",
    dirname(realpath(__file__)) + "/catalog/fzeri_F_2014_03_11_164432.xml",
}
out = {}


def parse(xmlentry):
    # flatten XML to dict
    for child in xmlentry.findall("PARAGRAFO"):
        if not child.attrib["etichetta"] in out:
            out[child.attrib["etichetta"]] = {}
        if len(child):   # paragraph does contain at least one subelement
            if child[0].tag == "RIPETIZIONE":
                for rep in child:
                    for subchild in rep:
                        if not subchild.tag in out[child.attrib["etichetta"]]:
                            out[child.attrib["etichetta"]][subchild.tag] = {}
                        out[child.attrib["etichetta"]][subchild.tag] = subchild.text
            else:
                for subchild in child:
                    if not subchild.tag in out[child.attrib["etichetta"]]:
                        out[child.attrib["etichetta"]][subchild.tag] = {}
                    out[child.attrib["etichetta"]][subchild.tag] = subchild.text


def main():
    for the_file in DEFAULT_SOURCES:
        print "### SOURCING FILES " + the_file
        xml = etree.parse(the_file)
        for xmlentry in xml.findall("SCHEDA"):
            parse(xmlentry)
    out_file = open("catalog_schema.txt", "w")
    for x in out:
        out_file.write("\n" + x)
        for y in out[x]:
            out_file.write("\n\t" + y + ': ' + out[x][y].encode('utf-8'))
    out_file.close()

if __name__ == "__main__":
    main()
    sys.exit(0)