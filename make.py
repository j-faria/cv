# -*- coding: utf-8 -*-
import os
import sys
import re
import hashlib
import json
import bibtexparser
import configparser

class iniReader(configparser.ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

cfg = iniReader()
filename = 'info.ini'
cfg.read(filename)
options = cfg.as_dict()
# options is a dictionary -> access variables like options[section][parameter]


### parse the command line arguments
import argparse
parser = argparse.ArgumentParser(description='Build and compile the CV and resumé PDFs.')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
parser.add_argument('--sign', action='store_true', help='Add date and signature to the document.')
parser.add_argument('--bib', action='store_true', help='Force recompilation of the bib file.')
parser.add_argument('--live', action='store_true', help='Live compilation.')
parser.add_argument('--no-view', action='store_true', help='View the generated pdf.')
parser.add_argument('--no-latexmk', action='store_true', help='Compile with xelatex itself.')
parser.add_argument('--no-compile', action='store_true', help='Do not compile the LaTeX file.')
parser.add_argument('--no-page-number', action='store_true', help='Do not include page numbers.')

args = parser.parse_args()


### read file hashes
try:
	oldhashes = json.load(open('filehashes.dat'))
	oldhash = oldhashes['cv.complete.bib']
	newhash = hashlib.md5(open('cv.complete.bib').read().encode()).hexdigest()
except IOError:
	oldhashes = {}
	oldhash = 'a'
	newhash = 'b'
	
########################
# deal with the bib file
########################

if newhash != oldhash or args.bib: # do this only if the cv.complete.bib file has changed
	print('Doing bib stuff!')

	with open('cv.complete.bib') as bibfile:
		database = bibtexparser.load(bibfile)

	for k,v in list(database.entries_dict.items()):
		full_author_list = v['author'].split('and')
		# find me
		my_name = next((x for x in full_author_list if 'Faria' in x), None)
		my_bib_name = r'Faria, J.~P.'
		ind = full_author_list.index(my_name)
		full_author_list = [my_bib_name if ('Faria' in a) else a for a in full_author_list]

		author_list = full_author_list[:ind+1]
		n_other_authors = len(full_author_list[ind+1:])
		print(ind, n_other_authors, end=' ')
		print(ind>3, author_list[0]) #, author_list

		if ind==0 and n_other_authors==1:
			# if first author with only 1 other author, don't change anything
			database.entries_dict[k]['author'] = ' and '.join(full_author_list)
			continue
		elif ind==1 and (n_other_authors in (0,1)):
			# if second author and no other authors or 1 other, don't change anything
			database.entries_dict[k]['author'] = ' and '.join(full_author_list)
			continue
		elif ind>3:
			author_list = [full_author_list[0]]
			author_list.append('{%d authors}' % (ind-1))
			author_list.append(my_bib_name)

		if n_other_authors >1:
			author_list.append('{%d other authors}' % n_other_authors)
		author = ' and '.join(author_list)

		database.entries_dict[k]['author'] = author

	with open('cv.bib', 'w') as bibfile:
		bibfile.write(bibtexparser.dumps(database))

	print('Finished parsing .bib files (%d entries).' % len(database.entries_dict))

	# update hash
	oldhashes['cv.complete.bib'] = newhash
	json.dump(oldhashes, open('filehashes.dat', 'w'))


###################
# metrics from ADS
###################
import plot_metrics
# oldhash = oldhashes['metrics.txt']
# newhash = hashlib.md5(open('metrics.txt').read()).hexdigest()
# if newhash != oldhash: # do this only if the metrics.txt file has changed
# metrics = plot_metrics.main('.', 'pdf', orcid='0000-0002-6728-244X')
# metrics = plot_metrics.main('.', 'pdf', query='author:"Faria, J. P."  database:"astronomy"')
# indicators = metrics['indicators refereed']


# print args
# sys.exit(0)

##################
# build the resume
##################

"""
	# read the template file
	with open('resume.template.tex') as f:
		content = f.read()

	# replace all { by ###
	content = content.replace('{', '### ')
	# replace all } by ##
	content = content.replace('}', '## ')


	# replace all *** with {
	content = content.replace('***', '{')
	# replace all ** with }
	content = content.replace('**', '}')


	degrees = []
	for v in options['education'].values():
		exec 'data =' + v
		# print data
		degrees.append("\degree{{{}}}{{{}}}{{{}}}{{{}}}".format(*data))

	# print '\n\n'.join(degrees)




	# sys.exit(0)

	# replace template fields
	content = content.format(author=options['biographical']['name'],
		                     institute=options['biographical']['institute'],
		                     address=options['biographical']['address'],
		                     phone=options['biographical']['phone'],
		                     email=options['biographical']['email'],
		                     website=options['online']['website'],
		                     twitter=options['online']['twitter'],
		                     github=options['online']['github'],
		                     interests=options['general']['interests'].strip('"'),
		                     degrees='\n\n'.join(degrees))



	# put all { and } back
	content = content.replace('### ', '{')
	# replace all } by ##
	content = content.replace('## ', '}')


	with open('resume.test.tex', 'w') as f:
		print >>f, content

	os.system('latexmk -xelatex -pdf --quiet resume.test.tex')
	print 'Finished resume -- see %s' % 'resume.test.pdf'
	print 
"""

##############
# build the cv
##############

# read the template file
with open('cv.tex') as f:
	content = f.read()

# replace all { by ###
content = content.replace('{', '### ')
# replace all } by ##
content = content.replace('}', '## ')


# replace all *** with {
content = content.replace('***', '{')
# replace all ** with }
content = content.replace('**', '}')


## helper functions
patt = re.compile('\d{4}')
findyear = lambda s: int(re.findall(patt, s)[0])

pat2 = re.compile('Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec')
months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
findmonth = lambda s: months[re.findall(pat2, s)[0]]
finddate = lambda s: (findyear(s), findmonth(s))



## add the signature at the top?
signature = ''
if args.sign:
	signature = '\\fancyhead[R]{\\today \\\\ \includegraphics[height=1.5\\baselineskip]{signature}}'


## should we add page numbers?
if args.no_page_number:
	PageStyle1 = r'\pagestyle{empty}'
	PageStyle2 = r'\thispagestyle{last-page-no-number}'
else:
	PageStyle1 = r'\pagestyle{default}'+'\n'+r'\thispagestyle{firststyle}'
	PageStyle2 = r'\thispagestyle{last-page}'


degrees = []
for v in list(options['education-full'].values()):
	exec('data =' + v)
	degrees.append("\degree{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}".format(*data))


exec('posters =' + options['posters']['list'].replace('\n', ''))
exec('talks =' + options['talks']['list'].replace('\n', ''))
exec('invited =' + options['talks']['invited'].replace('\n', ''))

posters = {'P%d' % (i+1): p for i,p in enumerate(posters)}
talks = {'T%d' % (i+1): p for i,p in enumerate(talks)}

postersANDtalks = posters.copy()
postersANDtalks.update(talks)

PostersTalks = ['\item[%s] %s' % (i,s) for i, s in postersANDtalks.items()]
from operator import itemgetter
key = lambda s: itemgetter(0, 1)(finddate(s))
PostersTalks.sort(key=key, reverse=True)
# print PostersTalks

invited = ['\item[] %s' % s for s in invited]

exec('conferences =' + options['conferences']['list'].replace('\n', ''))
conferences = ['\item ' + s for s in conferences]


# replace template fields
content = content.format(author=options['biographical']['name'],
	                     institute=options['biographical']['institute'],
	                     address=options['biographical']['address'],
	                     phone=options['biographical']['phone'],
	                     email=options['biographical']['email'],
	                     website=options['online']['website'],
	                     websiteescaped=options['online']['website'].replace('{\\textasciitilde}', '~'),
	                     twitter=options['online']['twitter'],
	                     github=options['online']['github'],
	                     orcid=options['online']['orcid'],
	                     interests=options['general']['interests'].strip('"'),
	                     degrees='\n\n'.join(degrees),
	                     invited='\n'.join(invited),
	                     postersANDtalks='\n'.join(PostersTalks),
	                     conferences='\n'.join(conferences),
	                     signature=signature,
	                     PageStyle1=PageStyle1,
	                     PageStyle2=PageStyle2,
	                     )



# put all { and } back
content = content.replace('### ', '{')
# replace all } by ##
content = content.replace('## ', '}')


with open('cv.test.tex', 'w') as f:
	print(content, file=f)

if args.no_compile:
	sys.exit(0)


if args.no_latexmk:
	os.system('xelatex -halt-on-error cv.test.tex')
	os.system('bibtex cv.test.aux')
	os.system('xelatex -halt-on-error cv.test.tex')
	os.system('xelatex -halt-on-error cv.test.tex')
else:
	if args.live: 
		live=' -pvc '
	else:
		live = ''
	if args.verbose:
		os.system('latexmk -xelatex -bibtex %s -f cv.test.tex' % live)
	else:
		os.system('latexmk -xelatex -bibtex %s --quiet -f cv.test.tex' % live)


print('Finished cv -- see %s' % 'cv.test.pdf')

import shutil
shutil.copy('cv.test.pdf', 'cvJoaoFaria.pdf')

if not args.no_view and not args.live:
	os.system('/usr/bin/evince cv.test.pdf &')