# -*- coding: utf-8 -*-
import os

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


from configfile import options


# replace template fields
content = content.format(author=options['biographical']['name'],
	                     institute=options['biographical']['institute'],
	                     address=options['biographical']['address'],
	                     phone=options['biographical']['phone'],
	                     email=options['biographical']['email'],
	                     website=options['online']['website'],
	                     twitter=options['online']['twitter'],
	                     github=options['online']['github'],)



# put all { and } back
content = content.replace('### ', '{')
# replace all } by ##
content = content.replace('## ', '}')


with open('resume.test.tex', 'w') as f:
	print >>f, content

os.system('latexmk -xelatex -pdf resume.test.tex')