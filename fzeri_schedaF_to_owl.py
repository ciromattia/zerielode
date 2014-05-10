#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

import sys
import argparse
from os.path import dirname, realpath
from os import mkdir
import logging
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
    parser.add_argument('source_file', nargs='+', help='FZeri catalog file(s) path')
    parser.add_argument('--single-entry', action="store_true",
                        help='Outputs entries in a single file for each one.')
    parser.add_argument('-o', '--output', dest="output_file", default="fzeri.ttl",
                        help='Output file or directory name')
    parser.add_argument('-f', '--format', dest="format", default="turtle",
                        help='Output format (xml|n3|turtle|nt|pretty-xml|trix)')
    options = parser.parse_args()


def format_to_ext(fmt):
    return {'xml': '.xml',
            'n3': '.n3',
            'turtle': '.ttl',
            'nt': '.nt',
            'pretty-xml': '.xml',
            'trix': '.xml'
            }[fmt]


def main():
    global options
    parse_options()
    logging.basicConfig()
    if options.single_entry:
        output_dir = dirname(realpath(__file__)) + "/" + options.output_file
        ext = format_to_ext(options.format)
        mkdir(output_dir)
        # parse xml
        for source_file in options.source_file:
            print "### SOURCING FILE " + source_file
            xml = etree.parse(source_file)
            for xmlentry in xml.findall("SCHEDA"):
                # create a new Graph
                rdf = init_graph()
                entry = FZeriParserSchedaF(xmlentry, rdf)
                entry.parse()
                rdf.serialize(output_dir + "/" + entry.entry_id + ext, format=options.format)
    else:
        # create a new Graph
        rdf = init_graph()
        # parse xml
        for source_file in options.source_file:
            print "### SOURCING FILE " + source_file
            xml = etree.parse(source_file)
            for xmlentry in xml.findall("SCHEDA"):
                entry = FZeriParserSchedaF(xmlentry, rdf)
                entry.parse()
        rdf.serialize(dirname(realpath(__file__)) + "/" + options.output_file, format=options.format)


def init_graph():
    rdf = Graph()
    rdf.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
    rdf.bind("qudt", "http://qudt.org/vocab/unit#")
    rdf.bind("pro", "http://purl.org/spar/pro")
    rdf.bind("time", "http://www.w3.org/2006/time")
    rdf.bind("fzeriThes", "http://fe.fondazionezeri.unibo.it/thesauri/")

    # Specialize property CRM.P102_has_title with proper/parallel/attributed flavours
    my_prop = CRM.P102a_has_proper_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))
    my_prop = CRM.P102b_has_parallel_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))
    my_prop = CRM.P102c_has_attributed_title
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P102_has_title))

    my_prop = CRM.P3a_cultural_context
    rdf.add((my_prop, RDF.type, RDF.Property))
    rdf.add((my_prop, RDFS.domain, CRM.E1_CRM_Entity))
    rdf.add((my_prop, RDFS.range, RDFS.Literal))
    rdf.add((my_prop, RDFS.subPropertyOf, CRM.P3_has_note))
    return rdf

if __name__ == "__main__":
    main()
    sys.exit(0)

