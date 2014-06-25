#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

from rdflib import Namespace, Literal, RDF, RDFS
from hashlib import sha1
from urllib import quote_plus

# init namespaces
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PRO = Namespace("http://purl.org/spar/pro")
TIME = Namespace("http://www.w3.org/2006/time#")
FABIO = Namespace("http://purl.org/spar/fabio/")
FENTRY = Namespace("http://www.essepuntato.it/2014/03/fentry/")
FRBR = Namespace("http://purl.org/vocab/frbr/core#")
PROV = Namespace("http://www.w3.org/ns/prov#")
# TODO: add DATACITE to identificators
DATACITE = Namespace("http://purl.org/spar/datacite")
QUDT = Namespace("http://qudt.org/vocab/unit#")
FZERI_FENTRY = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/schedaF/")
FZERI_OAENTRY = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/schedaOA/")
FZERI_NEGATIVE = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/negative/")
FZERI_DIMAGES = Namespace("http://fe.fondazionezeri.unibo.it/foto/")
FZERI_COLLECTION = Namespace("http://fe.fondazionezeri.unibo.it/collection/")

FZERI_DIMENSION = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/dimension/")
FZERI_SERIE = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/serie/")
FZERI_BOX = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/box/")
FZERI_MATERIAL = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/material/")
FZERI_ENTRYTYPE = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/entry_type/")
FZERI_IDENTIFIER = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/identifier/")
FZERI_PHOTOFORMAT = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/photo_format/")
FZERI_PHOTOCOLOR = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/photo_color/")
FZERI_PHOTOTYPE = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/photo_type/")
FZERI_CONDITIONTYPE = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/condition_type/")

unit_fzeri_to_qudt = {
    'mm': QUDT.Millimeter,
    'cm': QUDT.Centimeter,
    'm': QUDT.Meter,
}


