# Instruction

Need to install Python3.x beforehand

### Install python and libs

install python
```bash
sudo yum install centos-release-scl
sudo yum install rh-python36
python --version
yum install scl-utils
scl enable rh-python36 bash
```

```bash
yum -y install mysql-devel
```

version specific
```bash
yum -y install python-devel
yum -y install python36-devel
```

only if you don't have gcc and complain during an install process
```bash
yum install gcc
```

### Installing Pipenv
```bash
pip3 install pipenv
```

### Installing Dependencies

Make sure that you're in the project's root directory (the same one in which the `Pipfile` resides), and then run,

```bash
pipenv install --dev
```

### Initial Setup

1. Modify ElasticSearch and MySQL connection info in `config.yml`
2. Run script `pipenv run python setup.py`
3. Run process `pipenv run python process.py`
