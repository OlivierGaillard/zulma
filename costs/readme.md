# Install


- run `python manage.py startapp costs`
- add `costs` to your apps settings
- run `makemigrations` and `migrate`
- add namespace to the main `urls.py`

## Deployment

To deploy with git it is cool, *prior* to make a
`git pull`, to delete the files `models.py`,
`admin.py` and so on: all the new updated files.

If not git will refuse to overwrite those files.