class FZeriParserSchedaF:
    def __init__(self, xmlentry, graph):
        self.entry_id = self.oaentry_id = self.negative_id = self.myentry = None
        self.xmlentry = xmlentry
        self.graph = graph
        self.production_counter = 0

    def parse(self):
        try:
            self.entry_id = self.xmlentry.find("PARAGRAFO/SERCD").text
            self.oaentry_id = self.xmlentry.find("PARAGRAFO/SERCDOA").text
        except AttributeError:
            print "Entry has no ID!!!"
            return
        try:
            self.negative_id = quote_plus(self.xmlentry.find("PARAGRAFO/ROFI").text)
        except AttributeError:
            self.negative_id = None

        self.init_graph()

        # Process all paragraphs
        for child in self.xmlentry.findall("PARAGRAFO"):
            if len(child):   # paragraph does contain at least one subelement
                if child[0].tag == "RIPETIZIONE":
                    for repchild in child:
                        # call the appropriate parse_paragraph_* function
                        getattr(self, "parse_paragraph_" +
                                      child.attrib["etichetta"].lower().
                                replace(' ', '_').replace('(', '').replace(')', ''))(repchild, repchild.attrib['prog'])
                else:
                    # call the appropriate parse_paragraph_* function
                    getattr(self, "parse_paragraph_" + child.attrib["etichetta"].lower().
                            replace(' ', '_').replace('(', '').replace(')', ''))(child)

    # Init graph with the entry and various global resources
    def init_graph(self):
        self.myentry = FZERI_FENTRY[self.entry_id]
        self.graph.add((self.myentry, RDF.type, CRM.E31_Document))
        self.graph.add((self.myentry, RDF.type, FENTRY.FEntry))
        self.graph.add((self.myentry, CRM.P1_is_identified_by, Literal(self.entry_id)))
        title = FZERI_FENTRY[self.entry_id + '/title']
        self.graph.add((title, RDF.type, CRM.E35_Title))
        self.graph.add((title, RDF.type, DCTERMS.title))
        self.graph.add((title, RDFS.label, Literal(self.xmlentry.attrib['intestazione'])))
        self.graph.add((self.myentry, CRM.P102_has_title, title))
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        self.graph.add((myphoto, RDF.type, CRM['E22_Man-Made_Object']))
        self.graph.add((myphoto, RDF.type, FENTRY.Photograph))
        self.graph.add((myphoto, CRM.P1_is_identified_by, Literal(self.entry_id)))
        self.graph.add((self.myentry, CRM.P70_documents, myphoto))
        self.graph.add((myphoto, CRM.P70i_is_documented_in, self.myentry))
        self.graph.add((self.myentry, FENTRY.describes, myphoto))
        production = FZERI_FENTRY[self.entry_id + '/photo/production']
        self.graph.add((production, RDF.type, CRM.E12_Production))
        self.graph.add((production, CRM.P108_produced, myphoto))
        self.graph.add((myphoto, CRM.P108i_was_produced_by, production))

    # begin COPYRIGHT paragraph
    # COPYRIGHT contains only one field
    # example:
    #     CPRD: PI_0219/4/7
    def parse_paragraph_copyright(self, paragraph):
        copyright_exp_date = FZERI_FENTRY[self.entry_id + '/copyright']
        self.graph.add((copyright_exp_date, RDF.type, CRM.E30_Right))
        if paragraph.find("CRPD") is not None:
            self.graph.add((copyright_exp_date, CRM.P3_has_note, Literal(paragraph.find("CRPD").text)))
        self.graph.add((copyright_exp_date, CRM.P104i_applies_to, self.myentry))
        self.graph.add((self.myentry, CRM.P104_is_subject_to, copyright_exp_date))
        ### end COPYRIGHT paragraph

    # begin NOTES paragraph
    # NOTES contains only one field
    # example:
    #     OSS: Incollata su cartone delle stesse misure.
    def parse_paragraph_notes(self, paragraph):
        self.graph.add((self.myentry, CRM.P3_has_note, Literal(paragraph.find("OSS").text)))
        ### end NOTES paragraph

    # begin SUPERVISOR paragraph
    # SUPERVISOR contains only one field
    # example:
    #     FUR: Giudici C.
    def parse_paragraph_supervisor(self, paragraph):
        node = paragraph.find("FUR")
        if node is None:
            return
        supervisor = FZERI_FENTRY[self.entry_id + '/supervisor']
        self.graph.add((supervisor, RDF.type, CRM.E39_Actor))
        self.graph.add((supervisor, RDF.type, FOAF.Agent))
        self.graph.add((supervisor, RDFS.label, Literal(node.text)))
        self.graph.add((supervisor, FOAF.name, Literal(node.text)))
        creation = FZERI_FENTRY[self.entry_id + '/cataloguing']
        self.graph.add((creation, RDF.type, CRM.E65_Creation))
        self.graph.add((creation, CRM.P11_had_participant, supervisor))
        self.graph.add((supervisor, CRM.P11i_participated_in, creation))
        self.graph.add((self.myentry, RDF.type, FOAF.Document))
        role = FZERI_FENTRY[self.entry_id + '/supervisor/role']
        self.graph.add((role, RDF.type, PRO.roleInTime))
        self.graph.add((role, PRO.withRole, Literal("supervisor")))
        self.graph.add((role, PRO.relatesToDocument, self.myentry))
        self.graph.add((supervisor, PRO.holdsRoleInTime, role))
        self.graph.add((creation, CRM.P94_created, self.myentry))
        self.graph.add((self.myentry, CRM.P94i_was_created_by, creation))
        ### end SUPERVISOR paragraph

    # begin CLASSIFICATION paragraph
    # example:
    #     UBFU: Girolamo di Benvenuto 2
    #     UBFT: Pittura italiana sec. XV. Siena. Benvenuto di Giovanni, Girolamo di Benvenuto
    #     UBFS: Pittura italiana
    #     UBFP: Fototeca  Zeri
    #     INVN: 45423
    #     SERCD: 67680
    #     UBFF: 5
    #     UBFC: PI_0199/5/42
    #     SERCDOA: 19030
    #     UBFN: 0199
    def parse_paragraph_classification(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        collection = serie = box = issue = None
        for node in paragraph:
            if node.tag == "SERCDOA":
                self.graph.add((self.myentry, CRM.P67_refers_to, FZERI_OAENTRY[node.text]))
            elif node.tag == "INVN":
                inv = FZERI_FENTRY[self.entry_id + '/inventory/' + node.text]
                self.graph.add((inv, RDF.type, CRM.E42_Identifier))
                self.graph.add((inv, RDFS.label, Literal(node.text)))
                self.graph.add((inv, CRM.P149i_identifies, myphoto))
                self.graph.add((myphoto, CRM.P149_is_identified_by, inv))
            elif node.tag == "UBFP":
                collection = FZERI_COLLECTION[sha1(node.text.encode('utf-8')).hexdigest()]
                self.graph.add((collection, RDF.type, CRM.E53_Place))
                self.graph.add((collection, CRM.P87_is_identified_by, Literal(node.text)))
            elif node.tag == "UBFS":
                serie = FZERI_SERIE[sha1(node.text.encode('utf-8')).hexdigest()]
                self.graph.add((serie, RDF.type, CRM.E53_Place))
                self.graph.add((serie, CRM.P87_is_identified_by, Literal(node.text)))
            elif node.tag == "UBFT":
                box = FZERI_BOX[sha1(node.text.encode('utf-8')).hexdigest() +
                                "/" + paragraph.find("UBFN").text]
                self.graph.add((box, RDF.type, CRM.E53_Place))
                self.graph.add((box, CRM.P87_is_identified_by, Literal(node.text)))
                self.graph.add((box, CRM.P87_is_identified_by, Literal(paragraph.find("UBFN").text)))
            elif node.tag == "UBFU":
                issue = FZERI_BOX[sha1(node.text.encode('utf-8')).hexdigest() +
                                  "/" + paragraph.find("UBFF").text]
                self.graph.add((issue, RDF.type, CRM.E53_Place))
                self.graph.add((issue, CRM.P87_is_identified_by, Literal(node.text)))
                self.graph.add((issue, CRM.P87_is_identified_by, Literal(paragraph.find("UBFF").text)))
                self.graph.add((issue, CRM.P54i_is_current_permanent_location_of, myphoto))
                self.graph.add((myphoto, CRM.P54_has_current_permanent_location, issue))
            elif node.tag == "UBFC":
                self.graph.add((myphoto, CRM.P54_has_current_permanent_location, Literal(node.text)))
        contained = issue
        for container in box, serie, collection:
            if container:
                self.graph.add((container, CRM.P59_has_section, contained))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
                contained = container
        ### end CLASSIFICATION paragraph

    # begin OWNERSHIP paragraph
    # example:
    #     CDGG: proprietà Ente pubblico non territoriale
    #     CDGS: Alma Mater Studiorum Università di Bologna
    def parse_paragraph_ownership(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        acquisition = FZERI_FENTRY[self.entry_id + '/photo/ownership']
        self.graph.add((acquisition, RDF.type, CRM.E8_Acquisition))
        self.graph.add((acquisition, CRM.P24_transferred_title_of, myphoto))
        self.graph.add((myphoto, CRM.P24i_changed_ownership_through, acquisition))
        for node in paragraph:
            if node.tag == "CDGS":
                actor = FZERI_FENTRY[self.entry_id + '/photo/ownership/owner']
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                self.graph.add((actor, RDFS.label, Literal(node.text)))
                self.graph.add((actor, CRM.P22i_acquired_title_through, acquisition))
                self.graph.add((acquisition, CRM.P22_transferred_title_to, actor))
            elif node.tag == "CDGG":
                acquisition = FZERI_FENTRY[self.entry_id + '/photo/ownership']
                self.graph.add((acquisition, CRM.P3_has_note, Literal(node.text)))
        ### end OWNERSHIP paragraph

    # begin CODES paragraph
    # example:
    #     NCTR: 08
    #     ESC: Fondazione Federico Zeri - Università di Bologna
    #     TSK: F
    #     LIR: I
    # TODO: LIR field has yet to be mapped
    def parse_paragraph_codes(self, paragraph):
        for node in paragraph:
            if node.tag == "TSK":
                entry_type = FZERI_ENTRYTYPE[node.text]
                self.graph.add((entry_type, RDF.type, CRM.E55_Type))
                self.graph.add((entry_type, RDFS.label, Literal(node.text)))
                self.graph.add((self.myentry, CRM.P2_has_type, entry_type))
                self.graph.add((entry_type, CRM.P2i_is_type_of, self.myentry))
            elif node.tag == "NCTN":
                identifier = FZERI_FENTRY[self.entry_id + '/id_number']
                self.graph.add((identifier, RDF.type, CRM.E42_Identifier))
                self.graph.add((identifier, RDFS.label, Literal(node.text)))
                self.graph.add((identifier, CRM.P2_has_type, FZERI_IDENTIFIER.id_number))
                self.graph.add((FZERI_IDENTIFIER.id_number, CRM.P2i_is_type_of, identifier))
                self.graph.add((self.myentry, CRM.P48_has_preferred_identifier, identifier))
                self.graph.add((identifier, CRM.P48i_is_preferred_identifier_of, self.myentry))
            elif node.tag == "NCTR":
                identifier = FZERI_FENTRY[self.entry_id + '/regional_code']
                self.graph.add((identifier, RDF.type, CRM.E42_Identifier))
                self.graph.add((identifier, RDFS.label, Literal(node.text)))
                self.graph.add((identifier, CRM.P2_has_type, FZERI_IDENTIFIER.regional_code))
                self.graph.add((FZERI_IDENTIFIER.regional_code, CRM.P2i_is_type_of, identifier))
                self.graph.add((identifier, CRM.P48i_is_preferred_identifier_of, self.myentry))
                self.graph.add((self.myentry, CRM.P48_has_preferred_identifier, identifier))
            elif node.tag == "ESC":
                actor = FZERI_FENTRY[self.entry_id + '/keeper']
                self.graph.add((actor, RDF.type, CRM.E40_Legal_Body))
                self.graph.add((actor, RDF.type, FOAF.Agent))
                self.graph.add((actor, FOAF.name, Literal(node.text)))
                role = FZERI_FENTRY[self.entry_id + '/keeper/role']
                self.graph.add((role, RDF.type, PRO.roleInTime))
                self.graph.add((role, PRO.withRole, Literal("keeper")))
                self.graph.add((role, PRO.relatesToDocument, self.myentry))
                self.graph.add((actor, CRM.P50i_is_current_keeper_of, self.myentry))
                self.graph.add((self.myentry, CRM.P50_has_current_keeper, actor))
            # TODO: LIR has yet to be mapped
            elif node.tag == "LIR":
                pass
        ### end CODES paragraph

    # begin CATALOGUING paragraph
    # example:
    #     CMPD: 10/10/2005 0.00.00
    #     CMPN: Erika Giuliani
    def parse_paragraph_cataloguing(self, paragraph):
        creation = FZERI_FENTRY[self.entry_id + '/cataloguing']
        self.graph.add((creation, RDF.type, CRM.E65_Creation))
        for node in paragraph:
            if node.tag == "CMPD":
                timespan = FZERI_FENTRY[self.entry_id + '/cataloguing/ts']
                self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                date = FZERI_FENTRY[self.entry_id + '/cataloguing/date']
                self.graph.add((date, RDF.type, CRM.E49_Time_Appellation))
                self.graph.add((date, RDFS.label, Literal(node.text)))
                self.graph.add((date, CRM.P78i_identifies, timespan))
                self.graph.add((timespan, CRM.P78_is_identified_by, date))
                self.graph.add((timespan, CRM['P4i_is_time-span_of'], timespan))
                self.graph.add((creation, CRM['P4_has_time-span'], timespan))
            elif node.tag == "CMPN":
                actor = FZERI_FENTRY[self.entry_id + '/cataloguing/actor']
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                self.graph.add((actor, RDFS.label, Literal(node.text)))
                self.graph.add((actor, CRM.P14i_performed, creation))
                self.graph.add((creation, CRM.P14_carried_out_by, actor))
        self.graph.add((creation, CRM.P94_created, self.myentry))
        self.graph.add((self.myentry, CRM.P94i_was_created_by, creation))
        ### end CATALOGUING paragraph

    # begin UPDATING paragraph
    # example:
    #     AGGD: 09/10/2012
    #     AGGN: Marcello Rossini
    def parse_paragraph_updating(self, paragraph, rep):
        transformation = FZERI_FENTRY[self.entry_id + '/cataloguing/update/' + str(rep)]
        self.graph.add((transformation, RDF.type, CRM.E81_Transformation))
        for node in paragraph:
            if node.tag == "AGGD":
                timespan = FZERI_FENTRY[self.entry_id + '/cataloguing/update/' + str(rep) + '/ts']
                self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                self.graph.add((timespan, CRM['P4i_is_time-span_of'], transformation))
                self.graph.add((transformation, CRM['P4_has_time-span'], timespan))
                date = FZERI_FENTRY[self.entry_id + '/cataloguing/update/' + str(rep) + '/date']
                self.graph.add((date, RDF.type, CRM.E49_Time_Appellation))
                self.graph.add((date, RDFS.label, Literal(node.text)))
                self.graph.add((date, CRM.P78i_identifies, timespan))
                self.graph.add((timespan, CRM.P78_is_identified_by, date))
            elif node.tag == "AGGN":
                actor = FZERI_FENTRY[self.entry_id + '/cataloguing/update/' + str(rep) + '/actor']
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                self.graph.add((actor, RDFS.label, Literal(node.text)))
                self.graph.add((actor, CRM.P11i_participated_in, transformation))
                self.graph.add((transformation, CRM.P11_had_participant, actor))
        self.graph.add((transformation, CRM.P124_transformed, self.myentry))
        self.graph.add((self.myentry, CRM.P124i_was_transformed_by, transformation))
        ### end UPDATING paragraph

    # begin OBJECT paragraph
    # example:
    #     MISO: supporto primario
    #     MTX: BN
    #     QNTN: 1
    #     OGTS: assemblaggio
    #     MISD: 240
    #     MISA: 215
    #     MISL: 165
    #     OGTB: m
    #     MTC: gelatina ai sali d'argento/ carta baritata
    #     MISU: mm
    #     OGTD: positivo
    def parse_paragraph_object(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        dimensions = {"MISA": "height", "MISL": "width", "MISD": "diameter"}
        for node in paragraph:
            if node.tag == "OGTD":
                self.graph.add((myphoto, CRM.P2_has_type, Literal(node.text)))
            elif node.tag == "QNTN":
                self.graph.add((myphoto, CRM.P57_has_number_of_parts, Literal(node.text)))
            elif node.tag == "OGTB":
                self.graph.add((myphoto, DC.type, Literal(node.text)))
            elif node.tag == "OGTS":
                self.graph.add((myphoto, DC['format'], FZERI_PHOTOFORMAT[quote_plus(node.text)]))
            elif node.tag == "MTX":
                self.graph.add((myphoto, DC['format'], FZERI_PHOTOCOLOR[quote_plus(node.text)]))
            elif node.tag == "MTC":
                self.graph.add((myphoto, CRM.P45_consists_of, FZERI_MATERIAL[quote_plus(node.text)]))
                self.graph.add((FZERI_MATERIAL[quote_plus(node.text)], CRM.P45i_is_incorporated_in,
                                myphoto))
            elif node.tag in dimensions.keys():
                dimension = FZERI_FENTRY[self.entry_id + '/photo/' + dimensions[node.tag]]
                self.graph.add((dimension, RDF.type, CRM.E54_Dimension))
                self.graph.add((dimension, CRM.P2_has_type, FZERI_DIMENSION[dimensions[node.tag]]))
                self.graph.add((FZERI_DIMENSION[dimensions[node.tag]], CRM.P2i_is_type_of, dimension))
                self.graph.add((dimension, CRM.P90_has_value, Literal(node.text)))
                if paragraph.find("MISU") is not None:
                    self.graph.add((dimension, CRM.P91_has_unit,
                                    unit_fzeri_to_qudt[paragraph.find("MISU").text]))
                    self.graph.add((unit_fzeri_to_qudt[paragraph.find("MISU").text],
                                    CRM.P91i_is_unit_of, dimension))
                if paragraph.find("MISO") is not None:
                    self.graph.add((dimension, CRM.P2_has_type,
                                    FZERI_DIMENSION[quote_plus(paragraph.find("MISO").text)]))
                    self.graph.add((FZERI_DIMENSION[quote_plus(paragraph.find("MISO").text)],
                                    CRM.P2i_is_type_of, dimension))
                self.graph.add((dimension, CRM.P43i_is_dimension_of, myphoto))
                self.graph.add((myphoto, CRM.P43_has_dimension, dimension))

    # begin SUBJECT paragraph
    # example:
    #     SGLA: Girolamo di Benvenuto (Girolamo del Guasta) - sec. XVI - Madonna con Bambino e san Giovannino
    #     FTAT: insieme
    #     SGLL: Alessandro Botticelli (1446-1510). Madonna m.d. Christusknaben u.d. kleinen Johannes
    #     SGTI: Madonna con Bambino e san Giovannino
    #     SGLT: School of Sano di Pietro. Madonna and Child with Saints
    #     SGLS: del catalogatore
    #     OGTD: dipinto
    def parse_paragraph_subject(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        depicted_subject = FZERI_FENTRY[self.entry_id + '/photo/subject']
        subj_title = FZERI_FENTRY[self.entry_id + '/photo/subject/title']
        self.graph.add((subj_title, RDF.type, CRM.E35_Title))
        self.graph.add((subj_title, RDF.type, DCTERMS.title))
        self.graph.add((depicted_subject, RDF.type, CRM.E1_CRM_Entity))
        self.graph.add((depicted_subject, CRM.P62i_is_depicted_by, myphoto))
        self.graph.add((myphoto, CRM.P62_depicts, depicted_subject))
        for node in paragraph:
            if node.tag == "SGTI":
                self.graph.add((depicted_subject, CRM.P1_is_identified_by, Literal(node.text)))
            elif node.tag == "SGLT":
                self.graph.add((subj_title, RDFS.label, Literal(node.text)))
                self.graph.add((subj_title, FENTRY.isProperTitleOf, depicted_subject))
                self.graph.add((depicted_subject, FENTRY.hasProperTitle, subj_title))
            elif node.tag == "SGLL":
                self.graph.add((subj_title, RDFS.label, Literal(node.text)))
                self.graph.add((subj_title, FENTRY.isParallelTitleOf, depicted_subject))
                self.graph.add((depicted_subject, FENTRY.hasParallelTitle, subj_title))
            elif node.tag == "SGLA":
                self.graph.add((subj_title, RDFS.label, Literal(node.text)))
                self.graph.add((subj_title, FENTRY.isAttributedTitleOf, depicted_subject))
                self.graph.add((depicted_subject, FENTRY.hasAttributedTitle, subj_title))
            elif node.tag == "SGLS":
                self.graph.add((subj_title, CRM.P3_has_note, Literal(node.text)))
            elif node.tag == "FTAT":
                self.graph.add((depicted_subject, CRM.P3_has_note, Literal(node.text)))
            elif node.tag == "OGTD":
                self.graph.add((depicted_subject, CRM.P2_has_type, Literal(node.text)))
        ### end SUBJECT paragraph

    # begin AUTHOR paragraph
    # example:
    #     AUTN: Girolamo di Benvenuto
    #     AUTB: Scuola italiana, scuola toscana, scuola senese
    #     AUTP: Girolamo del Guasta
    #     AUTI: Palmezzano Marco (?)
    def parse_paragraph_author(self, paragraph, rep):
        # TODO: isn't it already described in the actual artwork?
        production = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep)]
        self.graph.add((production, RDF.type, CRM.E12_Production))
        self.graph.add((production, CRM.P108_produced, FZERI_OAENTRY[self.oaentry_id]))
        self.graph.add((FZERI_OAENTRY[self.oaentry_id], CRM.P108i_was_produced_by, production))
        actor = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep) + '/author']
        self.graph.add((actor, RDF.type, CRM.E39_Actor))
        self.graph.add((actor, CRM.P14i_performed, production))
        self.graph.add((production, CRM.P14_carried_out_by, actor))
        # TODO: add PROV-O relations (as specified in TPDL paper)
        for node in paragraph:
            if node.tag == "AUTN":
                proper_name = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep) + '/author/proper_name']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(node.text)))
                self.graph.add((proper_name, CRM.P131i_identifies, actor))
                self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
            elif node.tag == "AUTP":
                pseudonym = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep) + '/author/pseudonym']
                self.graph.add((pseudonym, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((pseudonym, RDFS.label, Literal(node.text)))
                self.graph.add((pseudonym, CRM.P131i_identifies, actor))
                self.graph.add((actor, CRM.P131_is_identified_by, pseudonym))
            elif node.tag == "AUTI":
                other_name = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep) + '/author/other_name']
                self.graph.add((other_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((other_name, RDFS.label, Literal(node.text)))
                self.graph.add((other_name, CRM.P131i_identifies, actor))
                self.graph.add((actor, CRM.P131_is_identified_by, other_name))
            elif node.tag == "AUTB":
                context = FZERI_OAENTRY[self.oaentry_id + '/artwork/production/' + str(rep) + '/author/context']
                self.graph.add((context, RDF.type, CRM.E62_String))
                self.graph.add((context, RDFS.label, Literal(node.text)))
                self.graph.add((actor, FENTRY.hasCulturalContext, context))
                self.graph.add((context, FENTRY.isCulturalContextOf, actor))
        ### end AUTHOR paragraph

    # begin DATING paragraph
    # example:
    #     DTSV: ca.
    #     DTMM: iscrizione
    #     DTSF: 1967
    #     DTZG: XX
    #     DTMS: fotografia eseguita in occasione della vendita all'asta nel 1961
    #     DTSL: ca.
    #     DTSI: 1967
    def parse_paragraph_dating(self, paragraph):
        production = FZERI_FENTRY[self.entry_id + '/photo/production']
        p_production = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter)]
        self.graph.add((p_production, RDF.type, CRM.E12_Production))
        self.graph.add((p_production, CRM.P9i_forms_part_of, production))
        self.graph.add((production, CRM.P9_consists_of, p_production))
        timespan = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/date']
        self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
        self.graph.add((timespan, CRM['P4i_is_time-span_of'], p_production))
        self.graph.add((p_production, CRM['P4_has_time-span'], timespan))
        for node in paragraph:
            if node.tag == "DTZG":
                century = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                       str(self.production_counter) + '/date/century']
                self.graph.add((century, RDF.type, CRM.E49_Time_Appellation))
                self.graph.add((century, RDFS.label, Literal(node.text)))
                self.graph.add((century, CRM.P78i_identifies, timespan))
                self.graph.add((timespan, CRM.P78_is_identified_by, century))
            elif node.tag == "DTSI":
                begin = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                     str(self.production_counter) + '/date/begin']
                self.graph.add((begin, RDF.type, TIME.Instant))
                self.graph.add((begin, TIME.inXSDDateTime, Literal(node.text)))
                self.graph.add((timespan, RDF.type, TIME.TemporalEntity))
                self.graph.add((timespan, TIME.hasBeginning, begin))
                if paragraph.find("DTSV") is not None:
                    self.graph.add((timespan, CRM.P79_beginning_is_qualified_by, Literal(paragraph.find("DTSV").text)))
            elif node.tag == "DTSF":
                end = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                   str(self.production_counter) + '/date/end']
                self.graph.add((end, RDF.type, TIME.Instant))
                self.graph.add((end, TIME.inXSDDateTime, Literal(node.text)))
                self.graph.add((timespan, RDF.type, TIME.TemporalEntity))
                self.graph.add((timespan, TIME.hasEnd, end))
                if paragraph.find("DTSL") is not None:
                    self.graph.add((timespan, CRM.P80_end_is_qualified_by, Literal(paragraph.find("DTSL").text)))
            elif node.tag == "DTMM":
                assignment = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                          str(self.production_counter) + '/assignment']
                self.graph.add((assignment, RDF.type, CRM.E13_Attribute_Assignment))
                self.graph.add((assignment, CRM.P17_was_motivated_by, Literal(node.text)))
                self.graph.add((assignment, CRM.P141_assigned, timespan))
                self.graph.add((timespan, CRM.P141i_was_assigned_by, assignment))
                self.graph.add((assignment, CRM.P140_assigned_attribute_to, p_production))
                self.graph.add((p_production, CRM.P140i_was_attributed_by, assignment))
            elif node.tag == "DTMS":
                self.graph.add((p_production, CRM.P3_has_note, Literal(node.text)))
        self.production_counter += 1
        ### end DATING paragraph

    # begin DATING paragraph
    # example:
    #     AUFI: The Art Institute of Chicago. Photograph Department
    #     AUFK: numero di inventario
    #     AUFM: n.r.
    #     AUFN: Anonimo
    #     AUFA: Edizioni Brogi
    #     AUFR: fotografo principale
    #     AUFS: studio
    def parse_paragraph_photographer(self, paragraph, rep):
        production = FZERI_FENTRY[self.entry_id + '/photo/production']
        p_production = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter)]
        self.graph.add((p_production, RDF.type, CRM.E12_Production))
        self.graph.add((p_production, CRM.P9i_forms_part_of, production))
        self.graph.add((production, CRM.P9_consists_of, p_production))
        actor = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/photographer']
        self.graph.add((actor, RDF.type, CRM.E39_Actor))
        self.graph.add((actor, CRM.P14_performed, p_production))
        self.graph.add((p_production, CRM.P14_carried_out_by, actor))
        for node in paragraph:
            if node.tag == "AUFN":
                proper_name = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                           str(self.production_counter) + '/photographer/proper_name']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(node.text)))
                self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
            elif node.tag == "AUFI":
                # TODO: add VCard Ontology
                address = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                       str(self.production_counter) + '/photographer/address']
                self.graph.add((address, RDF.type, CRM.E51_Contact_Point))
                self.graph.add((address, RDFS.label, Literal(node.text)))
                self.graph.add((actor, CRM.P76_has_contact_point, address))
            elif node.tag == "AUFM":
                try:
                    attribute_assignment
                except UnboundLocalError:
                    attribute_assignment = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                                        str(self.production_counter) + '/photographer/assignment']
                    self.graph.add((attribute_assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((attribute_assignment, CRM.P141_assigned, actor))
                    self.graph.add((actor, CRM.P141i_was_assigned_by, attribute_assignment))
                    self.graph.add((attribute_assignment, CRM.P140_assigned_attribute_to, p_production))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, attribute_assignment))
                self.graph.add((attribute_assignment, CRM.P17_was_motivated_by, Literal(node.text)))
            elif node.tag == "AUFK":
                try:
                    attribute_assignment
                except UnboundLocalError:
                    attribute_assignment = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                                        str(self.production_counter) + '/photographer/assignment']
                    self.graph.add((attribute_assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((attribute_assignment, CRM.P141_assigned, actor))
                    self.graph.add((actor, CRM.P141i_was_assigned_by, attribute_assignment))
                    self.graph.add((attribute_assignment, CRM.P140_assigned_attribute_to, p_production))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, attribute_assignment))
                self.graph.add((attribute_assignment, CRM.P16_used_specific_object, Literal(node.text)))
            elif node.tag == "AUFA":
                self.graph.add((actor, CRM.P3_has_note, Literal(node.text)))
            elif node.tag == "AUFS":
                self.graph.add((actor, CRM.P2_has_type, Literal(node.text)))
            elif node.tag == "AUFR":
                self.graph.add((actor, RDF.type, FOAF.Agent))
                myphoto = FZERI_FENTRY[self.entry_id + '/photo']
                self.graph.add((myphoto, RDF.type, FOAF.Document))
                role = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                    str(self.production_counter) + '/photographer/role']
                self.graph.add((role, RDF.type, PRO.roleInTime))
                self.graph.add((role, PRO.withRole, Literal(node.text)))
                self.graph.add((role, PRO.relatesToDocument, myphoto))
                self.graph.add((actor, PRO.holdsRoleInTime, role))
        self.production_counter += 1
        ### end PHOTOGRAPHER paragraph

    # begin PRODUCTION AND PUBLISHING paragraph
    # example:
    #     PDFK: 3071
    #     PDFI: Christies
    #     PDFN: Procacci, Michele
    #     PDFL: Londra
    #     PDFM: timbro
    #     PDFB: Christie's
    #     SFIT: L'Umbria Illustrata
    #     PDFD: 1980
    #     EDIT: Tilli - Perugia
    #     PDFR: committente
    def parse_paragraph_production_and_publishing(self, paragraph, rep):
        production = FZERI_FENTRY[self.entry_id + '/photo/production']
        p_production = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter)]
        self.graph.add((p_production, RDF.type, CRM.E12_Production))
        self.graph.add((p_production, CRM.P9i_forms_part_of, production))
        self.graph.add((production, CRM.P9_consists_of, p_production))
        publisher = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/publisher']
        self.graph.add((publisher, RDF.type, CRM.E39_Actor))
        self.graph.add((publisher, CRM.P14_performed, p_production))
        self.graph.add((p_production, CRM.P14_carried_out_by, publisher))
        for node in paragraph:
            if node.tag == "PDFN":
                proper_name = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                           str(self.production_counter) + '/publisher/proper_name']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(node.text)))
                self.graph.add((publisher, CRM.P131_is_identified_by, proper_name))
            elif node.tag == "PDFB":
                corporate_name = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                              str(self.production_counter) + '/publisher/corporate_name']
                self.graph.add((corporate_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((corporate_name, RDFS.label, Literal(node.text)))
                self.graph.add((publisher, CRM.P131_is_identified_by, corporate_name))
            elif node.tag == "PDFI":
                # TODO: add VCard Ontology
                address = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                       str(self.production_counter) + '/publisher/address']
                self.graph.add((address, RDF.type, CRM.E51_Contact_Point))
                self.graph.add((address, RDFS.label, Literal(node.text)))
                self.graph.add((publisher, CRM.P76_has_contact_point, address))
            elif node.tag == "PDFM":
                try:
                    attribute_assignment
                except UnboundLocalError:
                    attribute_assignment = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                                        str(self.production_counter) + '/publisher/assignment']
                    self.graph.add((attribute_assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((attribute_assignment, CRM.P141_assigned, publisher))
                    self.graph.add((publisher, CRM.P141i_was_assigned_by, attribute_assignment))
                    self.graph.add((attribute_assignment, CRM.P140_assigned_attribute_to, p_production))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, attribute_assignment))
                self.graph.add((attribute_assignment, CRM.P17_was_motivated_by, Literal(node.text)))
            elif node.tag == "PDFK":
                try:
                    attribute_assignment
                except UnboundLocalError:
                    attribute_assignment = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                                        str(self.production_counter) + '/publisher/assignment']
                    self.graph.add((attribute_assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((attribute_assignment, CRM.P141_assigned, publisher))
                    self.graph.add((publisher, CRM.P141i_was_assigned_by, attribute_assignment))
                    self.graph.add((attribute_assignment, CRM.P140_assigned_attribute_to, p_production))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, attribute_assignment))
                self.graph.add((attribute_assignment, CRM.P16_used_specific_object, Literal(node.text)))
            elif node.tag == "PDFR":
                self.graph.add((publisher, RDF.type, FOAF.Agent))
                myphoto = FZERI_FENTRY[self.entry_id + '/photo']
                self.graph.add((myphoto, RDF.type, FOAF.Document))
                role = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                    str(self.production_counter) + '/photographer/role']
                self.graph.add((role, RDF.type, PRO.roleInTime))
                self.graph.add((role, PRO.withRole, Literal(node.text)))
                self.graph.add((role, PRO.relatesToDocument, myphoto))
                self.graph.add((publisher, PRO.holdsRoleInTime, role))
            elif node.tag == "PDFL":
                location = FZERI_FENTRY[self.entry_id + '/photo/production/' +
                                        str(self.production_counter) + '/publisher/location']
                self.graph.add((location, RDF.type, CRM.E53_Place))
                self.graph.add((location, RDFS.label, Literal(node.text)))
                self.graph.add((p_production, CRM.P7_took_place_at, location))
            elif node.tag == "PDFD":
                timespan = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/date']
                self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                date = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/date/year']
                self.graph.add((date, RDF.type, CRM.E49_Time_Appellation))
                self.graph.add((date, RDFS.label, Literal(node.text)))
                self.graph.add((date, CRM.P78i_identifies, timespan))
                self.graph.add((timespan, CRM.P78_is_identified_by, date))
                self.graph.add((timespan, CRM['P4i_is_time-span_of'], p_production))
                self.graph.add((p_production, CRM['P4_has_time-span'], timespan))
            # TODO: EDIT has yet to be mapped
            elif node.tag == "EDIT":
                # edition = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter) + '/edition']
                # self.graph.add((edition, RDF.type, CRM['E52_Time-Span']))
                # self.graph.add((edition, RDFS.label, Literal(node.text)))
                # self.graph.add((edition, CRM['P4i_is_time-span_of'], p_production))
                # self.graph.add((p_production, CRM['P4_has_time-span'], edition))
                pass
            # TODO: SFIT has yet to be mapped
            elif node.tag == "SFIT":
                pass
        self.production_counter += 1
        ### end PRODUCTION AND PUBLISHING paragraph

    # begin PLACE AND DATE OF THE SHOT paragraph
    # example:
    #     LRA: Londra
    #     LRCC: Roma
    #     LRCS: Regno Unito
    #     LRD: 1967
    #     LRO: Asta Christie's 11/07/1980
    def parse_paragraph_place_and_date_of_the_shot(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        creation = FZERI_FENTRY[self.entry_id + '/photo/creation']
        self.graph.add((creation, RDF.type, CRM.E65_Creation))
        self.graph.add((creation, CRM.P94_created, myphoto))
        self.graph.add((myphoto, CRM.P94i_was_created_by, creation))
        country = village = None
        for node in paragraph:
            if node.tag == "LRD":
                timespan = FZERI_FENTRY[self.entry_id + '/photo/creation/date']
                self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                date = FZERI_FENTRY[self.entry_id + '/photo/creation/date/year']
                self.graph.add((date, RDF.type, CRM.E49_Time_Appellation))
                self.graph.add((date, RDFS.label, Literal(node.text)))
                self.graph.add((date, CRM.P78i_identifies, timespan))
                self.graph.add((timespan, CRM.P78_is_identified_by, date))
                self.graph.add((timespan, CRM['P4i_is_time-span_of'], creation))
                self.graph.add((creation, CRM['P4_has_time-span'], timespan))
            elif node.tag == "LRCS":
                country = FZERI_FENTRY[self.entry_id + '/photo/creation/country']
                self.graph.add((country, RDF.type, CRM.E53_Place))
                self.graph.add((country, RDFS.label, Literal(node.text)))
            elif node.tag == "LRCC" or node.tag == "LRA":
                village = FZERI_FENTRY[self.entry_id + '/photo/creation/village']
                self.graph.add((village, RDF.type, CRM.E53_Place))
                self.graph.add((village, RDFS.label, Literal(node.text)))
            elif node.tag == "LRO":
                occasion = FZERI_FENTRY[self.entry_id + '/photo/creation/occasion']
                self.graph.add((occasion, RDF.type, CRM.E4_Period))
                self.graph.add((occasion, RDFS.label, Literal(node.text)))
                self.graph.add((occasion, CRM.P10i_contains, creation))
                self.graph.add((creation, CRM.P10_falls_within, occasion))
        if country and village:
            self.graph.add((country, CRM.P89i_contains, village))
            self.graph.add((village, CRM.P89_falls_within, country))
            self.graph.add((village, CRM.P7i_witnessed, creation))
            self.graph.add((creation, CRM.P7_took_place_at, village))
        elif country:
            self.graph.add((country, CRM.P7i_witnessed, creation))
            self.graph.add((creation, CRM.P7_took_place_at, country))
        elif village:
            self.graph.add((village, CRM.P7i_witnessed, creation))
            self.graph.add((creation, CRM.P7_took_place_at, village))
        ### end PLACE AND DATE OF THE SHOT paragraph

    # begin RELATIONS WITH OTHER PHOTOGRAPHIC OBJECTS (NEGATIVE) paragraph
    # example:
    #     ROFC: Bologna/ Fondazione Federico Zeri - Università di Bologna/ Fototeca Zeri
    #     ROFI: C 6133
    #     ROFO: negativo
    #     ROFF: positivo
    def parse_paragraph_relations_with_other_photographic_objects_negative(self, paragraph):
        production = FZERI_FENTRY[self.entry_id + '/photo/production']
        p_production = FZERI_FENTRY[self.entry_id + '/photo/production/' + str(self.production_counter)]
        self.graph.add((p_production, RDF.type, CRM.E12_Production))
        self.graph.add((p_production, CRM.P9i_forms_part_of, production))
        self.graph.add((production, CRM.P9_consists_of, p_production))
        negative = FZERI_NEGATIVE[self.negative_id]
        self.graph.add((negative, RDF.type, CRM['E22_Man-Made_Object']))
        self.graph.add((negative, CRM.P1_is_identified_by, Literal(self.negative_id)))
        self.graph.add((p_production, CRM.P16_used_specific_object, negative))
        self.graph.add((negative, CRM.P16i_was_used_for, p_production))
        for node in paragraph:
            if node.tag == "ROFI":  # the ID we altready mapped in self.negative_id
                pass
            if node.tag == "ROFC":
                place = FZERI_NEGATIVE[self.negative_id + '/location']
                self.graph.add((place, RDF.type, CRM.E53_Place))
                self.graph.add((place, RDFS.label, Literal(node.text)))
                self.graph.add((place, CRM.P55i_is_current_location_of, negative))
                self.graph.add((negative, CRM.P55_has_current_location, place))
            if node.tag == "ROFO":
                neg_type = FZERI_PHOTOTYPE[quote_plus(node.text)]
                self.graph.add((neg_type, RDF.type, CRM.E55_Type))
                self.graph.add((neg_type, RDFS.label, Literal(node.text)))
                self.graph.add((neg_type, CRM.P2i_is_type_of, negative))
                self.graph.add((negative, CRM.P2_has_type, neg_type))
            # TODO: ROFF has yet to be mapped
            if node.tag == "ROFF":
                pass
        self.production_counter += 1
        ### end RELATIONS WITH OTHER PHOTOGRAPHIC OBJECTS (NEGATIVE) paragraph

    # begin DIGITAL IMAGE paragraph
    # example:
    #     VERSO: Pubblico
    #     FTAT: insieme
    #     FTAN: \80000\45600\45423.jpg
    #     FTAX: allegata
    #     FTAP: fotografia digitale
    def parse_paragraph_digital_image(self, paragraph, rep):
        image_id = paragraph.find('FTAN')
        if image_id is None:
            return
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        digital_image = FZERI_FENTRY[self.entry_id + '/photo/dimage/' + str(rep)]
        self.graph.add((digital_image, RDF.type, CRM.E38_Image))
        self.graph.add((digital_image, RDF.type, FABIO.DigitalManifestation))
        self.graph.add((self.myentry, FENTRY.describes, digital_image))
        self.graph.add((myphoto, FABIO.hasManifestation, digital_image))
        self.graph.add((digital_image, CRM.P138_represents, myphoto))
        self.graph.add((myphoto, CRM.P138i_has_representation, digital_image))
        img_file = FZERI_DIMAGES[image_id.text.replace('\\', '/').strip('/')]
        self.graph.add((img_file, RDF.type, CRM.E38_Image))
        self.graph.add((img_file, RDF.type, FABIO.ComputerFile))
        self.graph.add((img_file, FRBR.exemplar, digital_image))
        self.graph.add((self.myentry, FENTRY.describes, img_file))
        self.graph.add((img_file, CRM.P138_represents, digital_image))
        self.graph.add((digital_image, CRM.P138i_has_representation, img_file))
        for node in paragraph:
            if node.tag == "FTAT":
                self.graph.add((digital_image, CRM.P3_has_note, Literal(node.text)))
            elif node.tag == "FTAP":
                image_type = FZERI_PHOTOTYPE[quote_plus(node.text)]
                self.graph.add((image_type, RDF.type, CRM.E55_Type))
                self.graph.add((image_type, RDFS.label, Literal(node.text)))
                self.graph.add((image_type, CRM.P2i_is_type_of, digital_image))
                self.graph.add((digital_image, CRM.P2_has_type, image_type))
            # TODO: FTAX and VERSO
            elif node.tag == "FTAX":
                pass
            elif node.tag == "VERSO":
                pass
        ### end DIGITAL IMAGE paragraph

    # begin PROVENANCE paragraph
    # example:
    #     PRDI: 1953/12/10
    #     PRVP: Firenze
    #     PRCM: Collezione privata Gnoli Umberto
    #     PRVS: Italia
    #     PRL: Londra
    #     PRDU: 1947/ ca.
    #     PRCD: Università degli studi di Roma "La Sapienza": Dipartimento di Storia dell'Arte
    #     PRVC: Firenze
    def parse_paragraph_provenance(self, paragraph, rep):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        provenance = FZERI_FENTRY[self.entry_id + '/photo/provenance' + str(rep)]
        self.graph.add((provenance, RDF.type, CRM.E53_Place))
        self.graph.add((provenance, CRM.P53i_is_former_or_current_location_of, myphoto))
        self.graph.add((myphoto, CRM.P53_has_former_or_current_location, provenance))
        activity = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/move']
        self.graph.add((activity, RDF.type, CRM.E9_Move))
        timespan = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/move/date']
        self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
        self.graph.add((timespan, CRM['P4i_is_time-span_of'], activity))
        self.graph.add((activity, CRM['P4_has_time-span'], timespan))
        self.graph.add((provenance, CRM.P26_moved_to, activity))
        self.graph.add((provenance, CRM.P26i_was_destination_of, activity))
        self.graph.add((activity, CRM.P25_moved, myphoto))
        self.graph.add((myphoto, CRM.P25i_moved_by, activity))
        country = district = town = repository = None
        for node in paragraph:
            if node.tag == "PRDI":
                begin = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/move/date/begin']
                self.graph.add((begin, RDF.type, TIME.Instant))
                self.graph.add((begin, TIME.inXSDDateTime, Literal(node.text)))
                self.graph.add((timespan, RDF.type, TIME.TemporalEntity))
                self.graph.add((timespan, TIME.hasBeginning, begin))
            elif node.tag == "PRDU":
                end = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/move/date/end']
                self.graph.add((end, RDF.type, TIME.Instant))
                self.graph.add((end, TIME.inXSDDateTime, Literal(node.text)))
                self.graph.add((timespan, RDF.type, TIME.TemporalEntity))
                self.graph.add((timespan, TIME.hasEnd, end))
            elif node.tag == "PRVP":
                district = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/district']
                self.graph.add((district, RDF.type, CRM.E53_Place))
                self.graph.add((district, RDFS.label, Literal(node.text)))
            elif node.tag == "PRVS":
                country = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/country']
                self.graph.add((country, RDF.type, CRM.E53_Place))
                self.graph.add((country, RDFS.label, Literal(node.text)))
            elif node.tag == "PRVC" or node.tag == "PRL":
                town = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/town']
                self.graph.add((town, RDF.type, CRM.E53_Place))
                self.graph.add((town, RDFS.label, Literal(node.text)))
            elif node.tag == "PRCM":
                collection = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/collection']
                self.graph.add((collection, RDF.type, CRM.E46_Section_Definition))
                self.graph.add((collection, RDFS.label, Literal(node.text)))
                self.graph.add((collection, CRM.P87i_identifies, provenance))
                self.graph.add((provenance, CRM.P87_is_identified_by, collection))
            elif node.tag == "PRCD":
                repository = FZERI_FENTRY[self.entry_id + '/photo/provenance/' + str(rep) + '/repository']
                self.graph.add((repository, RDF.type, CRM.E53_Place))
                self.graph.add((repository, RDFS.label, Literal(node.text)))
        contained = provenance
        for container in repository, town, district, country:
            if container:
                self.graph.add((container, CRM.P59_has_section, contained))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
                contained = container
        ### end PROVENANCE paragraph

    # begin LOCATION paragraph
    # example:
    #     LDCM: Fototeca Zeri
    #     LDCN: Ex convento di S. Cristina
    #     PVCR: Emilia-Romagna
    #     PVCP: BO
    #     PVCC: Bologna
    #     LDCU: piazzetta G. Morandi, 2
    #     LDCS: Grandi Formati
    def parse_paragraph_location(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        location = FZERI_FENTRY[self.entry_id + '/photo/location']
        self.graph.add((location, RDF.type, CRM.E53_Place))
        self.graph.add((location, CRM.P55i_is_current_location_of, myphoto))
        self.graph.add((myphoto, CRM.P55_has_current_location, location))
        region = district = town = repository = None
        for node in paragraph:
            if node.tag == "LDCN":
                repository = FZERI_FENTRY[self.entry_id + '/photo/location/repository']
                self.graph.add((repository, RDF.type, CRM.E53_Place))
                self.graph.add((repository, RDFS.label, Literal(node.text)))
            elif node.tag == "PVCP":
                district = FZERI_FENTRY[self.entry_id + '/photo/location/district']
                self.graph.add((district, RDF.type, CRM.E53_Place))
                self.graph.add((district, RDFS.label, Literal(node.text)))
            elif node.tag == "PVCR":
                region = FZERI_FENTRY[self.entry_id + '/photo/location/region']
                self.graph.add((region, RDF.type, CRM.E53_Place))
                self.graph.add((region, RDFS.label, Literal(node.text)))
            elif node.tag == "PVCC":
                town = FZERI_FENTRY[self.entry_id + '/photo/location/town']
                self.graph.add((town, RDF.type, CRM.E53_Place))
                self.graph.add((town, RDFS.label, Literal(node.text)))
            elif node.tag == "LDCM":
                collection = FZERI_FENTRY[self.entry_id + '/photo/location/collection']
                self.graph.add((collection, RDF.type, CRM.E46_Section_Definition))
                self.graph.add((collection, RDFS.label, Literal(node.text)))
                self.graph.add((collection, CRM.P87i_identifies, location))
                self.graph.add((location, CRM.P87_is_identified_by, collection))
            elif node.tag == "LDCS":
                precise_location = FZERI_FENTRY[self.entry_id + '/photo/location/precise_location']
                self.graph.add((precise_location, RDF.type, CRM.E46_Section_Definition))
                self.graph.add((precise_location, RDFS.label, Literal(node.text)))
                self.graph.add((precise_location, CRM.P87i_identifies, location))
                self.graph.add((location, CRM.P87_is_identified_by, precise_location))
            elif node.tag == "LDCU":
                # TODO: add VCard Ontology
                address = FZERI_FENTRY[self.entry_id + '/photo/location/address']
                self.graph.add((address, RDF.type, CRM.E53_Place))
                self.graph.add((address, RDFS.label, Literal(node.text)))
                self.graph.add((location, CRM.P87_is_identified_by, address))
        contained = location
        for container in repository, town, district, region:
            if container:
                self.graph.add((container, CRM.P59_has_section, contained))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
                contained = container
        ### end LOCATION paragraph

    # begin STATE OF PRESERVATION paragraph
    # example:
    #     STCS: sbiadimento
    #     STCC: mediocre
    def parse_paragraph_state_of_preservation(self, paragraph):
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        condition = FZERI_FENTRY[self.entry_id + '/photo/condition']
        self.graph.add((condition, RDF.type, CRM.E3_Condition_State))
        self.graph.add((condition, CRM.P44i_is_condition_of, myphoto))
        self.graph.add((myphoto, CRM.P44_has_condition, condition))
        for node in paragraph:
            if node.tag == "STCS":
                self.graph.add((condition, RDFS.label, Literal(node.text)))
            elif node.tag == "STCC":
                condition_type = FZERI_CONDITIONTYPE[quote_plus(node.text)]
                self.graph.add((condition_type, RDF.type, CRM.E55_Type))
                self.graph.add((condition_type, RDFS.label, Literal(node.text)))
                self.graph.add((condition_type, CRM.P2i_is_type_of, condition))
                self.graph.add((condition, CRM.P2_has_type, condition_type))
        ### end STATE OF PRESERVATION paragraph

    # begin RELATION TO OTHER OBJECTS paragraph
    # example:
    #     OGTI: Collage di fotografie della predella raffigurante il Miracolo dell'ostia profanata di Paolo Uccello
    #     RVEL: 2
    def parse_paragraph_relation_to_other_objects(self, paragraph):
        collection_desc = paragraph.find('OGTI').text
        if collection_desc is None:
            return
        myphoto = FZERI_FENTRY[self.entry_id + '/photo']
        collection = FZERI_COLLECTION[sha1(collection_desc.encode('utf-8')).hexdigest()]
        self.graph.add((collection, RDF.type, CRM.E18_Physical_Thing))
        self.graph.add((collection, CRM.P46_is_composed_of, myphoto))
        self.graph.add((myphoto, CRM.P46i_forms_part_of, collection))
        for node in paragraph:
            # TODO
            if node.tag == "RVEL":
                pass
            elif node.tag == "OGTI":
                self.graph.add((collection, RDFS.label, Literal(node.text)))
        ### end RELATION TO OTHER OBJECTS paragraph
