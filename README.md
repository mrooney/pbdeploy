pbdeploy
========

pbdeploy (port-based deploy) is a script that handles starting,
reloading and stopping your server processes, without requiring a
daemon or pidfiles.

It also supports running scripts before and after certain services are
loaded, such as installing requirements, performing database migrations,
and running tests, to make continuous deployment a breeze.

to install: `pip install pbdeploy`

usage
===
First, create a `settings_deploy.py` file anywhere in your project:

    SERVICES = {
        "django": {
                "port": 8000,
                "start": "python manage.py runserver",
        },
        "nginx": {
                "port": 8080,
                "start": "nginx -c {project_dir}/nginx.conf",
                "restart": "kill -s SIGHUP {pid}",
        },
    }
    
In this example, we run django and also nginx. `project_dir` and `pid`
are special variables that are always available, `project_dir` being the
directory containing `settings_deploy.py` and `pid` being the pid of the
process being managed.

Now, simply run `pbdeploy` from the same directory, and pbdeploy will
run the start command if there isn't a process listening on the
specified port, otherwise it will issue the restart command. If no
restart command is specified, in the case of Django, pbdeploy won't do
anything if the process is already running.

To stop your processes, run `pbdeploy stop`.

going further
===
Here's a more complex example that takes advantage of more of pbdeploy's
features. Notice how the file is just Python so we can add any special logic we want, in this case using an environment variable for Solr:

    import os
    SERVICES = {
    "nginx": {
            "port": 12818,
            "start": "nginx -c {project_dir}/nginx.conf",
            "restart": "kill -s SIGHUP {pid}",
            "templates": ["nginx.conf.template"],
        },
    "gunicorn": {
            "port": 25590,
            "start": "gunicorn -D -c settings_gunicorn.py yourapp.wsgi:application",
            "restart": "kill -s SIGHUP {pid}",
            "before": "pip install -r requirements.txt",
            "after": "manage.py syncdb --migrate ",
        },
    "solr": {
            "port": 28426,
            "start": "java -Djetty.port={port} -Djetty.pid={project_dir}/run/solr.pid -Dsolr.solr.home={project_dir}/../solr -jar","start.jar",
            "cwd": os.getenv("SOLR_EXAMPLE"),
            "daemonizes": False,
        },
    }
    

philosophy
===
pbdeploy's philosophy is:

1. to be a stateless script, not a persistent process like supervisor. This means it doesn't require extra background memory or CPU cycles, and isn't a process that itself needs to be monitored.
1. understanding that processes often run on specific ports, allowing us to bypass pid files and just ask the OS for the pid listening on that port. However, pbdeploy also handles pid files just fine.

Both of these make pbdeploy perfect for running on a shared server like
WebFaction where memory is limited and services are already bound to
specific ports, and it also works just swell anywhere from local development on
OSX to production deployment on EC2.

Parameters
===
* `start`: the command to run to start the process if it isn't already running.
* `restart`: the command  to run to restart the process if it is already running. If you leave this absent, pbdeploy won't do anything for this process if it is already running.
* `stop`: the command  to run to stop the process via `pbdeploy stop`. If you leave this blank, `kill {pid}` is assumed.
* `port`: the port that the process runs on. pbdeploy uses this to determine if the process is running or not and get its pid. you'll need to specify either this or `pidfile`.
* `pidfile`: if your process runs on a dynamic port, or already writes a pidfile that you'd prefer to use, you can specify the location here instead of a `port`.
* `cwd`: the directory to run the start/restart commands from. default: the directory where `pbdeploy` is run.
* `before`: a command to run before the service is started or restarted. For running multiple commands, put them in a script and specify that, as in the example above. This won't be run if you `pbdeploy --quick`.
* `after`: a command to run after the service is started or restarted. For running multiple commands, put them in a script and specify that, as in the example above. This won't be run if you `pbdeploy --quick`.
* `daemonizes`: by default pbdeploy will wait for the `start` command to
exit so it can report non-zero exit codes, but if you specify False,
pbdeploy will background this process instead, useful for processes that don't daemonize themselves.

Continuous Deployment
===
A great use for before and after scripts is to run idempotent commands so that `pbdeploy` handles everything necessary for continuous deployment.

For Django, a before script might be:

    pip install -r ../requirements.txt | egrep -v "(Requirement already satisfied|Cleaning up)" || true
    python manage.py collectstatic --noinput
    
and an after script might be:

    python manage.py syncdb --migrate
    python manage.py test yourapp 2>&1
    
an example git post-receive hook that runs all this and restarts your services for you on push might look like:

    unset GIT_DIR
    cd $YOUR_APP_DIR
    git pull
    source env/bin/activate
    pbdeploy

Templating
===
pbdeploy supports templating in commands as well as files. For example, notice how above for the gunicorn service we can specify the restart command using "{pid}". This is a special variable that is always available.

You can also specify a file to template, such as we do with nginx. When we specify `templates: ["nginx.conf.template"]`, for each start/restart, pbdeploy will read `nginx.conf.template` and replace variables using Python string formatting, writing it out as just `nginx.conf`.

Variables that exist for templating are:
* `{pid}`: the pid of the process, determined either by the process listening on the specified port or the pidfile specified
* `{project_dir}`: the absolute path of the directory pbdeploy was run from. This is especially useful for avoiding hard-coding paths in configuration files (like nginx.conf) that require absolute paths.
* any parameter specified such as port/cwd/before/after, as well as
arbitrary parameters you can choose to add yourself. This is quite
powerful as you can dynamically compute / look up a value in
settings_deploy.py that will end up in your service's otherwise static config file on each start or restart.
