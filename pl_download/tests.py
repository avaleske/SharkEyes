from django.test import TestCase
from pl_download.models import check_for_new_file


class TestDownloader(TestCase):
    def setUp(self):
        None

    def test_check_for_new_file(self):
        check_for_new_file()