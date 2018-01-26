import os
from operator import itemgetter
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import Article, Photo
import exifread


class Command(BaseCommand):
    """
    The script create a list of tuples (article_id, image_file).
    We start form the list of article_id-s.

    p = Photo()
    p.photo= 'articles/_D8B0003.jpg'
    p.article = Article.objects.get(pk=10)

    """
    help = 'Bind pictures to articles.'


    def handle(self, *args, **options):
        articles_with_multiple_pic = {141: 14, 142: 12, 143:6, 144:3, 145:3}
        articles = Article.objects.filter(entreprise = 2)
        print("Total articles: %s" % str(len(articles)))
        print("removing articles already paired...")
        photos = Photo.objects.all()
        exclude_photo_names = []
        exclude_count = 0
        current_article_id = 0
        for p in photos:
            if current_article_id != p.article.id:
                articles = articles.exclude(pk=p.article.id)
                print('excluding article-ID ', p.article.id)
                current_article_id = p.article.id
            else:
                print('always same article-id %s' % current_article_id)
            photo_file_name = p.photo.name.split('/')[1]
            print('will remove picture %s.' % photo_file_name)
            exclude_photo_names.append(photo_file_name)
            exclude_count += 1
        print("%s articles already paired and excluded from script." % exclude_count)
        print("Netto total of articles: ", len(articles))


        pictures_dir = os.path.join(settings.MEDIA_ROOT, 'articles')
        files = os.listdir(pictures_dir)
        date_pic = {}
        datetime_list = []
        nb = 0
        files_exclude_count = 0
        for f in files:
            nb += 1
            if f in exclude_photo_names:
                print('%s is in excluded pictures list. Continuing with the next file.' % f)
                files_exclude_count += 1
                continue

            absolute_path = os.path.join(pictures_dir, f)
            photo_file = open(absolute_path, 'rb')
            tags = exifread.process_file(photo_file, details=False, stop_tag="EXIF DateTimeOriginal", strict=True)
            dtexif = tags['EXIF DateTimeOriginal']
            s = str(dtexif)
            t = s.split(' ')
            u = ' '.join(t)
            dt = datetime.strptime(u, "%Y:%m:%d %H:%M:%S")
            datetime_list.append(dt)
            date_pic[dt] = os.path.join('articles', f)
        print("%s files analysed." % nb)
        print('excluded files: %s' % files_exclude_count)


        datetime_list.sort()
        print("Sorted.")
        # binding
        count = 0
        total = 150 # total of articles to handle
        for a, p in zip(articles, datetime_list):
            count += 1
            if a.id in articles_with_multiple_pic:
                print('article %s has %s pictures.' % (a.id, articles_with_multiple_pic[a.id]))
                print('Adding the pictures and stop...')
                p_index = datetime_list.index(p)
                print('Beginning with picture %s' % date_pic[p])
                print('index: %s, nb-pic: %s' % (p_index, articles_with_multiple_pic[a.id]))
                multiple_pic_count = 0
                for i in range(p_index, articles_with_multiple_pic[a.id]+p_index):
                    multiple_pic_count += 1
                    pp = datetime_list[i]
                    print('%s: Picture %s will be added to article %s.' % (multiple_pic_count, date_pic[pp], a.id))
                    p = Photo()
                    p.photo = date_pic[pp]
                    p.article = a
                    p.save()
                break # because another exclusion of those articles and their pcitures is required.

            # usual case of ONE article with ONE picture
            photo_name = date_pic[p]
            print(a.id, photo_name, p)
            p = Photo()
            p.photo = photo_name
            p.article = a
            p.save()
            if count >= total:
                break
        print("Pairing %s articles and pictures." % count)







