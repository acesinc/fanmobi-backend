fanmobi-backend
=========================
Backend RESTful API for FanMobi

## Geting Started
1. Install Python 3.4.3. Python can be installed by downloading the appropriate
    files [here](https://www.python.org/downloads/release/python-343/). Note
    that Python 3.4 includes both `pip` and `venv`, a built-in replacement
    for the `virtualenv` package
2. Create a new python environment using python 3.4.x. First, create a new
    directory where this environment will live, for example, in
    `~/python_envs/fanmobi`. Now create a new environment there:
    `python3.4 -m venv ENV` (where `ENV` is the path you used above)
3. Active the new environment: `source ENV/bin/activate`
4. Set Python 3.4 as default `alias python='~/py3env/bin/python3.4'`
5. Install Python development headers `sudo apt-get install python3-dev`
6. Install the necessary dependencies into this python environment:
    `pip install -r requirements.txt`
7. Run the server: `./restart_clean_dev_server.sh`

Swagger documentation for the api is available at `http://localhost:8000/docs/`
Use username `user` password `password` when prompted for authentication info
