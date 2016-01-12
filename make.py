# -*- coding: utf-8 -*-
import os
import sys
import bibtexparser
from configfile import options


########################
# deal with the bib file
########################
with open('cv.complete.bib') as bibfile:
	database = bibtexparser.load(bibfile)

for k,v in database.entries_dict.items():
	full_author_list = v['author'].split('and')
	# find me
	my_name = next((x for x in full_author_list if 'Faria' in x), None)
	ind = full_author_list.index(my_name)

	if ind == 0:
		print 'first author'
		author_list = full_author_list[:ind+1]
		n_other_authors = len(full_author_list[ind+1:])
		author_list.append('{%d other authors}' % n_other_authors)
		author = ' and '.join(author_list)
	else:
		author_list = full_author_list[:ind+1]
		n_other_authors = len(full_author_list[ind+1:])
		# print ind, n_other_authors
		author_list.append('{%d other authors}' % n_other_authors)
		author = ' and '.join(author_list)

	database.entries_dict[k]['author'] = author

with open('cv.bib', 'w') as bibfile:
	bibfile.write(bibtexparser.dumps(database))


# sys.exit(0)

##################
# build the resume
##################

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
	                     interests=options['general']['interests'],
	                     degrees='\n\n'.join(degrees))



# put all { and } back
content = content.replace('### ', '{')
# replace all } by ##
content = content.replace('## ', '}')


with open('resume.test.tex', 'w') as f:
	print >>f, content

os.system('latexmk -xelatex -pdf --quiet resume.test.tex')
print 'Finished resume -- see %s' % 'resume.test.pdf'



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


degrees = []
for v in options['education-full'].values():
	exec 'data =' + v
	# print data
	degrees.append("\degree{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}".format(*data))

exec 'posters =' + options['posters']['list'].replace('\n', '')
exec 'talks =' + options['talks']['list'].replace('\n', '')

posters = {'P%d' % i: p for i,p in enumerate(posters)}
talks = {'T%d' % i: p for i,p in enumerate(talks)}

postersANDtalks = posters.copy()
postersANDtalks.update(talks)
PostersTalks = ['\item[%s] %s' % (i,s) for i, s in postersANDtalks.iteritems()]


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
	                     interests=options['general']['interests'],
	                     degrees='\n\n'.join(degrees),
	                     postersANDtalks='\n'.join(PostersTalks)
	                     )



# put all { and } back
content = content.replace('### ', '{')
# replace all } by ##
content = content.replace('## ', '}')


with open('cv.test.tex', 'w') as f:
	print >>f, content

os.system('latexmk -xelatex -pdf --quiet -f cv.test.tex')
print 'Finished cv -- see %s' % 'cv.test.pdf'