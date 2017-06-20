# -*- coding: utf-8 -*-
import os
import sys
import re
import hashlib
import json
import bibtexparser
from configfile import options


### parse the command line arguments
import argparse
parser = argparse.ArgumentParser(description='Build and compile the CV and resumé PDFs.')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
parser.add_argument('--sign', action='store_true', help='Add date and signature to the document.')
parser.add_argument('--bib', action='store_true', help='Force recompilation of the bib file.')
parser.add_argument('--live', action='store_true', help='Live compilation.')

args = parser.parse_args()


### read file hashes
oldhashes = json.load(open('filehashes.dat'))

########################
# deal with the bib file
########################
oldhash = oldhashes['cv.complete.bib']
newhash = hashlib.md5(open('cv.complete.bib').read()).hexdigest()

if newhash != oldhash or args.bib: # do this only if the cv.complete.bib file has changed

	with open('cv.complete.bib') as bibfile:
		database = bibtexparser.load(bibfile)

	for k,v in database.entries_dict.items():
		full_author_list = v['author'].split('and')
		# find me
		my_name = next((x for x in full_author_list if 'Faria' in x), None)
		my_author_name = r'{Faria}, J.~P.'
		ind = full_author_list.index(my_name)

		author_list = full_author_list[:ind+1]
		n_other_authors = len(full_author_list[ind+1:])
		print ind, n_other_authors,
		print ind>3, author_list[0]

		if ind==0 and n_other_authors==1:
			# if first author with only 1 other author, don't change anything
			database.entries_dict[k]['author'] = ' and '.join(full_author_list)
			continue
		if ind>3:
			author_list = [full_author_list[0]]
			author_list.append('{%d authors}' % (ind-1))
			author_list.append(my_author_name)
			# author_list.append()

		author_list.append('{%d other authors}' % n_other_authors)
		author = ' and '.join(author_list)

		database.entries_dict[k]['author'] = author

	with open('cv.bib', 'w') as bibfile:
		bibfile.write(bibtexparser.dumps(database))

	print 'Finished parsing .bib files (%d entries).' % len(database.entries_dict)

	# update hash
	oldhashes['cv.complete.bib'] = newhash
	json.dump(oldhashes, open('filehashes.dat', 'w'))


###################
# metrics from ADS
###################
# oldhash = oldhashes['metrics.txt']
# newhash = hashlib.md5(open('metrics.txt').read()).hexdigest()

# if newhash != oldhash: # do this only if the metrics.txt file has changed
import plot_metrics
metrics = plot_metrics.main('.', 'pdf', orcid='0000-0002-6728-244X')
indicators = metrics['indicators refereed']



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


## add the signature at the top?
signature = ''
if args.sign:
	signature = '\\fancyhead[R]{\\today \\\\ \includegraphics[height=1.5\\baselineskip]{signature}}'


degrees = []
for v in options['education-full'].values():
	exec 'data =' + v
	# print data
	degrees.append("\degree{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}".format(*data))

exec 'posters =' + options['posters']['list'].replace('\n', '')
exec 'talks =' + options['talks']['list'].replace('\n', '')

posters = {'P%d' % (i+1): p for i,p in enumerate(posters)}
talks = {'T%d' % (i+1): p for i,p in enumerate(talks)}

postersANDtalks = posters.copy()
postersANDtalks.update(talks)

invited = options['talks']['invited']

pat = re.compile('\d{4}')
findyear = lambda s: int(re.findall(pat, s)[0])

pat2 = re.compile('Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec')
months = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
findmonth = lambda s: months[re.findall(pat2, s)[0]]

finddate = lambda s: (findyear(s), findmonth(s))


PostersTalks = ['\item[%s] %s' % (i,s) for i, s in postersANDtalks.iteritems()]
from operator import itemgetter
key = lambda s: itemgetter(0, 1)(finddate(s))
PostersTalks.sort(key=key, reverse=True)
# print PostersTalks

exec 'conferences =' + options['conferences']['list'].replace('\n', '')
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
	                     invited='', #invited,
	                     postersANDtalks='\n'.join(PostersTalks),
	                     conferences='\n'.join(conferences),
	                     signature=signature,
	                     )



# put all { and } back
content = content.replace('### ', '{')
# replace all } by ##
content = content.replace('## ', '}')


with open('cv.test.tex', 'w') as f:
	print >>f, content


if args.live: 
	live=' -pvc '
else:
	live = ''
if args.verbose:
	os.system('latexmk -xelatex -bibtex %s -f cv.test.tex' % live)
else:
	os.system('latexmk -xelatex -bibtex %s --quiet -f cv.test.tex' % live)
print 'Finished cv -- see %s' % 'cv.test.pdf'
import shutil
shutil.copy('cv.test.pdf', 'cvJoaoFaria.pdf')

if not args.live:
	os.system('/usr/bin/evince cv.test.pdf &')