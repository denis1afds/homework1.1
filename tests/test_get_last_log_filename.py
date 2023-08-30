from unittest import TestCase, main
from LogAnalyzer import gen_match_files, get_last_filename, get_source_destination_filenames
import os
import re
from datetime import date
from unittest.mock import patch


class TestGetLastLogFileName(TestCase):
    test_log_dir = os.path.abspath('./data/tests/log')
    test_log_empty_dir = os.path.abspath('./data/tests/log/empty')
    test_invalid_dates_log_files_dir = os.path.abspath('./data/tests/log/invalid_date')

    test_report_dir = os.path.abspath('./data/tests/report')
    test_report_dir_with_late_date = os.path.abspath('./data/tests/report/late_date')

    test_valid_log_set = {('nginx-access-ui.log-20170630.log', date(2017, 6, 30)),
                          ('nginx-access-ui.log-20170701.log', date(2017, 7, 1)),
                          ('nginx-access-ui.log-20170629.log', date(2017, 6, 29)),
                          ('nginx-access-ui.log-20170628.log', date(2017, 6, 28)),
                          ('nginx-access-ui.log-20170627.log', date(2017, 6, 27)),
                          ('nginx-access-ui.log-20170626.log', date(2017, 6, 26)),
                          ('nginx-access-ui.log-20170625.log', date(2017, 6, 25)),
                          ('nginx-access-ui.log-20170624.log', date(2017, 6, 24)),
                          ('nginx-access-ui.log-20170623.log', date(2017, 6, 23)),
                          ('nginx-access-ui.log-20170122.log', date(2017, 1, 22)),
                          }

    test_invalid_log_set = {'nginx-access-ui.log-201730.log',
                            'nginx-access-ui.log-20170701.txt',
                            'nginx-access-ui.log',
                            'nu pogodi.avi',
                            'nginx-access-ui.log-27.log',
                            'log-20170626.log',
                            'apache-access-ui.log-20170625.log',
                            'isa-access-ui.log-20170624.log',
                            'access-ui.log-20170623.log',
                            'log-20170623.log',
                            }

    test_log_files_with_incorrect_date_suffix_set = {
        'nginx-access-ui.log-20170632.log',
        'nginx-access-ui.log-20171730.log',
        'nginx-access-ui.log-20170030.log'
    }

    test_valid_report_set = {
        'report-2017.06.01.html', 'report-2017.06.02.html', 'report-2017.06.03.html'}

    test_valid_report_with_late_date_set = {
        'report-2017.06.01.html', 'report-2017.06.02.html', 'report-2017.07.02.html'}

    log_filename_template = r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$"
    log_filename_regexp = None
    test_valid_filename_log_set = None

    report_filename_template = r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$"
    report_filename_regexp = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_valid_filename_log_set = set(filename for filename, _ in cls.test_valid_log_set)
        cls.log_filename_regexp = re.compile(cls.log_filename_template)
        cls.report_filename_regexp = re.compile(cls.report_filename_template)

# create path dir for contain empty log files with valid names
        if not os.path.exists(cls.test_log_dir):
            os.mkdir(cls.test_log_dir)
        log_filename_set = {filename for filename in os.listdir(cls.test_log_dir)}
        log_filename_for_test_set = cls.test_valid_filename_log_set.\
            union(cls.test_invalid_log_set).difference(log_filename_set)
        for filename_create in log_filename_for_test_set:
            empty_file = open(os.path.join(cls.test_log_dir, filename_create), mode='w')
            empty_file.close()

# create empty directory
        if not os.path.exists(cls.test_log_empty_dir):
            os.mkdir(cls.test_log_empty_dir)

# create dir with incorrect date suffix files
        if not os.path.exists(cls.test_invalid_dates_log_files_dir):
            os.mkdir(cls.test_invalid_dates_log_files_dir)
        for filename_create in cls.test_log_files_with_incorrect_date_suffix_set:
            empty_file = open(os.path.join(cls.test_invalid_dates_log_files_dir,
                                           filename_create), mode='w')
            empty_file.close()

