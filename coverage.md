#Coverage usage

1. First run coverage on the module: `coverage run manage.py test inventory`.
2. Generate report: `coverage html` with the files to exclude.

Exclude:

`--omit=/home/golivier/DjangoMusic/zulma/*/migrations/*,
	/home/golivier/DjangoMusic/.virtualenvs/*,
	*/admin.py,*/__init__.py,*/manage.py```
