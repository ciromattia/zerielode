#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

import sys
import argparse
from os.path import dirname, realpath
from rdflib import Graph, RDF, RDFS, XSD, Namespace
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
from fzeri_parser_schedaF import FZeriParserSchedaF

# define default source
DEFAULT_SOURCE = dirname(realpath(__file__)) + "/catalog/fzeri_F_2014_03_11_163504_test.xml"

CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


def parse_options():
    global options
    parser = argparse.ArgumentParser(description='FZeri to CIDOC-CRM catalog conversion script.')
    parser.add_argument('source_file', help='FZeri catalog file path', )
    parser.add_argument('-o', '--output', dest="output_file", default="fzeri.ttl",
                        help='Output file name')
    parser.add_argument('-f', '--format', dest="format", default="turtle",
                        help='Output format')
    options = parser.parse_args()


def main():
    global options
    parse_options()
    # create a new Graph
    rdf = Graph()
    rdf.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    rdf.bind("qudt", "http://qudt.org/vocab/unit#")
    rdf.bind("fzeriThes", "http://fe.fondazionezeri.unibo.it/thesauri/")

    my_prop = CRM.P102a_has_proper_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    # rdf.add((my_prop, RDFS.domain, CRM['E71_Man-Made_Thing']))
    # rdf.add((my_prop, RDFS.range, CRM.E35_Title))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))
    my_prop = CRM.P102b_has_parallel_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    # rdf.add((my_prop, RDFS.domain, CRM['E71_Man-Made_Thing']))
    # rdf.add((my_prop, RDFS.range, CRM.E35_Title))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))
    my_prop = CRM.P102c_has_attributed_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    # rdf.add((my_prop, RDFS.domain, CRM['E71_Man-Made_Thing']))
    # rdf.add((my_prop, RDFS.range, CRM.E35_Title))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))

    my_prop = CRM.P14a_carried_out_as_publisher_by
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14_carried_out_by))
    my_prop = CRM.P14ai_performed_as_publisher
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14i_performed))
    my_prop = CRM.P14b_carried_out_as_customer_by
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14_carried_out_by))
    my_prop = CRM.P14bi_performed_as_customer
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14i_performed))
    my_prop = CRM.P14c_carried_out_as_distributor_by
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14_carried_out_by))
    my_prop = CRM.P14ci_performed_as_distributor
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P14i_performed))

    my_prop = CRM.P3a_cultural_context
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.domain, CRM.E1_CRM_Entity))
    rdf.add((my_prop, RDFS.range, RDFS.Literal))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P3_has_note))

    my_prop = CRM.P82a_begin_of_the_begin
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.domain, CRM['E52_Time-Span']))
    rdf.add((my_prop, RDFS.range, XSD.dateTime))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P82_at_some_time_within))

    my_prop = CRM.P82b_end_of_the_end
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.domain, CRM['E52_Time-Span']))
    rdf.add((my_prop, RDFS.range, XSD.dateTime))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P82_at_some_time_within))

    # parse xml
    print "### SOURCING FILE " + options.source_file
    xml = etree.parse(options.source_file)
    for xmlentry in xml.findall("SCHEDA"):
        entry = FZeriParserSchedaF(xmlentry, rdf)
        entry.parse()
    rdf.serialize(dirname(realpath(__file__)) + "/" + options.output_file, format=options.format)

if __name__ == "__main__":
    main()
    sys.exit(0)

