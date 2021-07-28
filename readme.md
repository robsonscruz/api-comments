## Install dependencies
```bash
$ python -m pip install -r requirements.txt
```

## Set env
```bash
export MONGODB_URL="mongodb+srv://user:passwd@address-server-mongodb/database?retryWrites=true&w=majority"
export MONGODB_DB="db_project"
```

## Run app
```bash
$ gunicorn --log-level debug api:app
```

