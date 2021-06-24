# Usd-Bitcoin-Exchange-Mock

- Create Virtual Environment - `virtualenv .venv`
- Activate Virtual Environment - `source .venv/bin/activate`
- Install required libaries - `pip install -r requirements.txt`
- rename .envexample to .env - `mv .envexmaple .env` or you can do it manually
- run server = `uvicorn main:app --reload`

This isn't a full fledge API/ Microservice as it Authentication or any form of security added.
It is was created a teaching material to help teach or show how detailed logging (Log tracing can be performed).
Most importantly introduce FastApi
