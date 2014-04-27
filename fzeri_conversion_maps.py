#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

from rdflib import Namespace

QUDT = Namespace("http://qudt.org/vocab/unit#")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")

unit_fzeri_to_qudt = {
    'mm':   'Millimeter',
    'cm':   'Centimeter',
    'm':   'Meter',
}

production_roles = {
    'editore':      CRM.P14a_carried_out_as_publisher_by,
    'committente':  CRM.P14b_carried_out_as_customer_by,
    'distributore': CRM.P14c_carried_out_as_distributor_by,
}


def fzeri_to_qudt(unit):
    if unit in unit_fzeri_to_qudt:
        return QUDT[unit_fzeri_to_qudt[unit]]


def production_role_to_property(role):
    if role in production_roles:
        return production_roles[role]
    else:
        return None
