#!/usr/bin/python
#

# Run like:
# >python ontofox_conversion.py fobi-edit.owl imports/chebi_ontofox.txt
#

import os
from collections import OrderedDict
import optparse
import sys
import re
import json

class OntofoxConvert(object):

	CODE_VERSION = '0.0.1'

	def __init__(self):
		pass

	def __main__(self):

		(options, args) = self.get_command_line()

		if options.code_version:
			print (self.CODE_VERSION)
			return self.CODE_VERSION

		if len(args) < 2:
			stop_err('Please supply an OWL ontology file (in RDF/XML format), and an Ontofox configuration file')

		ontology_file = os.path.abspath(args[0])
		if not (ontology_file and os.path.isfile(ontology_file)):
			stop_err('Unable to locate given OWL ontology file (in RDF/XML format):' + ontology_file)

		ontofox_file = os.path.abspath(args[1])
		if not (ontofox_file and os.path.isfile(ontofox_file)):
			stop_err('Unable to locate given OWL ontology file (in RDF/XML format):' + ontofox_file)

		with (open(ontology_file)) as ontology_handle:
			ontology = ontology_handle.read()

		lookup = OrderedDict()
		# Looks for Ontofox import lines like:
		# http://purl.obolibrary.org/obo/CHEBI_9629	 # FOBI:030717	tomatidine
		# where purl of imported term is followed by hash # and id to replace.
		regex = re.compile(r"(?P<domain>http:\/\/purl\.obolibrary\.org\/obo\/)(?P<id>[a-zA-Z]+_\d+)\s+#\s+(?P<oldid>[a-zA-Z]+_\d+)")
		# Process all terms in ontofox config file.  Comment is expected to contain
		# term to match.
		found = False;
		with (open(ontofox_file)) as ontofox_handle:
			ontofox_lines = ontofox_handle.readlines()
			for line in ontofox_lines:
				# Begin looking at terms here
				if line == '[Low level source term URIs]\n':
					found = True;
					continue
				if found == True:
					binding = regex.match(line)
					if binding:
						lookup[binding.group('oldid')] = binding.group('id')
						sr = re.compile('/'+binding.group('oldid') +'"')
						ontology = sr.sub('/' + binding.group('id') + '"', ontology)

				if line == '[Top level source term URIs and target direct superclass URIs]\n':
					break




		with (open('./test.owl', 'w')) as output_handle:
			output_handle.write(ontology)


	def get_command_line(self):
		"""
		*************************** Parse Command Line *****************************
		"""
		parser = MyParser(
			description = 'Ontology OWL file updater.  Updates .rdf/xml OWL\
			file to contain	all terms mentioned in an OntoFox configuration\
			file.  ID of new term expected to be in comment part following\
			ontofox term purl.',
			usage = 'ontofetch.py [ontology file path or URL] [options]*',
			epilog="""  """)
		
		# first (unnamed) parameter is input owl file
		# second parameter is ontofox configuration file.
		# output to stdio unless -o provided in which case its to a file.

		# Standard code version identifier.
		parser.add_option('-v', '--version', dest='code_version', default=False, action='store_true', help='Return version of this code.')

		parser.add_option('-o', '--output', dest='output_file', type='string', help='Path and file name of output file to create')
		
		return parser.parse_args()

def stop_err(msg, exit_code = 1):
	sys.stderr.write("%s\n" % msg)
	sys.exit(exit_code)


class MyParser(optparse.OptionParser):
	"""
	Allows formatted help info.  From http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output.
	"""
	def format_epilog(self, formatter):
		return self.epilog


if __name__ == '__main__':

	updater = OntofoxConvert()
	updater.__main__()  
