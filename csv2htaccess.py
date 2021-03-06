#!/usr/bin/env python3

import argparse
import sys
import urllib.parse
from pprint import pprint


def main(args:argparse.Namespace):

	lines = getCsvLines(args.inputfile, args.encoding)
	code = int(args.redirectcode)
	outfile = False

	for l in lines:

		if not outfile:
			# Run the iterator before creating the output file
			outfile = getOutputFile(args.outputfile, args.inputfile, args.encoding)

		l = urllib.parse.unquote(l).strip()
		parts = l.split(",")

		if len(parts)!=2 or parts[1].strip()=='':
			continue

		old = parts[0].strip()
		new = parts[1].strip()

		outline = parseCsvLine(code, args.urlencode, old, new)
		outfile.write(outline + "\n")


	outfile.close()
	return True



def getCsvLines(filename:str, encoding:str):

	try:
		with open(filename, mode='r', encoding=encoding) as lines:
			for line in lines:
				yield line

	except FileNotFoundError:
		print('Input file "' + filename + '" not found.')
		sys.exit(-1)



def getOutputFile(filename:str, filename_in:str, encoding:str):

	if filename=='':
		filename_out = filename_in + '.htaccess'

	else:
		filename_out = filename

	outfile = open(filename_out, mode='w', encoding=encoding)

	return outfile



def parseCsvLine(code:int, urlencode:bool, old:str, new:str):

	old_parts = urllib.parse.urlparse(old)
	path = old_parts.path
	qs = urllib.parse.parse_qsl(old_parts.query)

	if parseCsvLine.previousQS:
		prevNewLine = "\n"
	else:
		prevNewLine = ""

	if len(qs)==0:
		parseCsvLine.previousQS = False
		return prevNewLine + parsePath(code, urlencode, old, new)

	parseCsvLine.previousQS = True
	return parseQueryString(code, urlencode, path, qs, new)

parseCsvLine.previousQS = False



def parseQueryString(code:int, urlencode:bool, path:str, qs:list, new:str):

	template = """
RewriteCond %%{REQUEST_URI}  ^%s$ [NC]%s
RewriteRule ^(.*)$ "%s" [R=%d,L]"""

	qs_cond_template = "\nRewriteCond %%{QUERY_STRING} %s=%s [NC]"
	qs_conditions = ""

	for q in qs:
		k = q[0]
		v = q[1]
		if urlencode:
			k = urllib.parse.quote(k)
			v = urllib.parse.quote(v)
		qs_conditions+= qs_cond_template % (k, v)

	if urlencode:
		path = urllib.parse.quote(path)
		new = urllib.parse.quote(new)

	return template % (path, qs_conditions, new, code)



def parsePath(code:int, urlencode:bool, old:str, new:str):

	template = "Redirect %d %s %s"

	if urlencode:
		old = urllib.parse.quote(old)
		new = urllib.parse.quote(new)

	return template % (code, old, new)



if __name__=="__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument('inputfile', help='CSV file used as import data')
	parser.add_argument('outputfile', nargs='?', default='', help='Filename to be used for .htaccess output.')
	parser.add_argument('-e', '--encoding', default='utf-8', help='Character encoding to use for input and output files.')
	parser.add_argument('-r', '--redirectcode', default='302', help='HTTP Status Code to use for redirects.')
	parser.add_argument('-u', '--urlencode', action='store_true', help='URL-encode output URLs.')

	args = parser.parse_args()
	main(args)
