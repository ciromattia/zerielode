#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

import sys
import os
import argparse
from os.path import dirname, realpath
import logging
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
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
        # empty already existing directory or create a new one
        if os.path.isdir(output_dir):
            for the_file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception, e:
                    print e
        else:
            os.path.mkdir(output_dir)
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
    rdf.bind("pro", "http://purl.org/spar/pro/")
    rdf.bind("dc", "http://purl.org/dc/elements/1.1/")
    rdf.bind("dcterms", "http://purl.org/dc/terms/")
    rdf.bind("foaf", "http://xmlns.com/foaf/0.1/")
    rdf.bind("time", "http://www.w3.org/2006/time#")
    rdf.bind("frbr", "http://purl.org/vocab/frbr/core#")
    rdf.bind("fabio", "http://purl.org/spar/fabio/")
    rdf.bind("fentry", "http://www.essepuntato.it/2014/03/fentry/")
    rdf.bind("prov", "http://www.w3.org/ns/prov#")
    rdf.bind("datacite", "http://purl.org/spar/datacite")
    rdf.bind("fzentryf", "http://fe.fondazionezeri.unibo.it/catalogo/schedaF/")
    rdf.bind("fzentryoa", "http://fe.fondazionezeri.unibo.it/catalogo/schedaOA/")
    rdf.bind("fznegative", "http://fe.fondazionezeri.unibo.it/catalogo/negative/")
    rdf.bind("fzcollection", "http://fe.fondazionezeri.unibo.it/collection/")
    rdf.bind("fzdimension", "http://fe.fondazionezeri.unibo.it/thesauri/dimension/")
    rdf.bind("fzserie", "http://fe.fondazionezeri.unibo.it/thesauri/serie/")
    rdf.bind("fzbox", "http://fe.fondazionezeri.unibo.it/thesauri/box/")
    rdf.bind("fzmaterial", "http://fe.fondazionezeri.unibo.it/thesauri/material/")
    rdf.bind("fzentrytype", "http://fe.fondazionezeri.unibo.it/thesauri/entry_type/")
    rdf.bind("fzidentifier", "http://fe.fondazionezeri.unibo.it/thesauri/identifier/")
    rdf.bind("fzphotoformat", "http://fe.fondazionezeri.unibo.it/thesauri/photo_format/")
    rdf.bind("fzphotocolor", "http://fe.fondazionezeri.unibo.it/thesauri/photo_color/")
    rdf.bind("fzphototype", "http://fe.fondazionezeri.unibo.it/thesauri/photo_type/")
    rdf.bind("fzconditiontype", "http://fe.fondazionezeri.unibo.it/thesauri/condition_type/")
    return rdf

if __name__ == "__main__":
    main()
    sys.exit(0)

