# Setup Python Dev Environment
Using some version of Python different than system version.
In this example
* Develop in Python 3.11
* Dev path: ~/swdev/python/my_python_project (<dev_dir> below)
* Python virtual env name: my_project_project (<venv_name> below)

1. Install Python: `sudo apt install python3.11`
2. Needed to install Python venv: `sudo apt install python3.11-venv`
3. Go to dev directory: e.g: `swDev/python/<dev_dir>`
4. Created virtual environment: `python3.11 -m venv <venv_name> .`
	Note the '.' at end creates the venv in the current dir.
5. Create activate link for easier access `ln -s <dir_path>/bin/activate <dir_path> activate`
6. Activate venv: `. ./activate`

## Record installed packages
* Create requirements.txt to document installed packages
	1. Activate venv: `. ./activate`
	2. pip freeze > requirements.txt

## Install packages using requirements.txt
* Use requirements.txt to install pacakges
	1. Activate venv: `. ./activate`
	2. pip install -r requirements.txt

