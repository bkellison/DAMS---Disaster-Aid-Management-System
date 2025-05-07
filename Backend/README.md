# disaster_relief_py_project

## Python Disaster Relief Apis
This is a Python project used to connect to sql db and create restful apis that return stored procedures or run matching algorithm

## Description
Connects to local mysql db
Returns stored procedures
Runs matching algorithm

## Installation
Create Virtual Environment:
```bash
py -m venv .venv  #Create a virtual environment
source .venv/bin/activate  #(Mac/Linux) Activate the environment
.venv/Scripts/activate #(Windows) Activate the environment
```

Confirm pip is installed. If not:
```bash
py -m ensurepip --default-pip
```

Install Dependencies:
```bash
pip install -r requirements.txt
```

Update requirements.txt (installed new dependency):
```bash
pip freeze > requirements.txt
```


## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.
