from pl_download.models import DataFileManager
import unittest


class UnitTestDownloader(unittest.TestCase):
    def setUp(self):
        result = None

    def testWaveWatchDownload(self):
        print "Running Wave Watch Download Test: "
        result = DataFileManager.get_latest_wave_watch_files()
        self.assertIsNotNone(result)

    def testFetchingFiles(self):
        print "Running Currents & SS Temperature Download Test: "
        result = DataFileManager.fetch_new_files()
        self.assertIsNotNone(result)