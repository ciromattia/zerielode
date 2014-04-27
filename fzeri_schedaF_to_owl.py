#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

import sys
from os.path import dirname, realpath
from rdflib import Graph, RDF, RDFS, XSD, Namespace
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
from fzeri_parser_schedaF import FZeriParserSchedaF

# define default source
DEFAULT_SOURCE = dirname(realpath(__file__)) + "/fzeri_F_2014_03_11_163504_test.xml"

CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


def main(argv=None):
    if argv:
        source_file = argv[0]
    else:
        source_file = DEFAULT_SOURCE
    # create a new Graph
    rdf = Graph()
    rdf.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    rdf.bind("qudt", "http://qudt.org/vocab/unit#")
    rdf.bind("fzeriThes", "http://fe.fondazionezeri.unibo.it/thesauri/")

    title_type = CRM.P102_1_title_type
    rdf.add((title_type, RDF.type, RDF.Property))
    rdf.add((title_type, RDFS.domain, CRM['E71_Man-Made_Thing']))
    rdf.add((title_type, RDFS.range, CRM.E35_Title))
    rdf.add((title_type, RDFS.subPropertyOf, CRM.P102_has_title))

    title_type = CRM.P3_1_cultural_context
    rdf.add((title_type, RDF.type, RDF.Property))
    rdf.add((title_type, RDFS.domain, CRM.E1_CRM_Entity))
    rdf.add((title_type, RDFS.range, RDFS.Literal))
    rdf.add((title_type, RDFS.subPropertyOf, CRM.P3_has_note))

    title_type = CRM.P82a_begin_of_the_begin
    rdf.add((title_type, RDF.type, RDF.Property))
    rdf.add((title_type, RDFS.domain, CRM['E52_Time-Span']))
    rdf.add((title_type, RDFS.range, XSD.dateTime))
    rdf.add((title_type, RDFS.subPropertyOf, CRM.P82_at_some_time_within))

    title_type = CRM.P82b_end_of_the_end
    rdf.add((title_type, RDF.type, RDF.Property))
    rdf.add((title_type, RDFS.domain, CRM['E52_Time-Span']))
    rdf.add((title_type, RDFS.range, XSD.dateTime))
    rdf.add((title_type, RDFS.subPropertyOf, CRM.P82_at_some_time_within))

    # parse xml
    print "### SOURCING FILE " + source_file
    xml = etree.parse(source_file)
    for xmlentry in xml.findall("SCHEDA"):
        entry = FZeriParserSchedaF(xmlentry, rdf)
        entry.parse()
    rdf.serialize(dirname(realpath(__file__)) + "/fzeri.ttl", format="turtle")

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)
