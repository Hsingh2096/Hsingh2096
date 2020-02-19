# Load Errors
```
inserted new repos belonging to Spring-projects
inserted new repos belonging to GemXD
Traceback (most recent call last):
  File "gitim.py", line 110, in <module>
    gitim.clone_main()
  File "gitim.py", line 88, in clone_main
    get_repos = g.get_organization(args.org).get_repos if args.org else g.get_user().get_repos
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/MainClass.py", line 293, in get_organization
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 322, in requestJsonAndCheck
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 345, in __check
github.GithubException.UnknownObjectException: 404 {"message": "Not Found", "documentation_url": "https://developer.github.com/v3"}
Traceback (most recent call last):
  File "repoload.py", line 94, in <module>
    r.repos_main()
  File "repoload.py", line 78, in repos_main
    repos = self.get_repos(org, token)
  File "repoload.py", line 23, in get_repos
    result = subprocess.check_output(["python", "gitim.py", "-t", token, "-o", org])
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 395, in check_output
    **kwargs).stdout
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 487, in run
    output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['python', 'gitim.py', '-t', '7865b374905007623f693af31af272cb622564bc', '-o', 'orgs/gemfire']' returned non-zero exit status 1.
inserted new repos belonging to greenplum-db

inserted new repos belonging to spring-guides
inserted new repos belonging to SteeltoeOSS
inserted new repos belonging to Pivotal-DataFabric
inserted new repos belonging to Pivotal-Data-Engineering
inserted new repos belonging to cfmobile
inserted new repos belonging to pivotaltracker
Traceback (most recent call last):
  File "gitim.py", line 110, in <module>
    gitim.clone_main()
  File "gitim.py", line 88, in clone_main
    get_repos = g.get_organization(args.org).get_repos if args.org else g.get_user().get_repos
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/MainClass.py", line 293, in get_organization
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 322, in requestJsonAndCheck
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 345, in __check
github.GithubException.UnknownObjectException: 404 {"message": "Not Found", "documentation_url": "https://developer.github.com/v3"}
Traceback (most recent call last):
  File "repoload.py", line 94, in <module>
    r.repos_main()
  File "repoload.py", line 78, in repos_main
    repos = self.get_repos(org, token)
  File "repoload.py", line 23, in get_repos
    result = subprocess.check_output(["python", "gitim.py", "-t", token, "-o", org])
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 395, in check_output
    **kwargs).stdout
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 487, in run
    output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['python', 'gitim.py', '-t', '7865b374905007623f693af31af272cb622564bc', '-o', 'orgs/pivotal-cf']' returned non-zero exit status 1.
Traceback (most recent call last):
  File "gitim.py", line 110, in <module>
    gitim.clone_main()
  File "gitim.py", line 88, in clone_main
    get_repos = g.get_organization(args.org).get_repos if args.org else g.get_user().get_repos
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/MainClass.py", line 293, in get_organization
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 322, in requestJsonAndCheck
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 345, in __check
github.GithubException.UnknownObjectException: 404 {"message": "Not Found", "documentation_url": "https://developer.github.com/v3"}
Traceback (most recent call last):
  File "repoload.py", line 94, in <module>
    r.repos_main()
  File "repoload.py", line 78, in repos_main
    repos = self.get_repos(org, token)
  File "repoload.py", line 23, in get_repos
    result = subprocess.check_output(["python", "gitim.py", "-t", token, "-o", org])
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 395, in check_output
    **kwargs).stdout
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 487, in run
    output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['python', 'gitim.py', '-t', '7865b374905007623f693af31af272cb622564bc', '-o', 'orgs/pivotal-cf-experimental']' returned non-zero exit status 1.
inserted new repos belonging to pcfdev-forks
inserted new repos belonging to pivotal-cloudops
inserted new repos belonging to cf-platform-eng
inserted new repos belonging to platform-acceleration-lab
inserted new repos belonging to Pivotal-Field-Engineering
Traceback (most recent call last):
  File "gitim.py", line 110, in <module>
    gitim.clone_main()
  File "gitim.py", line 88, in clone_main
    get_repos = g.get_organization(args.org).get_repos if args.org else g.get_user().get_repos
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/MainClass.py", line 293, in get_organization
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 322, in requestJsonAndCheck
  File "/Users/sgoggins/github/virtualenvs/augur-data-utils/lib/python3.7/site-packages/PyGithub-1.45-py3.7.egg/github/Requester.py", line 345, in __check
github.GithubException.UnknownObjectException: 404 {"message": "Not Found", "documentation_url": "https://developer.github.com/v3/orgs/#get-an-organization"}
Traceback (most recent call last):
  File "repoload.py", line 94, in <module>
    r.repos_main()
  File "repoload.py", line 78, in repos_main
    repos = self.get_repos(org, token)
  File "repoload.py", line 23, in get_repos
    result = subprocess.check_output(["python", "gitim.py", "-t", token, "-o", org])
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 395, in check_output
    **kwargs).stdout
  File "/usr/local/Cellar/python/3.7.4_1/Frameworks/Python.framework/Versions/3.7/lib/python3.7/subprocess.py", line 487, in run
    output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['python', 'gitim.py', '-t', '7865b374905007623f693af31af272cb622564bc', '-o', 'pivotal-partner-solution-architecture']' returned non-zero exit status 1.

inserted new repos belonging to pivotalservices
inserted new repos belonging to pivotal
inserted new repos belonging to Pivotal-sg
inserted new repos belonging to pivotalsoftware
inserted new repos belonging to pivotal-education
inserted new repos belonging to pivotal-gss
inserted new repos belonging to appsuite
```