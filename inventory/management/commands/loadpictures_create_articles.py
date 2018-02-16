import os
from operator import itemgetter
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import Article



class Command(BaseCommand):
    """
    The script read the pictures and create instances of 'ArticleBase'.
    """
    help = 'Load the pictures to create one instance of "ArticleBase" per picture.'


    def handle(self, *args, **options):
        pictures_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        target_dir = os.path.join(settings.MEDIA_ROOT, 'articles')
        files = os.listdir(pictures_dir)
        nb = 0
        for f in files:
            nb += 1
            print(f)
            source_path = os.path.join(pictures_dir, f)
            print('source path:', source_path)
            target_path = os.path.join(target_dir, f)
            print('target path:', target_path)
            a = ArticleBase(photo=os.path.join('articles', f))
            a.save()
            print('ArticleBase created.')
            print('Moving picture from tmp to articles...')
            os.rename(source_path, target_path)






