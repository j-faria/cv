#!/bin/bash
# Update the online rendering at http://j-faria.github.io/cv with Travis

# Exit on errors
set -o errexit -o nounset

alias pdf2htmlEX='docker run -ti --rm -v `pwd`:/pdf bwits/pdf2htmlex pdf2htmlEX'

# Begin
echo "Updating online page..."

# Get git hash
# rev=$(git rev-parse --short HEAD)

cd $TRAVIS_BUILD_DIR
git checkout gh-pages
pdf2htmlEX --zoom 1.3 --embed-outline 0 cv.test.pdf
git add -f cv.test.html
git -c user.name='travis' -c user.email='travis' commit -m "rebuild html, `date`"
git push -q -f https://$GITHUB_USER:$GITHUB_API_KEY@github.com/$TRAVIS_REPO_SLUG gh-pages