# create path dir for contain empty report files with valid names
        if not os.path.exists(cls.test_report_dir):
            os.mkdir(cls.test_report_dir)
        report_filename_set = {filename for filename in os.listdir(cls.test_report_dir)}
        report_filename_for_test_set = cls.test_valid_report_set.difference(report_filename_set)
        for filename_create in report_filename_for_test_set:
            empty_file = open(os.path.join(cls.test_report_dir, filename_create), mode='w')
            empty_file.close()

# create path dir for contain empty report files with late date
        if not os.path.exists(cls.test_report_dir_with_late_date):
            os.mkdir(cls.test_report_dir_with_late_date)
        report_filename_set = {filename for filename
                               in os.listdir(cls.test_report_dir_with_late_date)}
        report_filename_for_test_set = cls.test_valid_report_with_late_date_set\
            .difference(report_filename_set)
        for filename_create in report_filename_for_test_set:
            empty_file = open(os.path.join(cls.test_report_dir_with_late_date,
                                           filename_create), mode='w')
            empty_file.close()

    @classmethod
    def tearDownClass(cls) -> None:
        # clean logs
        if os.path.exists(cls.test_log_dir):
            for path, _, file_list in os.walk(cls.test_log_dir):
                for filename in file_list:
                    os.remove(os.path.join(path, filename))
        os.rmdir(cls.test_invalid_dates_log_files_dir)
        os.rmdir(cls.test_log_empty_dir)
        os.rmdir(cls.test_log_dir)
        # clean reports
        if os.path.exists(cls.test_report_dir_with_late_date):
            for path, _, file_list in os.walk(cls.test_report_dir_with_late_date):
                for filename in file_list:
                    os.remove(os.path.join(path, filename))
        os.rmdir(cls.test_report_dir_with_late_date)

        if os.path.exists(cls.test_report_dir):
            for path, _, file_list in os.walk(cls.test_report_dir):
                for filename in file_list:
                    os.remove(os.path.join(path, filename))
        os.rmdir(cls.test_report_dir)

    def test_gen_match_log_files(self):
        for filename, file_suffix_date in gen_match_files(self.__class__.test_log_dir,
                                                          self.__class__.log_filename_regexp,
                                                          '%Y%m%d'):
            self.assertIn((os.path.split(filename)[1],  file_suffix_date),
                          self.__class__.test_valid_log_set)

    def test_gen_match_log_files_reverse(self):
        log_files_list = [os.path.split(filename)[1] for filename, _ in
                          gen_match_files(self.__class__.test_log_dir,
                                          self.__class__.log_filename_regexp,
                                          '%Y%m%d')]
        for filename, _ in self.__class__.test_valid_log_set:
            self.assertIn(filename, log_files_list)

    def test_gen_match_report_files(self):
        for filename, file_suffix_date in gen_match_files(self.__class__.test_report_dir,
                                                          self.__class__.report_filename_regexp,
                                                          '%Y.%m.%d'):
            self.assertIn(os.path.split(filename)[1], self.__class__.test_valid_report_set)

    def test_gen_no_match_files(self):
        for filename, _ in gen_match_files(self.__class__.test_log_dir,
                                           self.__class__.log_filename_regexp,
                                           '%Y%m%d'):
            self.assertFalse((os.path.split(filename)[1])
                             in self.__class__.test_invalid_log_set)

    def test_gen_no_match_files_from_empty_dir(self):
        for filename, _ in gen_match_files(self.__class__.test_log_empty_dir,
                                           self.__class__.log_filename_regexp,
                                           '%Y%m%d'):
            self.assertTrue(False)

    def test_gen_no_match_files_from_incorrect_date_suffix_dir(self):
        with patch('LogAnalyzer.logging.error') as mock_logging:
            for filename, _ in gen_match_files(
                    self.__class__.test_invalid_dates_log_files_dir,
                    self.__class__.log_filename_regexp,
                    '%Y%m%d'):
                pass
            mock_logging.assert_called()

    def test_get_last_filename(self):
        (filename, file_date) = get_last_filename(self.__class__.test_log_dir,
                                                  self.__class__.log_filename_regexp, '%Y%m%d')
        self.assertEqual(filename, os.path.join(self.__class__.test_log_dir,
                                                'nginx-access-ui.log-20170701.log'))
        self.assertEqual(file_date, date(2017, 7, 1))

    def test_get_last_filename_from_empty_dir(self):
        (filename, file_date) = get_last_filename(self.__class__.test_log_empty_dir,
                                                  self.__class__.log_filename_regexp, '%Y%m%d')
        self.assertIsNone(filename)
        self.assertIsNone(file_date)

    def test_get_last_filename_from_incorrect_date_suffix_dir(self):
        with patch('LogAnalyzer.logging.error') as mock_logging:
            (filename, file_date) = \
                get_last_filename(self.__class__.test_invalid_dates_log_files_dir,
                                  self.__class__.log_filename_regexp, '%Y%m%d')
        self.assertIsNone(filename)
        self.assertIsNone(file_date)
        mock_logging.assert_called()

    def test_get_source_destination_filenames(self):
        config_dict = {
            "log_dir": self.__class__.test_log_dir,
            "log_filename_regexp": self.__class__.log_filename_regexp,
            "log_filedate_format": '%Y%m%d',
            "report_dir": self.__class__.test_report_dir,
            "report_filename_regexp": self.__class__.report_filename_regexp,
            "report_filename_root": "report-{}.html",
            "report_filedate_format": '%Y.%m.%d'
        }
        result = get_source_destination_filenames(config_dict)
        self.assertTrue(True)
        self.assertEqual(result[1], os.path.join(self.__class__.test_log_dir,
                                                 'nginx-access-ui.log-20170701.log'))
        self.assertEqual(result[2], os.path.join(self.__class__.test_report_dir,
                                                 'report-2017.07.01.html'))

    def test_get_source_destination_filenames_with_no_reports(self):
        config_dict = {
            "log_dir": self.__class__.test_log_dir,
            "log_filename_regexp": self.__class__.log_filename_regexp,
            "log_filedate_format": '%Y%m%d',
            "report_dir": self.__class__.test_log_empty_dir,
            "report_filename_regexp": self.__class__.report_filename_regexp,
            "report_filename_root": "report-{}.html",
            "report_filedate_format": '%Y.%m.%d'
        }
        result = get_source_destination_filenames(config_dict)
        self.assertTrue(True)
        self.assertEqual(result[1], os.path.join(self.__class__.test_log_dir,
                                                 'nginx-access-ui.log-20170701.log'))
        self.assertEqual(result[2], os.path.join(self.__class__.test_log_empty_dir,
                                                 'report-2017.07.01.html'))

    def test_get_source_destination_filenames_with_late_reports(self):
        config_dict = {
            "log_dir": self.__class__.test_log_dir,
            "log_filename_regexp": self.__class__.log_filename_regexp,
            "log_filedate_format": '%Y%m%d',
            "report_dir": self.__class__.test_report_dir_with_late_date,
            "report_filename_regexp": self.__class__.report_filename_regexp,
            "report_filename_root": "report-{}.html",
            "report_filedate_format": '%Y.%m.%d'
        }
        result = get_source_destination_filenames(config_dict)
        self.assertFalse(result[0])
        self.assertIsNone(result[1])
        self.assertIsNone(result[2])

    def test_get_source_destination_filenames_without_logs(self):
        config_dict = {
            "log_dir": self.__class__.test_log_empty_dir,
            "log_filename_regexp": self.__class__.log_filename_regexp,
            "log_filedate_format": '%Y%m%d',
            "report_dir": self.__class__.test_report_dir,
            "report_filename_regexp": self.__class__.report_filename_regexp,
            "report_filename_root": "report-{}.html",
            "report_filedate_format": '%Y.%m.%d'
        }
        result = get_source_destination_filenames(config_dict)
        self.assertFalse(result[0])
        self.assertIsNone(result[1])
        self.assertIsNone(result[2])


if __name__ == '__main__':
    main()
