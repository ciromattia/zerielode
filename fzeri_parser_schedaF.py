#!/usr/local/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Ciro Mattia Gonano <ciromattia@gmail.com>'
__license__ = 'ISC'
__copyright__ = '2014, Ciro Mattia Gonano <ciromattia@gmail.com>'
__docformat__ = 'restructuredtext en'

from rdflib import Namespace, Literal, RDF, RDFS
from hashlib import sha1
from urllib import quote_plus
import fzeri_conversion_maps

# init namespaces
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
FZERI_FENTRY = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/schedaF/")
FZERI_OAENTRY = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/schedaOA/")
FZERI_NEGATIVE = Namespace("http://fe.fondazionezeri.unibo.it/catalogo/negative/")
FZERI_THESAURI = Namespace("http://fe.fondazionezeri.unibo.it/thesauri/")
FZERI_DIMAGES = Namespace("http://fe.fondazionezeri.unibo.it/foto/")


class FZeriParserSchedaF:
    def __init__(self, xmlentry, graph):
        self.current_paragraph = None
        self.current_iteration = None
        self.elements = None
        self.dict = {}
        self.xmlentry = xmlentry
        self.graph = graph

    def parse(self):
        # flatten XML to dict
        for child in self.xmlentry.findall("PARAGRAFO"):
            if len(child):   # paragraph does contain at least one subelement
                self.current_paragraph = child
                #print "Paragraph: " + self.current_paragraph.attrib["etichetta"]
                if self.current_paragraph[0].tag == "RIPETIZIONE":
                    for i in self.current_paragraph:
                        self.current_iteration = int(i.attrib["prog"])
                        self.elements = i
                        self.parse_elements()
                else:
                    self.current_iteration = None
                    self.elements = self.current_paragraph
                    self.parse_elements()
        self.map_to_crm()
        return self.dict

    def parse_elements(self):
        for child in self.elements:
            if self.current_iteration:
                if child.tag not in self.dict or self.dict[child.tag] is not dict:
                    self.dict[child.tag] = {}
                self.dict[child.tag][self.current_iteration] = child.text
            else:
                self.dict[child.tag] = child.text

    def map_to_crm(self):
        try:
            entry_id = self.dict["SERCD"]
        except KeyError:
            print "Entry has no ID!!!"
            return

        # Entry
        myentry = FZERI_FENTRY[entry_id]
        self.graph.add((myentry, RDF.type, CRM.E31_Document))
        title = FZERI_FENTRY[entry_id + '/title']
        self.graph.add((title, RDF.type, CRM.E35_Title))
        self.graph.add((title, RDFS.label, Literal(self.xmlentry.attrib['intestazione'])))
        self.graph.add((myentry, CRM.P102_has_title, title))
        self.graph.add((myentry, CRM.P1_is_identified_by, Literal(entry_id)))
        self.graph.add((myentry, CRM.P67_refers_to, FZERI_OAENTRY[self.dict['SERCDOA']]))
        if "TSK" in self.dict:
            entry_type = FZERI_THESAURI['entry_type/' + self.dict['TSK']]
            self.graph.add((entry_type, RDF.type, CRM.E55_Type))
            self.graph.add((entry_type, RDFS.label, Literal(self.dict['TSK'])))
            self.graph.add((myentry, CRM.P2_has_type, entry_type))
        if "NCTN" in self.dict:
            identifier = FZERI_FENTRY[entry_id + '/id_number']
            self.graph.add((identifier, RDF.type, CRM.E42_Identifier))
            self.graph.add((identifier, RDFS.label, Literal(self.dict['NCTN'])))
            self.graph.add((identifier, CRM.P2_has_type, FZERI_THESAURI['identifier/id_number']))
            self.graph.add((myentry, CRM.P48_has_preferred_identifier, identifier))
        if "NCTR" in self.dict:
            identifier = FZERI_FENTRY[entry_id + '/regional_code']
            self.graph.add((identifier, RDF.type, CRM.E42_Identifier))
            self.graph.add((identifier, RDFS.label, Literal(self.dict['NCTR'])))
            self.graph.add((identifier, CRM.P2_has_type, FZERI_THESAURI['identifier/regional_code']))
            self.graph.add((myentry, CRM.P48_has_preferred_identifier, identifier))

        # Cataloguing notes
        # TODO: LIR is yet to be mapped
        if "LIR" in self.dict:
            pass
        if "ESC" in self.dict:
            actor = FZERI_THESAURI['actor/' + sha1(self.dict['ESC'].encode('utf-8')).hexdigest()]
            self.graph.add((actor, RDF.type, CRM.E40_Legal_Body))
            proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['ESC'].encode('utf-8')).hexdigest() +
                                         '/proper_name/']
            self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
            self.graph.add((proper_name, RDFS.label, Literal(self.dict['ESC'])))
            self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
            self.graph.add((myentry, CRM.P50_has_current_keeper, actor))
        creation = FZERI_FENTRY[entry_id + '/cataloguing/']
        self.graph.add((creation, RDF.type, CRM.E65_Creation))
        if "CMPD" in self.dict:
            timespan = FZERI_FENTRY[entry_id + '/cataloguing/date/']
            self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
            self.graph.add((timespan, RDFS.label, Literal(self.dict['CMPD'])))
            self.graph.add((creation, CRM['P4_has_time-span'], timespan))
        if "CMPN" in self.dict:
            actor = FZERI_THESAURI['actor/' + sha1(self.dict['CMPN'].encode('utf-8')).hexdigest()]
            self.graph.add((actor, RDF.type, CRM.E39_Actor))
            proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['CMPN'].encode('utf-8')).hexdigest() +
                                         '/proper_name/']
            self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
            self.graph.add((proper_name, RDFS.label, Literal(self.dict['CMPN'])))
            self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
            self.graph.add((creation, CRM.P14_carried_out_by, actor))
        self.graph.add((myentry, CRM.P94i_was_created_by, creation))
        # Updates
        if "AGGD" in self.dict:
            for index in self.dict['AGGD']:
                transformation = FZERI_FENTRY[entry_id + '/cataloguing/update/' + str(index)]
                self.graph.add((transformation, RDF.type, CRM.E81_Transformation))
                timespan = FZERI_FENTRY[entry_id + '/cataloguing/update/' + str(index) + '/date/']
                self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                self.graph.add((timespan, RDFS.label, Literal(self.dict['AGGD'][index])))
                self.graph.add((transformation, CRM['P4_has_time-span'], timespan))
                if "AGGN" in self.dict and index in self.dict['AGGN']:
                    actor = FZERI_THESAURI['actor/' + sha1(self.dict['AGGN'][index].encode('utf-8')).hexdigest()]
                    self.graph.add((actor, RDF.type, CRM.E39_Actor))
                    proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['AGGN'][index].encode('utf-8')).hexdigest() +
                                                 '/proper_name/']
                    self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                    self.graph.add((proper_name, RDFS.label, Literal(self.dict['AGGN'][index])))
                    self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
                    self.graph.add((transformation, CRM.P11_had_participant, actor))
                self.graph.add((myentry, CRM.P124i_was_transformed_by, transformation))
        # if "FUR" in self.dict:
        #     self.graph.add((myentry, CRM.P3_has_note, Literal(self.dict['FUR'])))
        if "OSS" in self.dict:
            self.graph.add((myentry, CRM.P3_has_note, Literal(self.dict['OSS'])))

        # Object
        myphoto = FZERI_FENTRY[entry_id + '/photo']
        self.graph.add((myphoto, RDF.type, CRM['E22_Man-Made_Object']))
        self.graph.add((myphoto, CRM.P1_is_identified_by, Literal(entry_id)))
        self.graph.add((myentry, CRM.P70_documents, myphoto))
        if "OGTD" in self.dict:
            self.graph.add((myphoto, CRM.P2_has_type, Literal(self.dict['OGTD'])))
        if "QNTN" in self.dict:
            self.graph.add((myphoto, CRM.P57_has_number_of_parts, Literal(self.dict['QNTN'])))
        # OGTB (i.e. bibliographic level) has not been mapped yet
        if "FTAT" in self.dict:
            self.graph.add((myphoto, CRM.P3_has_note, Literal(self.dict['FTAT'])))
        # if "MTX" in self.dict:
        #    self.graph.add((myphoto, CRM.P45_consist_of, FZERI_THESAURI['material'][self.dict['MTX']]))
        if "MTC" in self.dict:
            self.graph.add((myphoto, CRM.P45_consist_of, FZERI_THESAURI['material/' + quote_plus(self.dict['MTC'])]))
        if "MISA" in self.dict:
            ph_height = FZERI_FENTRY[entry_id + '/photo/height']
            self.graph.add((ph_height, RDF.type, CRM.E54_Dimension))
            self.graph.add((ph_height, CRM.P2_has_type, FZERI_THESAURI['dimension/height']))
            self.graph.add((ph_height, CRM.P90_has_value, Literal(self.dict['MISA'])))
            if "MISU" in self.dict:
                self.graph.add((ph_height, CRM.P91_has_unit, fzeri_conversion_maps.fzeri_to_qudt(self.dict['MISU'])))
            self.graph.add((myphoto, CRM.P43_has_dimension, ph_height))
        if "MISL" in self.dict:
            ph_width = FZERI_FENTRY[entry_id + '/photo/width']
            self.graph.add((ph_width, RDF.type, CRM.E54_Dimension))
            self.graph.add((ph_width, CRM.P2_has_type, FZERI_THESAURI['dimension/width']))
            self.graph.add((ph_width, CRM.P90_has_value, Literal(self.dict['MISL'])))
            if "MISU" in self.dict:
                self.graph.add((ph_width, CRM.P91_has_unit, fzeri_conversion_maps.fzeri_to_qudt(self.dict['MISU'])))
            self.graph.add((myphoto, CRM.P43_has_dimension, ph_width))
        if "MISO" in self.dict:
            ph_dimension_type = FZERI_THESAURI['dimension/' + quote_plus(self.dict['MISO'])]
            self.graph.add((myphoto, CRM.P43_has_dimension, ph_dimension_type))

        # Logical location
        inv = FZERI_FENTRY[entry_id + '/inventory/' + self.dict["INVN"]]
        self.graph.add((inv, RDF.type, CRM.E42_Identifier))
        self.graph.add((inv, CRM.P48_has_preferred_identifier, Literal(self.dict["INVN"])))
        self.graph.add((myphoto, CRM.P149_is_identified_by, inv))
        collection = FZERI_THESAURI['collection/' + sha1(self.dict['UBFP'].encode('utf-8')).hexdigest()]
        serie = FZERI_THESAURI['serie/' + sha1(self.dict['UBFS'].encode('utf-8')).hexdigest()]
        box = FZERI_THESAURI['box/' + sha1(self.dict['UBFT'].encode('utf-8') + self.dict['UBFN']).hexdigest()]
        issue = FZERI_THESAURI['issue/' + sha1(self.dict['UBFU'].encode('utf-8') + self.dict['UBFF']).hexdigest()]
        self.graph.add((collection, RDF.type, CRM.E53_Place))
        self.graph.add((collection, CRM.P87_is_identified_by, Literal(self.dict['UBFP'])))
        self.graph.add((serie, RDF.type, CRM.E53_Place))
        self.graph.add((serie, CRM.P87_is_identified_by, Literal(self.dict['UBFS'])))
        self.graph.add((serie, CRM.P59i_is_located_on_or_within, collection))
        self.graph.add((box, RDF.type, CRM.E53_Place))
        self.graph.add((box, CRM.P87_is_identified_by, Literal(self.dict['UBFT'])))
        self.graph.add((box, CRM.P87_is_identified_by, Literal(self.dict['UBFN'])))
        self.graph.add((box, CRM.P59i_is_located_on_or_within, serie))
        self.graph.add((issue, RDF.type, CRM.E53_Place))
        self.graph.add((issue, CRM.P87_is_identified_by, Literal(self.dict['UBFU'])))
        self.graph.add((issue, CRM.P87_is_identified_by, Literal(self.dict['UBFF'])))
        self.graph.add((issue, CRM.P59i_is_located_on_or_within, box))
        self.graph.add((myphoto, CRM.P54_has_current_permanent_location, issue))
        self.graph.add((myphoto, CRM.P54_has_current_permanent_location, Literal(self.dict['UBFC'])))

        # Subject
        subj_id = sha1(self.dict['SGTI'].encode('utf-8')).hexdigest()
        depicted_subject = FZERI_THESAURI['subject/' + subj_id]
        self.graph.add((depicted_subject, RDF.type, CRM.E1_CRM_Entity))
        self.graph.add((depicted_subject, CRM.P1_is_identified_by, Literal(self.dict['SGTI'])))
        self.graph.add((myphoto, CRM.P62_depicts, depicted_subject))
        subj_title = None
        has_title_property = CRM.P102_has_title
        if "SGLT" in self.dict:
            subj_title = self.dict['SGLT']
            has_title_property = CRM.P102a_has_proper_title
        elif "SGLL" in self.dict:
            subj_title = self.dict['SGLL']
            has_title_property = CRM.P102b_has_parallel_title
        elif "SGLA" in self.dict:
            subj_title = self.dict['SGLA']
            has_title_property = CRM.P102c_has_attributed_title
        if subj_title:
            subj_title_resource = FZERI_THESAURI['subject/' + subj_id + '/title/' +
                                                 sha1(subj_title.encode('utf-8')).hexdigest()]
            self.graph.add((subj_title_resource, RDF.type, CRM.E35_Title))
            self.graph.add((subj_title_resource, CRM.P149_is_identified_by, Literal(subj_title)))
            if "SGLS" in self.dict:
                self.graph.add((subj_title_resource, CRM.P3_has_note, Literal(self.dict['SGLS'])))
            self.graph.add((depicted_subject, has_title_property, subj_title_resource))

        # artwork's author
        # TODO: isn't it already described in the actual artwork?
        if "AUTN" in self.dict:
            production = FZERI_OAENTRY[self.dict['SERCDOA'] + '/artwork/production']
            self.graph.add((production, RDF.type, CRM.E12_Production))
            for index in self.dict['AUTN']:
                p_production = FZERI_OAENTRY[entry_id + '/artwork/production/' + str(index)]
                self.graph.add((p_production, RDF.type, CRM.E12_Production))
                actor = FZERI_THESAURI['actor/' + sha1(self.dict['AUTN'][index].encode('utf-8')).hexdigest()]
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['AUTN'][index].encode('utf-8')).hexdigest() +
                                             '/proper_name/']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(self.dict['AUTN'][index])))
                self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
                if "AUTP" in self.dict and index in self.dict['AUTP']:
                    pseudonym = FZERI_THESAURI['actor/' + sha1(self.dict['AUTN'][index].encode('utf-8')).hexdigest() +
                                               '/pseudonym/']
                    self.graph.add((pseudonym, RDF.type, CRM.E82_Actor_Appellation))
                    self.graph.add((pseudonym, RDFS.label, Literal(self.dict['AUTP'][index])))
                    self.graph.add((actor, CRM.P131_is_identified_by, pseudonym))
                if "AUTB" in self.dict and index in self.dict['AUTB']:
                    context = FZERI_THESAURI['actor/' + sha1(self.dict['AUTN'][index].encode('utf-8')).hexdigest() +
                                             '/context/']
                    self.graph.add((context, RDF.type, CRM.E62_String))
                    self.graph.add((context, RDFS.label, Literal(self.dict['AUTB'][index])))
                    self.graph.add((actor, CRM.P3a_cultural_context, context))
                self.graph.add((p_production, CRM.P14_carried_out_by, actor))
                self.graph.add((production, CRM.P9_consists_of, p_production))

        # Production
        production = FZERI_FENTRY[entry_id + '/photo/production']
        self.graph.add((production, RDF.type, CRM.E12_Production))
        self.graph.add((myphoto, CRM.P108i_was_produced_by, production))
        production_counter = 1
        # Production dating
        if "DTZG" in self.dict:
            p_production = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/']
            self.graph.add((p_production, RDF.type, CRM.E12_Production))
            timespan = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/date/']
            self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
            self.graph.add((timespan, RDFS.label, Literal(self.dict['DTZG'])))
            if "DTSI" in self.dict:
                self.graph.add((timespan, CRM.P82a_begin_of_the_begin, Literal(self.dict['DTSI'])))
            if "DTSV" in self.dict:
                self.graph.add((timespan, CRM.P79_beginning_is_qualified_by, Literal(self.dict['DTSV'])))
            if "DTSF" in self.dict:
                self.graph.add((timespan, CRM.P82b_end_of_the_end, Literal(self.dict['DTSI'])))
            if "DTSL" in self.dict:
                self.graph.add((timespan, CRM.P80_end_is_qualified_by, Literal(self.dict['DTSL'])))
            self.graph.add((p_production, CRM['P4_has_time-span'], timespan))
            if "DTMM" in self.dict:
                assignment = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/assignment']
                self.graph.add((assignment, RDF.type, CRM.E13_Attribute_Assignment))
                self.graph.add((assignment, CRM.P17_was_motivated_by, Literal(self.dict['DTMM'])))
                self.graph.add((p_production, CRM.P140i_was_attributed_by, assignment))
            if "DTMS" in self.dict:
                self.graph.add((p_production, CRM.P3_has_note, Literal(self.dict['DTMS'])))
            self.graph.add((production, CRM.P9_consists_of, p_production))
            production_counter += 1
        # Photographer
        if "AUFN" in self.dict:
            for index in self.dict['AUFN']:
                p_production = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/']
                self.graph.add((p_production, RDF.type, CRM.E12_Production))
                actor = FZERI_THESAURI['actor/' + sha1(self.dict['AUFN'][index].encode('utf-8')).hexdigest()]
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['AUFN'][index].encode('utf-8')).hexdigest() +
                                             '/proper_name/']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(self.dict['AUFN'][index])))
                self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
                if "AUFI" in self.dict and index in self.dict['AUFI']:
                    address = FZERI_THESAURI['actor/' + sha1(self.dict['AUFN'][index].encode('utf-8')).hexdigest() +
                                             '/address/']
                    self.graph.add((address, RDF.type, CRM.E51_Contact_Point))
                    self.graph.add((address, RDFS.label, Literal(self.dict['AUFI'])))
                    self.graph.add((actor, CRM.P76_has_contact_point, address))
                if "AUFM" in self.dict and index in self.dict['AUFM']:
                    assignment = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/assignment']
                    self.graph.add((assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((assignment, CRM.P17_was_motivated_by, Literal(self.dict['AUFM'])))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, assignment))
                self.graph.add((p_production, CRM.P14_carried_out_by, actor))
                self.graph.add((production, CRM.P9_consists_of, p_production))
                production_counter += 1
        # Production and publishing
        if "PDFN" in self.dict:
            for index in self.dict['PDFN']:
                p_production = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/']
                self.graph.add((p_production, RDF.type, CRM.E12_Production))
                actor = FZERI_THESAURI['actor/' + sha1(self.dict['PDFN'][index].encode('utf-8')).hexdigest()]
                self.graph.add((actor, RDF.type, CRM.E39_Actor))
                proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['PDFN'][index].encode('utf-8')).hexdigest() +
                                             '/proper_name/']
                self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
                self.graph.add((proper_name, RDFS.label, Literal(self.dict['PDFN'][index])))
                self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
                if "PDFI" in self.dict and index in self.dict['PDFI']:
                    address = FZERI_THESAURI['actor/' + sha1(self.dict['PDFN'][index].encode('utf-8')).hexdigest() +
                                             '/address/']
                    self.graph.add((address, RDF.type, CRM.E51_Contact_Point))
                    self.graph.add((address, RDFS.label, Literal(self.dict['PDFI'][index])))
                    self.graph.add((actor, CRM.P76_has_contact_point, address))
                if "PDFM" in self.dict and index in self.dict['PDFM']:
                    assignment = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/assignment']
                    self.graph.add((assignment, RDF.type, CRM.E13_Attribute_Assignment))
                    self.graph.add((assignment, CRM.P17_was_motivated_by, Literal(self.dict['PDFM'][index])))
                    self.graph.add((p_production, CRM.P140i_was_attributed_by, assignment))
                if "PDFL" in self.dict and index in self.dict['PDFL']:
                    location = FZERI_FENTRY[entry_id + '/photo/production/' + str(production_counter) + '/location']
                    self.graph.add((location, RDF.type, CRM.E53_Place))
                    self.graph.add((location, RDFS.label, Literal(self.dict['PDFL'][index])))
                    self.graph.add((p_production, CRM.P7_took_place_at, location))
                prod_property = None
                if "PDFR" in self.dict and index in self.dict['PDFR']:
                    prod_property = fzeri_conversion_maps.production_role_to_property(self.dict['PDFR'][index])
                if prod_property:
                    self.graph.add((p_production, prod_property, actor))
                else:
                    self.graph.add((p_production, CRM.P14_carried_out_by, actor))
                self.graph.add((production, CRM.P9_consists_of, p_production))
                production_counter += 1

        # Creation (place and date of the shot)
        if "LRD" in self.dict:
            creation = FZERI_FENTRY[entry_id + '/photo/creation']
            self.graph.add((creation, RDF.type, CRM.E65_Creation))
            self.graph.add((creation, CRM.P3_has_note, Literal(self.dict['LRD'])))
            self.graph.add((myphoto, CRM.P94i_was_created_by, creation))

        # Relations with other photographic objects (negative)
        if "ROFI" in self.dict:  # ROFI represents the negative number
            self.graph.add((myphoto, CRM.P70i_is_documented_in, FZERI_NEGATIVE[self.dict['ROFI']]))

        # Physical location
        if "LDCN" in self.dict:
            location = FZERI_THESAURI['/location/' + sha1(self.dict['LDCN'].encode('utf-8')).hexdigest()]
            self.graph.add((location, RDF.type, CRM.E53_Place))
            contained = location
            if "PVCC" in self.dict:
                container = FZERI_THESAURI['/location/' + sha1(self.dict['PVCC'].encode('utf-8')).hexdigest()]
                self.graph.add((container, RDF.type, CRM.E53_Place))
                self.graph.add((container, RDFS.label, Literal(self.dict['PVCC'])))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
            if "PVCP" in self.dict:
                container = FZERI_THESAURI['/location/' + sha1(self.dict['PVCP'].encode('utf-8')).hexdigest()]
                self.graph.add((container, RDF.type, CRM.E53_Place))
                self.graph.add((container, RDFS.label, Literal(self.dict['PVCP'])))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
            if "PVCR" in self.dict:
                container = FZERI_THESAURI['/location/' + sha1(self.dict['PVCP'].encode('utf-8')).hexdigest()]
                self.graph.add((container, RDF.type, CRM.E53_Place))
                self.graph.add((container, RDFS.label, Literal(self.dict['PVCP'])))
                self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
            if "LDCU" in self.dict:
                address = FZERI_THESAURI['/location/' + sha1(self.dict['LDCN'].encode('utf-8')).hexdigest() +
                                         '/address/']
                self.graph.add((address, RDF.type, CRM.E53_Place))
                self.graph.add((address, RDFS.label, Literal(self.dict['LDCU'])))
                self.graph.add((location, CRM.P87_is_identified_by, address))
            if "LDCM" in self.dict:
                collection = FZERI_THESAURI['/location/' + sha1(self.dict['LDCN'].encode('utf-8')).hexdigest() +
                                            '/collection/']
                self.graph.add((collection, RDF.type, CRM.E46_Section_Definition))
                self.graph.add((collection, RDFS.label, Literal(self.dict['UBFP'])))
                self.graph.add((location, CRM.P87_is_identified_by, collection))
            self.graph.add((myphoto, CRM.P55_has_current_location, location))

        # Previous physical locations (provenance)
        if "PRCM" in self.dict:
            for index in self.dict['PRCM']:
                provenance = FZERI_THESAURI['/location/' + sha1(self.dict['PRCM'][index].encode('utf-8')).hexdigest()]
                self.graph.add((provenance, RDF.type, CRM.E53_Place))
                contained = provenance
                if "PRVS" in self.dict and index in self.dict['PRVS']:
                    container = FZERI_THESAURI['/location/' +
                                               sha1(self.dict['PRVS'][index].encode('utf-8')).hexdigest()]
                    self.graph.add((container, RDF.type, CRM.E53_Place))
                    self.graph.add((container, RDFS.label, Literal(self.dict['PRVS'][index])))
                    self.graph.add((contained, CRM.P59i_is_located_on_or_within, container))
                if "PRDU" in self.dict and index in self.dict['PRDU']:
                    activity = FZERI_FENTRY[entry_id + '/photo/provenance/' + str(index)]
                    self.graph.add((activity, RDF.type, CRM.E9_Move))
                    timespan = FZERI_FENTRY[entry_id + '/photo/provenance/' + str(index) + '/date/']
                    self.graph.add((timespan, RDF.type, CRM['E52_Time-Span']))
                    self.graph.add((timespan, CRM.P82b_end_of_the_end, Literal(self.dict['PRDU'][index])))
                    if "PRDI" in self.dict:
                        self.graph.add((timespan, CRM.P82a_begin_of_the_begin, Literal(self.dict['PRDI'][index])))
                    self.graph.add((activity, CRM['P4_has_time-span'], timespan))
                    self.graph.add((activity, CRM.P26_moved_from, provenance))
                    self.graph.add((activity, CRM.P25_moved, myphoto))
                self.graph.add((myphoto, CRM.P53_has_former_or_current_location, provenance))

        # Ownership
        if "CDGS" in self.dict:
            acquisition = FZERI_FENTRY[entry_id + '/photo/ownership/']
            self.graph.add((acquisition, RDF.type, CRM.E8_Acquisition))
            actor = FZERI_THESAURI['actor/' + sha1(self.dict['CDGG'].encode('utf-8')).hexdigest()]
            self.graph.add((actor, RDF.type, CRM.E39_Actor))
            proper_name = FZERI_THESAURI['actor/' + sha1(self.dict['CDGG'].encode('utf-8')).hexdigest() +
                                         '/proper_name/']
            self.graph.add((proper_name, RDF.type, CRM.E82_Actor_Appellation))
            self.graph.add((proper_name, RDFS.label, Literal(self.dict['CDGG'])))
            self.graph.add((actor, CRM.P131_is_identified_by, proper_name))
            self.graph.add((acquisition, CRM.P22_transferred_title_to, actor))
            self.graph.add((myphoto, CRM.P24i_changed_ownership_through, acquisition))
            if "CDGG" in self.dict:
                self.graph.add((acquisition, CRM.P3_has_note, Literal(self.dict['CDGG'])))

        # Digital images
        if "FTAN" in self.dict:
            for index in self.dict['FTAN']:
                digital_image = FZERI_DIMAGES[self.dict['FTAN'][index].replace('\\', '/')]
                self.graph.add((digital_image, RDF.type, CRM.E38_Image))
                if "FTAT" in self.dict and index in self.dict['FTAT']:
                    self.graph.add((digital_image, CRM.P3_has_note, Literal(self.dict['FTAT'][index])))
                if "FTAP" in self.dict and index in self.dict['FTAP']:
                    image_type = FZERI_THESAURI['foto_type/' + quote_plus(self.dict['FTAP'][index])]
                    self.graph.add((image_type, RDF.type, CRM.E55_Type))
                    self.graph.add((image_type, RDFS.label, Literal(self.dict['FTAP'][index])))
                    self.graph.add((digital_image, CRM.P2_has_type, image_type))
                # TODO: FTAX and VERSO
                if "FTAX" in self.dict and index in self.dict['FTAX']:
                    pass
                if "VERSO" in self.dict and index in self.dict['VERSO']:
                    pass
                self.graph.add((myphoto, CRM.P138i_has_representation, digital_image))