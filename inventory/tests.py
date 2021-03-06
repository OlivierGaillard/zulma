from django.test import TestCase, Client
from django.conf import settings
from .models import Article
import os
import glob
import shutil
from subprocess import PIPE, Popen
import subprocess
import zipfile
from PIL import Image
from zipfile import ZipInfo, ZipFile
import tempfile



# Create your tests here.
class TestInventory(TestCase):

    def setUp(self):
        self.tmp_dir = '/home/golivier/DjangoMusic/zulma/tmp'
        self.tmp_img = '/home/golivier/DjangoMusic/zulma/tmpimg/picsdir'
        self.zip_file_no_dir = 'testnodir.zip'
        self.zip_file__dir_name_nospace = 'picsdir.zip'
        self.zip_file__dir_name_with_space = 'pics dir.zip'
        self.zip_file_dir_name_with_zip_and_spaces = 'FOTOS COSAS DE CASA ZIP.zip'
        self.zip_file_kea = 'Kea 1.zip'
        self.big_zip_kea = 'kea.zip'

    def tearDown(self):
        for entry in os.scandir(self.tmp_dir):
            if entry.is_file() and (entry.name.endswith('.jpg') or entry.name.endswith('.db')):
                os.unlink(entry)
            if entry.is_dir():
                for e in os.scandir(entry):
                    if e.is_file() and e.name.endswith('.jpg'):
                        os.unlink(e)
                os.rmdir(entry)

    def _count_images(self, dirpath):
        images = []
        images_dir = os.path.join(self.tmp_dir, dirpath)
        with os.scandir(os.path.join(images_dir)) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.jpg'):
                    images.append(entry.name)
        return len(images)

    def test_unzip(self):
        """Test unzip files containing no directory"""
        zip_file_path =  os.path.join(self.tmp_dir, self.zip_file_no_dir)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
             zip_ref.extractall(self.tmp_dir)

        self.assertEqual(self._count_images('.'), 3)



    def test_unzip_dir(self):
        """Test unzip files containing directory"""
        zip_file_path = os.path.join(self.tmp_dir, self.zip_file__dir_name_nospace)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.tmp_dir)

        self.assertEqual(self._count_images('picsdir'), 3)

    def test_unzip_dir_space_name(self):
        """Test unzip files containing directory name with spaces"""
        zip_file_path = os.path.join(self.tmp_dir, self.zip_file__dir_name_with_space)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.tmp_dir)

        self.assertEqual(self._count_images('pics dir'), 3)

    def test_unzip_dir_space_name_zip(self):
        zip_file_path = os.path.join(self.tmp_dir, self.zip_file_dir_name_with_zip_and_spaces)
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.tmp_dir)

        self.assertEqual(self._count_images('FOTOS COSAS DE CASA ZIP'), 3)


    def test_unzip_walk(self):
        zip_file_path = os.path.join(self.tmp_dir, self.zip_file_kea)
        zipfile = ZipFile(zip_file_path)
        with tempfile.TemporaryDirectory() as tempdir:
            ZipFile.extractall(zipfile, path=tempdir)
            for dirpath, dirnames, filenames in os.walk(tempdir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    shutil.move(filepath, self.tmp_dir)

    def test_unzip_walk2(self):
        zip_file_path = os.path.join(self.tmp_dir, self.big_zip_kea)
        zipfile = ZipFile(zip_file_path)
        with tempfile.TemporaryDirectory() as tempdir:
            ZipFile.extractall(zipfile, path=tempdir)
            for dirpath, dirnames, filenames in os.walk(tempdir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    #ZipFile.extractall(filepath)

                for dirname in dirnames:
                    print('dirname:', dirname)


    def test_resize(self):
        dirpath = self.tmp_img
        os.chdir(dirpath)
        max_size = 100
        size = max_size
        for file in os.listdir('.'):
            size -= 10
            size_arg = "{0}%".format(size)
            #print(file, size_arg)
            subprocess.call(["mogrify", "-resize", size_arg,  file])





