from unittest import TestCase
from LogAnalyzer import LogRecordGen, create_report_dict
import os
import re
from unittest.mock import patch


class TestGetLastLogFileName(TestCase):
    test_log_dir = os.path.abspath('./data/tests')
    log_line_template = r'^(?P<remote_addr>\S+)\s+'\
                        r'(?P<remote_user>\S+)\s+'\
                        r'(?P<http_x_real_ip>\S+)\s+'\
                        r'\[(?P<time_local>[^\]]+)\]\s+'\
                        r'\"(?P<request>[^\"]+)\"\s+'\
                        r'(?P<status>\d+)\s+'\
                        r'(?P<body_bytes_sent>\d+)\s+'\
                        r'\"(?P<http_referer>[^\"]+)\"\s+'\
                        r'\"(?P<http_user_agent>[^\"]+)\"\s+'\
                        r'\"(?P<http_x_forwarded_for>[^\"]+)\"\s+'\
                        r'\"(?P<http_x_request_id>[^\"]+)\"\s+'\
                        r'\"(?P<http_rb_user>[^\"]+)\"\s+'\
                        r'(?P<request_time>\S+)'
    log_line_regexp = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.log_line_regexp = re.compile(cls.log_line_template)

    def test_gen_match_log_files(self):
        with patch('LogAnalyzer.logging.warning') as mock_logging:
            with LogRecordGen(
                    os.path.join(self.__class__.test_log_dir, 'nginx-access-ui.log-20170630.log'),
                    self.__class__.log_line_regexp,
                    0.05
            ) as log_record_gen:
                for _ in log_record_gen:
                    pass
                self.assertEqual(log_record_gen.lines_count, 30)
                self.assertEqual(log_record_gen.parse_errors_count, 2)
                self.assertListEqual(log_record_gen.parse_errors_lines_list, [7, 11])
            mock_logging.assert_called_once_with('parsing error ratio over threshold percent. '
                                                 'Actual:6.667%, Expect: less 5.0%')

    def test_gen_match_log_files_wrong_filename(self):
        with self.assertRaises(FileNotFoundError):
            with LogRecordGen(
                    os.path.join(self.__class__.test_log_dir, 'nginx-access-ui.log-20170632.log'),
                    self.__class__.log_line_regexp,
                    0.01
            ) as log_record_gen:
                for _ in log_record_gen:
                    pass

    def test_create_report_dict(self):
        with LogRecordGen(
                os.path.join(self.__class__.test_log_dir, 'nginx-access-ui.log-20170630.log'),
                self.__class__.log_line_regexp, 0.1) as log_record_gen:
            url_statistic_list = create_report_dict(log_record_gen, 100)
        self.assertEqual(len(url_statistic_list), 25)
        test_record_dict = [record_dict for record_dict in url_statistic_list
                            if record_dict['url'] == '/api/v2/banner/25019908'][0]
        self.assertEqual(test_record_dict['count'], 4)
        self.assertLess(abs(test_record_dict['time_sum'] - 4.123), 0.0001)
        self.assertEqual(test_record_dict['count_perc'], '14.286%')
        self.assertEqual(test_record_dict['time_avg'], '1.031')
        self.assertEqual(test_record_dict['time_perc'], '33.976%')
        self.assertEqual(test_record_dict['time_max'], '1.403')
        self.assertEqual(test_record_dict['time_med'], '1.282')

    def test_create_report_dict_with_top_records_limit(self):
        with LogRecordGen(
                os.path.join(self.__class__.test_log_dir, 'nginx-access-ui.log-20170630.log'),
                self.__class__.log_line_regexp, 0.1) as log_record_gen:
            url_statistic_list = create_report_dict(log_record_gen, 3)
        self.assertEqual(len(url_statistic_list), 3)
        self.assertEqual(url_statistic_list[0]['url'], '/api/v2/banner/25019908')
        self.assertLess(abs(url_statistic_list[0]['time_sum'] - 4.123), 0.0001)
        self.assertEqual(url_statistic_list[1]['url'], '/api/v2/banner/25047606')
        self.assertLess(abs(url_statistic_list[1]['time_sum'] - 1.49), 0.0001)
        self.assertEqual(url_statistic_list[2]['url'], '/api/v2/banner/25013431')
        self.assertLess(abs(url_statistic_list[2]['time_sum'] - 0.917), 0.0001)
