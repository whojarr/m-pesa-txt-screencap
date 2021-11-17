# m-pesa-txt-screencap

https://github.com/whojarr/m-pesa-txt-screencap/

Contact: David Hunter dhunter@digitalcreation.co.nz

Copyright (C) 2021 Digital Creation Ltd

For license information, see LICENSE


## Requires

serverless framework [https://www.serverless.com/](https://www.serverless.com/)

yarn [https://classic.yarnpkg.com/en/](https://classic.yarnpkg.com/en/)

python 3.8 (i use pyenv below to meet this requirement)

poetry [https://python-poetry.org/](https://python-poetry.org/)

pyenv [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv) (option to use the version in .python-version automatically)

## local dev

poetry install

poetry shell

sls wsgi serve -p 8000


## deploy

yarn install

setup the required parameters in System Manager Parameter Store

/m-pesa-txt-screencap/${self:provider.stage}/teams_url

/m-pesa-txt-screencap/${self:provider.stage}/apikey

/m-pesa-txt-screencap/${self:provider.stage}/domain_name 


e.g. /m-pesa-txt-screencap/dev/teams_url

e.g. /m-pesa-txt-screencap/someone/teams_url

sls create_domain (once per stage)

sls deploy

or 

AWS_PROFILE=someone sls deploy --stage someone

# TODO:

* Detect and handle other message types in addition to user_login

* Complete documentation for WP Webhooks configuration
