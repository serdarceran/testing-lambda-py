
# A sample serverless function to test testing lambda functions

[![Build Status](https://travis-ci.org/joshuaballoch/testing-lambda-py.svg?branch=master)](https://travis-ci.org/joshuaballoch/testing-lambda-py)

## Installation

1. Create & Source the virtualenv

```
pip install virtualenv
virtualenv .venv -p python3 OR virtualenv .venv -p python
source .venv/bin/activate
```

2.  Install pip tools

```
pip3 install pip-tools
```

3. Install the development requirements

```
pip-compile --output-file requirements-dev.txt requirements/requirements-dev.in

pip install -r requirements-dev.txt
```

4. Run tests
```
pytest test*
```

5. Install serverless
```
npm install -g serverless
```

6. Deploy app
```
serverless deploy --stage=dev
```

7. Trace logs
```
serverless logs -f activity --stage=dev --tail
```
