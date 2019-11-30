#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
****************************************************
ontology_modify.py
Author: Damion Dooley

This script runs specific SPARQL create/update/delete queries on a given
ontology.  Queries are hard-baked below. Modified ontology is saved in place.

python ontology_modify.py test.owl

**************************************************** 
""" 

import optparse
import sys
import os
import rdflib
from rdflib.plugins.sparql.parser import parseUpdate
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.sparql import processUpdate
import rdfextras; rdfextras.registerplugins() # so we can Graph.query()
from rdflib.namespace import OWL, RDF, RDFS

# Do this, otherwise a warning appears on stdout: No handlers could be found for logger "rdflib.term"
import logging; logging.basicConfig(level=logging.ERROR) 

CODE_VERSION = '0.0.1'

def stop_err( msg, exit_code=1 ):
	sys.stderr.write("%s\n" % msg)
	sys.exit(exit_code)

class MyParser(optparse.OptionParser):
	"""
	Allows formatted help info.  From http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output.
	"""
	def format_epilog(self, formatter):
		return self.epilog

class OntologyUpdate(object):
	"""
	Read in an ontology file. Run Sparql 1.1 UPDATE and DELETE
	queries on it.
	"""

	def __init__(self):

		self.graph=rdflib.Graph()

		self.struct = {}
		# JSON-LD @context markup, and as well its used for a prefix encoding table.
		self.struct['@context'] = {
			'obo':'http://purl.obolibrary.org/obo/',
			'owl':'http://www.w3.org/2002/07/owl#',
			'oboInOwl': 'http://www.geneontology.org/formats/oboInOwl#'
		}


	def __main__(self): #, main_ontology_file
		"""

		"""
		(options, args) = self.get_command_line()

		if options.code_version:
			print (CODE_VERSION)
			return CODE_VERSION

		if not len(args):
			stop_err('Please supply an OWL ontology file (in XML/RDF format)')

		main_ontology_file = args[0] #accepts relative path with file name
		main_ontology_file = self.check_folder(main_ontology_file, "Ontology file")
		if not os.path.isfile(main_ontology_file):
			stop_err('Please check the OWL ontology file path')			

		print ("PROCESSING " + main_ontology_file + " ...")

		# Get ontology core filename, without .owl suffix
		ontology_filename = os.path.basename(main_ontology_file).rsplit('.',1)[0]

		self.graph.parse(source=main_ontology_file) 
		
		print (self.doQueryUpdate('delete labels')) # list of labels to delete
		print (self.doQueryUpdate('convert labels')) # list of labels to convert to 'alternate label'

		# Write owl file
		if (self.graph):
			self.graph.serialize(destination=main_ontology_file, format='pretty-xml')
		else:
			print ("Error: No graph output.")

	
	############################## UTILITIES ###########################


	def doQueryUpdate(self, query_name, initBinds = {}):
		"""
		Given a sparql 1.1 update query, perform it. 
		"""

		query = self.queries[query_name]



		try:
			result = processUpdate(self.graph, self.prefixes + query, initBindings=initBinds, initNs=self.namespace)
			#result = parseUpdate(self.graph, self.prefixes + query, initBindings=initBinds, initNs=self.namespace)
			#self.graph.query(self.prefixes + query, initBindings=initBinds, initNs=self.namespace)

		except Exception as e:
			print ("\nSparql query [%s] parsing problem: %s \n" % (query_name, str(e) ))
			return None

		return result


	def get_command_line(self):
		"""
		*************************** Parse Command Line *****************************
		"""
		parser = MyParser(
			description = 'Ontology modification script.',
			usage = 'ontology_modify.py [ontology file path] [options]*',
			epilog="""  """)
		
		# Standard code version identifier.
		parser.add_option('-v', '--version', dest='code_version', default=False, action='store_true', help='Return version of this code.')

		return parser.parse_args()


	def check_folder(self, file_path, message = "Directory for "):
		"""
		Ensures file folder path for a file exists.
		It can be a relative path.
		"""
		if file_path != None:

			path = os.path.normpath(file_path)
			if not os.path.isdir(os.path.dirname(path)): 
				# Not an absolute path, so try default folder where script launched from:
				path = os.path.normpath(os.path.join(os.getcwd(), path) )
				if not os.path.isdir(os.path.dirname(path)):
					stop_err(message + "[" + path + "] does not exist!")			
					
			return path
		return None


	""" 
	Add these PREFIXES to Protege Sparql query window if you want to test a query there:
	"""
	prefixes = r"""
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
	PREFIX owl: <http://www.w3.org/2002/07/owl#>
	PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
	PREFIX obo: <http://purl.obolibrary.org/obo/>
	PREFIX xmls: <http://www.w3.org/2001/XMLSchema#>
	""" 
	namespace = { 
		'owl': rdflib.URIRef('http://www.w3.org/2002/07/owl#'),
		'rdfs': rdflib.URIRef('http://www.w3.org/2000/01/rdf-schema#'),
		'obo': rdflib.URIRef('http://purl.obolibrary.org/obo/'),
		'rdf': rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
		'xmls': rdflib.URIRef('http://www.w3.org/2001/XMLSchema#'),
		'oboInOwl': rdflib.URIRef('http://www.geneontology.org/formats/oboInOwl#')
	}

	queries = {
		##################################################################
		# EXAMPLE: Generic TREE "is a" hierarchy from given root.
		# FUTURE: ADD SORTING OPTIONS, CUSTOM ORDER.
		#
		'tree': prepareQuery("""
			SELECT DISTINCT ?id ?parent ?label ?uiLabel ?definition
			WHERE {	
				?parent rdfs:subClassOf* ?root.
				?id rdfs:subClassOf ?parent.
				OPTIONAL {?id rdfs:label ?label}.
				OPTIONAL {?id obo:GENEPIO_0000006 ?uiLabel}.
				OPTIONAL {?id obo:IAO_0000115 ?definition.}
			}
			ORDER BY ?parent ?label ?uiLabel
		""", initNs = namespace),

		# ################################################################
		# 
		# Update/Delete queries are below. These queries are straight strings.
		# 
		# WARNING: THIS QUERY PROCESSOR THROWS SYNTAX ERROR IF NO SPACE BEFORE PERIOD 
		#

		'delete labels': """
		DELETE {?entity rdfs:label ?label}
		WHERE {
			VALUES ?entity {
			obo:CHEBI_15727 obo:CHEBI_15864 obo:CHEBI_15891 obo:CHEBI_15948 obo:CHEBI_16164 obo:CHEBI_16196 obo:CHEBI_16207 obo:CHEBI_16243 obo:CHEBI_16285 obo:CHEBI_16411 obo:CHEBI_16737 obo:CHEBI_17254 obo:CHEBI_17276 obo:CHEBI_17377 obo:CHEBI_17445 obo:CHEBI_17597 obo:CHEBI_17620 obo:CHEBI_17847 obo:CHEBI_17992 obo:CHEBI_18088 obo:CHEBI_18101 obo:CHEBI_18112 obo:CHEBI_18135 obo:CHEBI_18323 obo:CHEBI_18346 obo:CHEBI_18388 obo:CHEBI_1905  obo:CHEBI_27480 obo:CHEBI_27547 obo:CHEBI_27732 obo:CHEBI_27794 obo:CHEBI_27997 obo:CHEBI_28088 obo:CHEBI_28177 obo:CHEBI_28197 obo:CHEBI_28374 obo:CHEBI_28499 obo:CHEBI_28591 obo:CHEBI_28757 obo:CHEBI_28946 obo:CHEBI_30763 obo:CHEBI_30764 obo:CHEBI_30769 obo:CHEBI_30778 obo:CHEBI_30816 obo:CHEBI_32111 obo:CHEBI_32159 obo:CHEBI_32365 obo:CHEBI_34741 obo:CHEBI_36002 obo:CHEBI_36023 obo:CHEBI_39912 obo:CHEBI_43355 obo:CHEBI_4582  obo:CHEBI_4828  obo:CHEBI_48991 obo:CHEBI_50205 obo:CHEBI_545959obo:CHEBI_6052  obo:CHEBI_6650  obo:CHEBI_66682 obo:CHEBI_68329 obo:CHEBI_68441 obo:CHEBI_68447 obo:CHEBI_68449 obo:CHEBI_68465 obo:CHEBI_68531 obo:CHEBI_68889 obo:CHEBI_691622obo:CHEBI_77131 obo:CHEBI_8198  obo:CHEBI_82914 obo:CHEBI_9629  obo:FOODON_00001059 obo:FOODON_00001287 obo:FOODON_00002439 obo:FOODON_00002475 obo:FOODON_00002711 obo:FOODON_00002933 obo:FOODON_00003049 obo:FOODON_00003083 obo:FOODON_00003140 obo:FOODON_00003157 obo:FOODON_00003229 obo:FOODON_00003230 obo:FOODON_00003238 obo:FOODON_00003239 obo:FOODON_00003240 obo:FOODON_00003242 obo:FOODON_00003243 obo:FOODON_00003245 obo:FOODON_00003248 obo:FOODON_00003249 obo:FOODON_00003250 obo:FOODON_00003252 obo:FOODON_00003253 obo:FOODON_00003255 obo:FOODON_00003260 obo:FOODON_00003261 obo:FOODON_00003263 obo:FOODON_00003268 obo:FOODON_03301055 obo:FOODON_03301103 obo:FOODON_03301105 obo:FOODON_03301116 obo:FOODON_03301175 obo:FOODON_03301217 obo:FOODON_03301397 obo:FOODON_03301440 obo:FOODON_03301474 obo:FOODON_03301585 obo:FOODON_03301619 obo:FOODON_03301632 obo:FOODON_03301660 obo:FOODON_03301672 obo:FOODON_03301705 obo:FOODON_03301729 obo:FOODON_03301826 obo:FOODON_03301889 obo:FOODON_03301906 obo:FOODON_03302111 obo:FOODON_03302379 obo:FOODON_03302775 obo:FOODON_03303207 obo:FOODON_03305417 obo:FOODON_03305518 obo:FOODON_03306255 obo:FOODON_03306867 obo:FOODON_03307177 obo:FOODON_03307240 obo:FOODON_03307744 obo:FOODON_03309462 obo:FOODON_03309491 obo:FOODON_03310232 obo:FOODON_03310272 obo:FOODON_03310273 obo:FOODON_03310290 obo:FOODON_03310351 obo:FOODON_03310820 obo:FOODON_03311555 obo:FOODON_03312036 obo:FOODON_03312067 obo:FOODON_03315184 obo:FOODON_03315258 obo:FOODON_03315751 obo:FOODON_03316042 obo:FOODON_03317254 obo:FOODON_03317446 obo:FOODON_03317508 obo:FOODON_03411043 obo:FOODON_03411205 obo:FOODON_03411237 obo:FOODON_03411258 obo:FOODON_03411269 obo:FOODON_03411316 obo:FOODON_03411323 obo:FOODON_03411335 obo:FOODON_03411423 obo:FOODON_03411457 obo:FOODON_03411514 obo:FOODON_03411854 obo:FOODON_03413878 obo:FOODON_03414363 obo:FOODON_03420156 obo:FOODON_03420157 obo:FOODON_03530027 obo:UBERON_0036016  obo:CHEBI_15724 obo:CHEBI_15761 obo:CHEBI_16828 obo:CHEBI_17295 obo:CHEBI_17574 obo:CHEBI_17895 obo:CHEBI_45658 obo:CHEBI_74077 obo:CHEBI_75632 obo:CHEBI_81556 obo:CHEBI_82392 obo:CHEBI_82912 obo:FOODON_00003251 obo:FOODON_03306347 obo:FOODON_03411222 obo:FOODON_03411328 obo:FOODON_03411669 obo:FOODON_03412112 obo:FOODON_03412248
			} 
			?entity rdfs:label ?label .
		}
		""",

		# Switch given label to alternative term
		# Note: "DELETE" must come before "INSERT"
		'convert labels': """
			DELETE {?entity rdfs:label ?label}
			INSERT {?entity obo:IAO_0000118 ?label}
			WHERE {
				VALUES ?entity {
				obo:CHEBI_10219 obo:CHEBI_10362 obo:CHEBI_11060 obo:CHEBI_1427  obo:CHEBI_15600 obo:CHEBI_15671 obo:CHEBI_15964 obo:CHEBI_16112 obo:CHEBI_16384 obo:CHEBI_16603 obo:CHEBI_16914 obo:CHEBI_16958 obo:CHEBI_17385 obo:CHEBI_17395 obo:CHEBI_17439 obo:CHEBI_17579 obo:CHEBI_17691 obo:CHEBI_17846 obo:CHEBI_17884 obo:CHEBI_18048 obo:CHEBI_18089 obo:CHEBI_18095 obo:CHEBI_18123 obo:CHEBI_18125 obo:CHEBI_1879  obo:CHEBI_1904  obo:CHEBI_2120  obo:CHEBI_25858 obo:CHEBI_25998 obo:CHEBI_27432 obo:CHEBI_27596 obo:CHEBI_27823 obo:CHEBI_27881 obo:CHEBI_28125 obo:CHEBI_28364 obo:CHEBI_28478 obo:CHEBI_28647 obo:CHEBI_31463 obo:CHEBI_31799 obo:CHEBI_31967 obo:CHEBI_32357 obo:CHEBI_32374 obo:CHEBI_32643 obo:CHEBI_32798 obo:CHEBI_32980 obo:CHEBI_35147 obo:CHEBI_35280 obo:CHEBI_41254 obo:CHEBI_45530 obo:CHEBI_4806  obo:CHEBI_48400 obo:CHEBI_50599 obo:CHEBI_57589 obo:CHEBI_5995  obo:CHEBI_62207 obo:CHEBI_63558 obo:CHEBI_63559 obo:CHEBI_63798 obo:CHEBI_64414 obo:CHEBI_68444 obo:CHEBI_68505 obo:CHEBI_69439 obo:CHEBI_70824 obo:CHEBI_71018 obo:CHEBI_73961 obo:CHEBI_75721 obo:CHEBI_75726 obo:CHEBI_76126 obo:CHEBI_80091 obo:CHEBI_84038 obo:CHEBI_84039 obo:CHEBI_84040 obo:CHEBI_85533 obo:CHEBI_90obo:CHEBI_9008  obo:FOODON_00001006 obo:FOODON_00001013 obo:FOODON_00001014 obo:FOODON_00001041 obo:FOODON_00001046 obo:FOODON_00001057 obo:FOODON_00001061 obo:FOODON_00001131 obo:FOODON_00001138 obo:FOODON_00001139 obo:FOODON_00001146 obo:FOODON_00001151 obo:FOODON_00001158 obo:FOODON_00001169 obo:FOODON_00001183 obo:FOODON_00001190 obo:FOODON_00001209 obo:FOODON_00001215 obo:FOODON_00001242 obo:FOODON_00001256 obo:FOODON_00001257 obo:FOODON_00001261 obo:FOODON_00001264 obo:FOODON_00001274 obo:FOODON_00001275 obo:FOODON_00001278 obo:FOODON_00001302 obo:FOODON_00001650 obo:FOODON_00001709 obo:FOODON_00001765 obo:FOODON_00001845 obo:FOODON_00001915 obo:FOODON_00001956 obo:FOODON_00001998 obo:FOODON_00002123 obo:FOODON_00002176 obo:FOODON_00002220 obo:FOODON_00002222 obo:FOODON_00002257 obo:FOODON_00002277 obo:FOODON_00002297 obo:FOODON_00002340 obo:FOODON_00002424 obo:FOODON_00002434 obo:FOODON_00002466 obo:FOODON_00002473 obo:FOODON_00002501 obo:FOODON_00002502 obo:FOODON_00002528 obo:FOODON_00002562 obo:FOODON_00002664 obo:FOODON_00002718 obo:FOODON_00002737 obo:FOODON_00002753 obo:FOODON_00002889 obo:FOODON_00003012 obo:FOODON_00003013 obo:FOODON_00003019 obo:FOODON_00003024 obo:FOODON_00003042 obo:FOODON_00003066 obo:FOODON_00003108 obo:FOODON_00003230 obo:FOODON_00003231 obo:FOODON_00003232 obo:FOODON_00003233 obo:FOODON_00003235 obo:FOODON_00003236 obo:FOODON_00003241 obo:FOODON_00003244 obo:FOODON_00003246 obo:FOODON_00003247 obo:FOODON_00003254 obo:FOODON_00003257 obo:FOODON_00003258 obo:FOODON_00003259 obo:FOODON_00003264 obo:FOODON_00003265 obo:FOODON_00003266 obo:FOODON_00003267 obo:FOODON_00003269 obo:FOODON_00003270 obo:FOODON_00003271 obo:FOODON_00003272 obo:FOODON_03301005 obo:FOODON_03301036 obo:FOODON_03301040 obo:FOODON_03301072 obo:FOODON_03301107 obo:FOODON_03301123 obo:FOODON_03301136 obo:FOODON_03301236 obo:FOODON_03301240 obo:FOODON_03301283 obo:FOODON_03301299 obo:FOODON_03301300 obo:FOODON_03301326 obo:FOODON_03301355 obo:FOODON_03301415 obo:FOODON_03301441 obo:FOODON_03301449 obo:FOODON_03301460 obo:FOODON_03301482 obo:FOODON_03301483 obo:FOODON_03301502 obo:FOODON_03301545 obo:FOODON_03301570 obo:FOODON_03301577 obo:FOODON_03301580 obo:FOODON_03301593 obo:FOODON_03301635 obo:FOODON_03301641 obo:FOODON_03301697 obo:FOODON_03301701 obo:FOODON_03301702 obo:FOODON_03301704 obo:FOODON_03301713 obo:FOODON_03301716 obo:FOODON_03301719 obo:FOODON_03301722 obo:FOODON_03301724 obo:FOODON_03301727 obo:FOODON_03301773 obo:FOODON_03301813 obo:FOODON_03301830 obo:FOODON_03301831 obo:FOODON_03301833 obo:FOODON_03301977 obo:FOODON_03302045 obo:FOODON_03302116 obo:FOODON_03302458 obo:FOODON_03302727 obo:FOODON_03302732 obo:FOODON_03302776 obo:FOODON_03302908 obo:FOODON_03303085 obo:FOODON_03303222 obo:FOODON_03303380 obo:FOODON_03304006 obo:FOODON_03304595 obo:FOODON_03304639 obo:FOODON_03304640 obo:FOODON_03304656 obo:FOODON_03304707 obo:FOODON_03304859 obo:FOODON_03305208 obo:FOODON_03305236 obo:FOODON_03305237 obo:FOODON_03305263 obo:FOODON_03305317 obo:FOODON_03305656 obo:FOODON_03306581 obo:FOODON_03306632 obo:FOODON_03306811 obo:FOODON_03306893 obo:FOODON_03306944 obo:FOODON_03307119 obo:FOODON_03307294 obo:FOODON_03307458 obo:FOODON_03307633 obo:FOODON_03307770 obo:FOODON_03309709 obo:FOODON_03309832 obo:FOODON_03309855 obo:FOODON_03309858 obo:FOODON_03309927 obo:FOODON_03309954 obo:FOODON_03309985 obo:FOODON_03310193 obo:FOODON_03310357 obo:FOODON_03310387 obo:FOODON_03310547 obo:FOODON_03310635 obo:FOODON_03310641 obo:FOODON_03310709 obo:FOODON_03310775 obo:FOODON_03310815 obo:FOODON_03310858 obo:FOODON_03310943 obo:FOODON_03311095 obo:FOODON_03311146 obo:FOODON_03311349 obo:FOODON_03311513 obo:FOODON_03311604 obo:FOODON_03311663 obo:FOODON_03311757 obo:FOODON_03315081 obo:FOODON_03315145 obo:FOODON_03315513 obo:FOODON_03315904 obo:FOODON_03316061 obo:FOODON_03316114 obo:FOODON_03316636 obo:FOODON_03316694 obo:FOODON_03317365 obo:FOODON_03411005 obo:FOODON_03411136 obo:FOODON_03411161 obo:FOODON_03411236 obo:FOODON_03411324 obo:FOODON_03411374 obo:FOODON_03411462 obo:FOODON_03411512 obo:FOODON_03411558 obo:FOODON_03411566 obo:FOODON_03420108
				} 
				?entity rdfs:label ?label .
			}
		"""
}

if __name__ == '__main__':

	myontology = OntologyUpdate()
	myontology.__main__()

