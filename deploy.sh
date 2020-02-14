#!/bin/bash
# Automatically update the PDF on the pdf branch with Travis

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

# Exit on errors
set -o errexit -o nounset

# Begin
echo "Committing pdf..."

# Get git hash
rev=$(git rev-parse --short HEAD)

# Create orphan repo
cd $TRAVIS_BUILD_DIR
git checkout --orphan pdf
git rm -rf .
cp cv.test.pdf cv.JoaoFaria.pdf
git add -f cv.JoaoFaria.pdf
git -c user.name='travis' -c user.email='travis' commit -m "rebuild pdf at ${rev}"
git push -q -f https://$GITHUB_USER:$GITHUB_API_KEY@github.com/$TRAVIS_REPO_SLUG pdf