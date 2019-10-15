# Instruction

Need to install Python3.x beforehand

### Install python and libs

```bash
yum -y install python-devel mysql-devel
```

```bash
sudo yum install centos-release-scl
sudo yum install rh-python36
python --version
yum install scl-utils
scl enable rh-python36 bash
```

### Installing Pipenv
```bash
pip3 install pipenv
```

### Installing this Projects' Dependencies

Make sure that you're in the project's root directory (the same one in which the `Pipfile` resides), and then run,

```bash
pipenv install --dev
```

### Initial Setup

1. Modify ElasticSearch and MySQL connection info in `config.yml`
2. Run script `pipenv run python setup.py`
3. Run process `pipenv run python process.py`
