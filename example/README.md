# django_userdefinedtables Example
This section of code may be pulled down separately from the rest of the codebase, or along with it.
After it is pulled down locally, it can be run with or without Docker:

## With Docker
Key the following in your command line from this directory:

```bash
docker build -t django_userdefinedtables .
docker run -p 8001:8000 django_userdefinedtables
```

After the build is complete and the app is running, navigate to http://localhost:8001 in a browser window.
You should see a