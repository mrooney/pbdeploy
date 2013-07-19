pbdeploy
========

pbdeploy (port-based deploy) is a script for simplifying the (continuous) deployment of your application, including starting/restarting/stopping processes, as well as handling pre/post steps like installing requirements, running database migrations, and running tests.

to install: `pip install pbdeploy`

usage
===
Simply run `pbdeploy` from any directory you place a `settings_deploy.py` file in, documented below.

You can run `pbdeploy --quick` to skip running before/after scripts, and `pbdeploy stop` to stop any services managed by pbdeploy.

philosophy
===
pbdeploy's philosophy is:

1. to be a script, not a persistent process like supervisor. This means it doesn't require extra background memory or CPU cycles, and isn't a process that itself needs to be monitored.
1. to understand that processes often run on specific ports, allowing us to bypass pid files and just ask the OS for the pid listening on that port. However, pbdeploy also handles pid files just fine.

Both of these make pbdeploy perfect for running on a shared server like WebFaction where memory is limited services are already bound to specific ports, however it also works just as well for local development on OSX or production deployment on AWS.

getting started
===
You'll just need to create a `settings_deploy.py` in whichever directory you plan to run `pbdeploy` from.

This file will contain a short definition of each process to handle. Here's a simple example:

    SERVICES = {
        "django": {
                "port": 8000,
                "start": "python manage.py runserver",
        }
    }
    
In this simple Django example, we just specify a name, and the port and start command. With this settings_deploy.py file in place, we can just run `pbdeploy` from this directory, and if it doesn't see a process already listening on port 8000, it will run the start command.

Here's a more complex example involving multiple services. Notice how the file is just Python so we can add any special logic we want, in this case using an environment variable for Solr:

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
            "before": "./before_deploy.sh",
            "start": "gunicorn -D -c settings_gunicorn.py yourapp.wsgi:application",
            "restart": "kill -s SIGHUP {pid}",
            "after": "./after_deploy.sh",
        },
    "solr": {
            "port": 28426,
            "start": "java -Djetty.port={port} -Djetty.pid={project_dir}/run/solr.pid -Dsolr.solr.home={project_dir}/../solr -jar","start.jar",
            "cwd": os.getenv("SOLR_EXAMPLE"),
            "daemonizes": False,
        },
    }
    
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
* `daemonizes`: by default pbdeploy will wait for the `start` command to exit so it can report non-zero exit codes, but if you specify False, pbdeploy will background this process instead, useful for process that don't daemonize themselves.

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
* any parameter specified such as port/cwd/before/after, as well as arbitrary parameters you can choose to add yourself. This is quite powerful as you can dynamically compute / look up a value in settings_deploy.py that will end up in your service's typically config file on each start or restart.
