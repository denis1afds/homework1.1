import unittest
from unittest.mock import patch
from LogAnalyzer import init_analyzer
import os
import datetime


class TestInitAnalyzer(unittest.TestCase):
    report_filename_valid = None
    report_filename_invalid = None
    log_filename_valid = None
    log_filename_invalid = None
    log_line_valid_filename = None
    log_line_invalid_filename = None
    config_test_filepath = None
    config = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.report_filename_valid = (
            'report-2023.05.30.html', 'report-2023.05.31.html', 'report-2023.06.30.html')
        cls.report_filename_invalid = (
            'report-2023-05-30.html', 'report-2023/05/31.html', 'report-2023.06.30.htm',
            'rep-2023-05-30.html', 'report-2023-05-30.txt', 'report-30-05-2023.html',
            'report-2023.05.30.htmlk',
        )
        cls.log_filename_valid = (
            'nginx-access-ui.log-20180630.log', 'nginx-access-ui.log-20170630.gz',
            'nginx-access-ui.log-20230630.gz', 'nginx-access-ui.log-20230130.log',
        )
        cls.log_filename_invalid = (
            'nginx-access-ui.log-20180630.txt', 'nginx-access-ui.log-20170630.bz',
            'nginx-access-ui.log-20230630.zip', 'nginx-access-ui.log-20230130.logtx',
            'nginx-access-ui.log-201806.log', 'nginx-access-ui.log-deeffb12.gz',
        )

        cls.config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./data/reports",
            "REPORT_TEMPLATE_PATH": "./data/templates/report.html",
            "LOG_DIR": "./data/logs",
            "INTERNAL_LOG_PATH": "./data/analyzer_logs/log_module_${date}.log",
        }
        cls.log_line_valid_filename = './data/tests/valid_log.log'
        cls.log_line_invalid_filename = './data/tests/invalid_log.log'
        cls.config_test_filepath = os.path.abspath(r'.\data\tests\config_test.json')

        if os.path.isfile(cls.config_test_filepath):
            os.remove(cls.config_test_filepath)

    def test_init_default_config(self):
        result_config = init_analyzer(TestInitAnalyzer.config)
        self.assertEqual(result_config['report_size'], 1000)
        self.assertEqual(result_config['report_dir'], os.path.abspath('./data/reports'))
        self.assertEqual(result_config['report_template_path'],
                         os.path.abspath('./data/templates/report.html'))
        self.assertEqual(result_config['report_filename_template'],
                         r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$")
        for report_filename in TestInitAnalyzer.report_filename_valid:
            self.assertRegex(report_filename, result_config['report_filename_regexp'])
        for report_filename in TestInitAnalyzer.report_filename_invalid:
            self.assertNotRegex(report_filename, result_config['report_filename_regexp'])
        self.assertEqual(result_config['report_filename_root'], 'report-{}.html')
        self.assertEqual(result_config['report_filedate_format'], '%Y.%m.%d')
        self.assertEqual(result_config['log_dir'], os.path.abspath('./data/logs'))
        self.assertEqual(result_config['log_filename_template'],
                         r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$")
        for log_filename in TestInitAnalyzer.log_filename_valid:
            self.assertRegex(log_filename, result_config['log_filename_regexp'])
        for log_filename in TestInitAnalyzer.log_filename_invalid:
            self.assertNotRegex(log_filename, result_config['log_filename_regexp'])
        self.assertEqual(result_config['log_line_template'],
                         r'^(?P<remote_addr>\S+)\s+'
                         r'(?P<remote_user>\S+)\s+'
                         r'(?P<http_x_real_ip>\S+)\s+'
                         r'\[(?P<time_local>[^\]]+)\]\s+'
                         r'\"(?P<request>[^\"]+)\"\s+'
                         r'(?P<status>\d+)\s+'
                         r'(?P<body_bytes_sent>\d+)\s+'
                         r'\"(?P<http_referer>[^\"]+)\"\s+\"'
                         r'(?P<http_user_agent>[^\"]+)\"\s+\"'
                         r'(?P<http_x_forwarded_for>[^\"]+)\"\s+'
                         r'\"(?P<http_x_request_id>[^\"]+)\"\s+'
                         r'\"(?P<http_rb_user>[^\"]+)\"\s+'
                         r'(?P<request_time>\S+)'
                         )

        self.assertLess(abs(result_config['log_parse_error_threshold'] - 0.01), 0.00001)
        with (open(TestInitAnalyzer.log_line_valid_filename, 'rt', encoding='utf-8')) \
                as valid_log_fd:
            line = valid_log_fd.readline()
            self.assertRegex(line, result_config['log_line_regexp'])

        with (open(TestInitAnalyzer.log_line_invalid_filename, 'rt', encoding='utf-8')) \
                as invalid_log_fd:
            line = invalid_log_fd.readline()
            self.assertNotRegex(line, result_config['log_line_regexp'])

        self.assertEqual(result_config['internal_log_path'],
                         os.path.abspath('./data/analyzer_logs/log_module_{}.log'
                                         .format(datetime.datetime.strftime(datetime.date.today(),
                                                                            '%Y-%m-%d')
                                                 )
                                         )
                         )
        self.assertEqual(result_config['log_filedate_format'], '%Y%m%d')
        self.assertTrue(result_config['is_launch'])

    @patch('sys.argv', ['filename', '--no-launch'])
    def test_init_no_launch(self):
        result_config = init_analyzer(TestInitAnalyzer.config)

        self.assertEqual(result_config['report_size'], 1000)
        self.assertEqual(result_config['report_dir'], os.path.abspath('./data/reports'))
        self.assertEqual(result_config['report_template_path'], os.path.abspath('./data/templates/report.html'))
        self.assertEqual(result_config['report_filename_template'],
                         r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$")
        for report_filename in TestInitAnalyzer.report_filename_valid:
            self.assertRegex(report_filename, result_config['report_filename_regexp'])

        for report_filename in TestInitAnalyzer.report_filename_invalid:
            self.assertNotRegex(report_filename, result_config['report_filename_regexp'])
        self.assertEqual(result_config['report_filename_root'], 'report-{}.html')
        self.assertEqual(result_config['report_filedate_format'], '%Y.%m.%d')
        self.assertEqual(result_config['log_dir'], os.path.abspath('./data/logs'))
        self.assertEqual(result_config['log_filename_template'],
                         r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$")
        for log_filename in TestInitAnalyzer.log_filename_valid:
            self.assertRegex(log_filename, result_config['log_filename_regexp'])
        for log_filename in TestInitAnalyzer.log_filename_invalid:
            self.assertNotRegex(log_filename, result_config['log_filename_regexp'])
        self.assertEqual(result_config['log_line_template'],
                         r'^(?P<remote_addr>\S+)\s+'
                         r'(?P<remote_user>\S+)\s+'
                         r'(?P<http_x_real_ip>\S+)\s+'
                         r'\[(?P<time_local>[^\]]+)\]\s+'
                         r'\"(?P<request>[^\"]+)\"\s+'
                         r'(?P<status>\d+)\s+'
                         r'(?P<body_bytes_sent>\d+)\s+'
                         r'\"(?P<http_referer>[^\"]+)\"\s+\"'
                         r'(?P<http_user_agent>[^\"]+)\"\s+\"'
                         r'(?P<http_x_forwarded_for>[^\"]+)\"\s+'
                         r'\"(?P<http_x_request_id>[^\"]+)\"\s+'
                         r'\"(?P<http_rb_user>[^\"]+)\"\s+'
                         r'(?P<request_time>\S+)'
                         )
        with (open(TestInitAnalyzer.log_line_valid_filename, 'rt', encoding='utf-8')) \
                as valid_log_fd:
            line = valid_log_fd.readline()
            self.assertRegex(line, result_config['log_line_regexp'])
        with (open(TestInitAnalyzer.log_line_invalid_filename, 'rt', encoding='utf-8')) \
                as invalid_log_fd:
            line = invalid_log_fd.readline()
            self.assertNotRegex(line, result_config['log_line_regexp'])
        self.assertEqual(result_config['internal_log_path'],
                         os.path.abspath('./data/analyzer_logs/log_module_{}.log'
                                         .format(datetime.datetime.strftime(datetime.date.today(),
                                                                            '%Y-%m-%d')
                                                 )
                                         )
                         )
        self.assertEqual(result_config['log_filedate_format'], '%Y%m%d')
        self.assertFalse(result_config['is_launch'])

    @patch('sys.argv', [
        'filename',
        '--config-export',
        r'.\data\tests\config_test.json',
        '--no-launch', ]
           )
    def test_init_with_config_export_no_launch(self):
        result_config = init_analyzer(TestInitAnalyzer.config)
        self.assertEqual(result_config['report_size'], 1000)
        self.assertEqual(result_config['report_dir'], os.path.abspath('./data/reports'))
        self.assertEqual(result_config['report_template_path'],
                         os.path.abspath('./data/templates/report.html'))
        self.assertEqual(result_config['report_filename_template'],
                         r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$")
        for report_filename in TestInitAnalyzer.report_filename_valid:
            self.assertRegex(report_filename, result_config['report_filename_regexp'])

        for report_filename in TestInitAnalyzer.report_filename_invalid:
            self.assertNotRegex(report_filename, result_config['report_filename_regexp'])
        self.assertEqual(result_config['report_filename_root'], 'report-{}.html')
        self.assertEqual(result_config['report_filedate_format'], '%Y.%m.%d')
        self.assertEqual(result_config['log_dir'], os.path.abspath('./data/logs'))
        self.assertEqual(result_config['log_filename_template'],
                         r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$")

        for log_filename in TestInitAnalyzer.log_filename_valid:
            self.assertRegex(log_filename, result_config['log_filename_regexp'])

        for log_filename in TestInitAnalyzer.log_filename_invalid:
            self.assertNotRegex(log_filename, result_config['log_filename_regexp'])

        self.assertEqual(result_config['log_line_template'],
                         r'^(?P<remote_addr>\S+)\s+'
                         r'(?P<remote_user>\S+)\s+'
                         r'(?P<http_x_real_ip>\S+)\s+'
                         r'\[(?P<time_local>[^\]]+)\]\s+'
                         r'\"(?P<request>[^\"]+)\"\s+'
                         r'(?P<status>\d+)\s+'
                         r'(?P<body_bytes_sent>\d+)\s+'
                         r'\"(?P<http_referer>[^\"]+)\"\s+\"'
                         r'(?P<http_user_agent>[^\"]+)\"\s+\"'
                         r'(?P<http_x_forwarded_for>[^\"]+)\"\s+'
                         r'\"(?P<http_x_request_id>[^\"]+)\"\s+'
                         r'\"(?P<http_rb_user>[^\"]+)\"\s+'
                         r'(?P<request_time>\S+)'
                         )

        with (open(TestInitAnalyzer.log_line_valid_filename, 'rt', encoding='utf-8')) \
                as valid_log_fd:
            line = valid_log_fd.readline()
            self.assertRegex(line, result_config['log_line_regexp'])
        with (open(TestInitAnalyzer.log_line_invalid_filename, 'rt', encoding='utf-8')) \
                as invalid_log_fd:
            line = invalid_log_fd.readline()
            self.assertNotRegex(line, result_config['log_line_regexp'])
        self.assertEqual(result_config['internal_log_path'],
                         os.path.abspath('./data/analyzer_logs/log_module_{}.log'
                                         .format(datetime.datetime.strftime(datetime.date.today(),
                                                                            '%Y-%m-%d')
                                                 )
                                         )
                         )
        self.assertEqual(result_config['log_filedate_format'], '%Y%m%d')
        self.assertFalse(result_config['is_launch'])
        self.assertTrue(os.path.isfile(TestInitAnalyzer.config_test_filepath))
        os.remove(TestInitAnalyzer.config_test_filepath)

    @patch('sys.argv', ['filename', '--config', r'.\data\tests\config.json'])
    def test_init_with_config_import(self):
        result_config = init_analyzer(TestInitAnalyzer.config)

        self.assertEqual(result_config['report_size'], 10)
        self.assertEqual(result_config['report_dir'].lower(),
                         os.path.abspath('./data/reports/test').lower())
        self.assertEqual(result_config['report_template_path'].lower(),
                         os.path.abspath('./data/templates/report.html').lower())
        self.assertEqual(result_config['report_filename_template'],
                         r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$")
        for report_filename in TestInitAnalyzer.log_filename_valid:
            self.assertRegex(report_filename, result_config['report_filename_regexp'])

        for report_filename in TestInitAnalyzer.log_filename_invalid:
            self.assertNotRegex(report_filename, result_config['report_filename_regexp'])
        self.assertEqual(result_config['report_filename_root'], 'report-{}.html')
        self.assertEqual(result_config['report_filedate_format'], '%Y.%m.%d')

        self.assertEqual(result_config['log_dir'].lower(),
                         os.path.abspath('./data/logs').lower())
        self.assertEqual(result_config['log_filename_template'],
                         r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$")

        for log_filename in TestInitAnalyzer.report_filename_valid:
            self.assertRegex(log_filename, result_config['log_filename_regexp'])

        for log_filename in TestInitAnalyzer.report_filename_invalid:
            self.assertNotRegex(log_filename, result_config['log_filename_regexp'])

        self.assertEqual(result_config['log_line_template'],
                         r'^(?P<remote_addr>\S+)\s+'
                         r'(?P<remote_user>\S+)\s+'
                         r'(?P<http_x_real_ip>\S+)\s+'
                         r'\[(?P<time_local>[^\]]+)\]\s+'
                         r'\"(?P<request>[^\"]+)\"\s+'
                         r'(?P<status>\d+)\s+'
                         r'(?P<body_bytes_sent>\d+)\s+'
                         r'\"(?P<http_referer>[^\"]+)\"\s+\"'
                         r'(?P<http_user_agent>[^\"]+)\"\s+\"'
                         r'(?P<http_x_forwarded_for>[^\"]+)\"\s+'
                         r'\"(?P<http_x_request_id>[^\"]+)\"\s+'
                         r'\"(?P<http_rb_user>[^\"]+)\"\s+'
                         r'(?P<request_time>\S+)'
                         )

        with (open(TestInitAnalyzer.log_line_valid_filename, 'rt', encoding='utf-8')) \
                as valid_log_fd:
            line = valid_log_fd.readline()
            self.assertRegex(line, result_config['log_line_regexp'])
        with (open(TestInitAnalyzer.log_line_invalid_filename, 'rt', encoding='utf-8')) \
                as invalid_log_fd:
            line = invalid_log_fd.readline()
            self.assertNotRegex(line, result_config['log_line_regexp'])

        self.assertEqual(result_config['internal_log_path'].lower(),
                         os.path.abspath('./data/analyzer_logs/журнал_{}.log'
                                         .format(datetime.datetime.strftime(datetime.date.today(),
                                                                            '%Y-%m-%d')
                                                 )
                                         ).lower()
                         )
        self.assertEqual(result_config['log_filedate_format'], '%Y-%m-%d')
        self.assertTrue(result_config['is_launch'])


if __name__ == '__main__':
    unittest.main()
