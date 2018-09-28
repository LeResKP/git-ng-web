#!/usr/bin/env sh


VERSION=0.0.1-alpha.2


virtualenv env
env/bin/pip install -r "https://raw.githubusercontent.com/LeResKP/git-ng-web/$VERSION/requirements.txt"
env/bin/pip install "git+https://github.com/LeResKP/git-ng-web.git@$VERSION"

wget "https://raw.githubusercontent.com/LeResKP/git-ng-web/$VERSION/production.ini"
wget "https://raw.githubusercontent.com/LeResKP/git-ng-web/$VERSION/scripts/git_ng_web.sh"
chmod +x git_ng_web.sh

wget "https://github.com/LeResKP/git-ng-web/releases/download/$VERSION/angular-git-ng-web-$VERSION.zip"
mkdir static
unzip "angular-git-ng-web-$VERSION.zip" -d static/
