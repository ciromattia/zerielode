#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

from rdflib import Literal, Namespace

QUDT = Namespace("http://qudt.org/vocab/unit#")

unit_fzeri_to_qudt = {
    'mm':   'Millimeters',
}


def fzeri_to_qudt(unit):
    if unit in unit_fzeri_to_qudt:
        return QUDT[unit_fzeri_to_qudt[unit]]
