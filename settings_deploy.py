SERVICES = {
    "nginx":
        {
            "port": 27190,
            "start": ["nginx", "-c", "{project_dir}/nginx.conf"],
            "restart": ["kill", "-s", "SIGHUP", "{pid}"],
            "templates": ["nginx.conf.template"],
        },
    "gunicorn":
        {
            "port": 18650,
            "start": ["gunicorn", "-D", "-c", "settings_gunicorn.py", "yourapp.wsgi:application"],
            "restart": ["kill", "-s", "SIGHUP", "{pid}"],
        },
}

