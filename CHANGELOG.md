1.8
---
- setup.py change to ensure we are using a compatible psutil version for
  previous change

1.7
---
- fix bug in detecting master process based on oldest pid

1.6
---
- fix issue finding the pid of processes with periods in their names (such as python2.7)

1.5
---
- update description for pypi and re-release

1.4
---
- fix a crash when a port-based process is not running and another process is outbound on that same port
