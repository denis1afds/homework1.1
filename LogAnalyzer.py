#!/usr/bin/env python
# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for"
#                       "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';
import sys
import os
import re
import gzip
import logging
import datetime
import json
import argparse
from string import Template
from collections import defaultdict
from statistics import median


def global_exception_handler(*_):
    logging.exception('uncaught exception')


sys.excepthook = global_exception_handler

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./data/reports",
    "REPORT_TEMPLATE_PATH": "./data/templates/report.html",
    "LOG_DIR": "./data/logs",
    "INTERNAL_LOG_PATH": "./data/analyzer_logs/log_module_${date}.log"
}


def main():
    config_dict = init_analyzer()
    logging.basicConfig(level=logging.INFO,
                        filename=config_dict['internal_log_path'],
                        filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s")

    is_launch, log_filename, report_filename = get_source_destination_filenames(config_dict)
    if is_launch:
        try:
            with LogRecordGen(log_filename,
                              config_dict['log_line_regexp'],
                              config_dict['log_parse_error_threshold']) as log_record_gen:
                log_json = json.dumps(create_report_dict(log_record_gen,
                                                         config_dict['report_size'])
                                      )

            with open(config_dict['report_template_path'], mode='r', encoding='utf-8') as rtf:
                with open(report_filename, mode='w', encoding='utf-8') as rof:
                    for data in rtf:
                        rof.write(Template(data).safe_substitute(table_json=log_json))

        except (FileNotFoundError, PermissionError):
            logging.exception('File access error')


def init_analyzer(default_config=None):
    if default_config is None:
        default_config = config
    current_config = {
        "report_size": default_config['REPORT_SIZE'],
        "report_dir": os.path.abspath(default_config['REPORT_DIR']),
        "report_template_path": os.path.abspath(default_config['REPORT_TEMPLATE_PATH']),
        "report_filename_template": r"^report-(?P<file_date>[0-9]{4}\.[0-9]{2}\.[0-9]{2})\.html$",
        "report_filename_root": "report-{}.html",
        "report_filedate_format": "%Y.%m.%d",
        "log_dir": os.path.abspath(default_config['LOG_DIR']),
        "log_filename_template": r"^nginx-access-ui\.log-(?P<file_date>[0-9]{8})\.(?:log|gz)$",
        "log_filedate_format": "%Y%m%d",
        "log_line_template": r'^(?P<remote_addr>\S+)\s+'
                             r'(?P<remote_user>\S+)\s+'
                             r'(?P<http_x_real_ip>\S+)\s+'
                             r'\[(?P<time_local>[^\]]+)\]\s+'
                             r'\"(?P<request>[^\"]+)\"\s+'
                             r'(?P<status>\d+)\s+'
                             r'(?P<body_bytes_sent>\d+)\s+'
                             r'\"(?P<http_referer>[^\"]+)\"\s+'
                             r'\"(?P<http_user_agent>[^\"]+)\"\s+'
                             r'\"(?P<http_x_forwarded_for>[^\"]+)\"\s+'
                             r'\"(?P<http_x_request_id>[^\"]+)\"\s+'
                             r'\"(?P<http_rb_user>[^\"]+)\"\s+'
                             r'(?P<request_time>\S+)',
        "log_parse_error_threshold": 0.01,
        "internal_log_path": os.path.abspath(default_config['INTERNAL_LOG_PATH'])
    }

    parser_cli = argparse.ArgumentParser(description='Parse last nginx log and create report ')
    parser_cli.add_argument('--config', dest='config_import_filename',
                            help='Config file path (optional)',
                            action='store',
                            default=None)
    parser_cli.add_argument('--config-export', dest='config_export_filename',
                            help='Store result or default config to path',
                            action='store',
                            default=None)
    parser_cli.add_argument('--no-launch', dest='is_launch',
                            help='Not necessary analyzer launch. '
                                 '(Makes sense when required export config to file',
                            action='store_false',
                            default=True)
    args = parser_cli.parse_args()

    if args.config_import_filename:
        try:
            with open(args.config_import_filename, mode='rt', encoding='utf-8') as cfg_file:
                custom_config = json.load(cfg_file)
                for config_key in custom_config:
                    current_config[config_key] = \
                        custom_config.get(config_key, current_config.get(config_key, None))

        except FileNotFoundError:
            print('File with config not found: {}'.format(args.config_filename))
            raise

        except json.JSONDecodeError:
            print('Config file decode error')
            raise

    if args.config_export_filename:
        try:
            with open(args.config_export_filename, mode='wt', encoding='utf-8') as cfg_file:
                json.dump(current_config, cfg_file, indent=2)
        except OSError:
            print('Store config error')
            raise

    current_config.update({'is_launch': args.is_launch})

    current_config.update({'report_filename_regexp': re.compile(
        current_config['report_filename_template'])})
    current_config.update({'log_filename_regexp': re.compile(
        current_config['log_filename_template'])})
    current_config.update({'log_line_regexp': re.compile(
        current_config['log_line_template'])})
    current_config.update({'internal_log_path': Template(current_config['internal_log_path']).
                          safe_substitute(date=datetime.datetime.strftime(datetime.date.today(),
                                                                          '%Y-%m-%d'))})
    return current_config


def gen_match_files(file_path, filename_regexp, date_format):
    for filename in os.listdir(file_path):
        if os.path.isfile(os.path.join(file_path, filename)):
            file_match = filename_regexp.search(filename)
            if file_match is not None:
                try:
                    file_date = datetime.datetime.strptime(file_match.group('file_date'),
                                                           date_format).date()
                except ValueError:
                    logging.error('File date parsing error:' + filename)
                else:
                    yield os.path.abspath(os.path.join(file_path, filename)), file_date


def get_last_filename(path_dir, filename_regexp, file_date_suffix):
    try:
        return (sorted(((file[0], file[1])
                        for file in gen_match_files(path_dir, filename_regexp, file_date_suffix)),
                       key=lambda file: file[1], reverse=True)[0])
    except IndexError:
        return None, None


def get_source_destination_filenames(config_dict):
    """Return source log and destination report filenames in tuple

    config_dict -- dictionary with application settings
    """
    (log_filename, log_filedate) = get_last_filename(config_dict['log_dir'],
                                                     config_dict['log_filename_regexp'],
                                                     config_dict['log_filedate_format'])

    (report_filename, report_filedate) = get_last_filename(config_dict['report_dir'],
                                                           config_dict['report_filename_regexp'],
                                                           config_dict['report_filedate_format'])

    if log_filedate is not None:
        if (log_filedate > report_filedate) if report_filedate is not None else True:
            return \
                True, \
                log_filename, \
                os.path.join(config_dict['report_dir'],
                             config_dict['report_filename_root'].format(log_filedate.strftime(
                                     config_dict['report_filedate_format']))
                             )
    return False, None, None


def create_report_dict(log_record_gen, top_records_no):
    total_request_qty = 0
    total_request_time = 0
    url_request_time = defaultdict(list)

    for log_dict in log_record_gen:
        url_list = log_dict['request'].split(' ')
        url_line = url_list[1] if len(url_list) > 1 else None
        total_request_qty += 1
        total_request_time += log_dict['request_time']
        url_request_time[url_line].append(log_dict['request_time'])

    url_statistic_list = list()

    for url_line in url_request_time:
        time_sum = sum(url_request_time[url_line])
        url_statistic_list.append({
            'url': url_line,
            'count': len(url_request_time[url_line]),
            'count_perc': '{:.3%}'.format(len(url_request_time[url_line]) / total_request_qty),
            'time_sum': round(time_sum, 3),
            'time_perc': '{:.3%}'.format(time_sum / total_request_time),
            'time_avg': '{:.3f}'.format(time_sum / len(url_request_time[url_line])),
            'time_max': '{:.3f}'.format(max(url_request_time[url_line])),
            'time_med': '{:.3f}'.format(median(url_request_time[url_line]))
        })
    return sorted(url_statistic_list,
                  key=lambda record_dict: record_dict['time_sum'],
                  reverse=True)[:top_records_no]


class LogRecordGen:
    def __init__(self, log_filename, log_parser_regexp, log_parse_error_threshold):
        self.log_filename = log_filename
        self.log_parser_regexp = log_parser_regexp
        self.log_parse_error_threshold = log_parse_error_threshold
        self.lines_count = 0
        self.parse_errors_count = 0
        self.parse_errors_lines_list = list()
        self.open_operator = gzip.open if log_filename.endswith('.gz') else open

    def __enter__(self):
        self.file_descr = self.open_operator(self.log_filename, mode='rt', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            ratio = self.parse_errors_count / self.lines_count
            logging.info('parsing lines:{}, parsings error count:{} ({:.3%})'
                         .format(self.lines_count,
                                 self.parse_errors_count,
                                 ratio)
                         )
            if ratio >= self.log_parse_error_threshold:
                logging.warning('parsing error ratio over threshold percent. '
                                'Actual:{:.3%}, Expect: less {:.1%}'
                                .format(ratio, self.log_parse_error_threshold))
        self.file_descr.close()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            line = self.file_descr.readline()
            if len(line) == 0:
                raise StopIteration
            self.lines_count += 1
            try:
                fields = re.search(self.log_parser_regexp, line).groupdict()
                fields['request_time'] = float(fields['request_time'])
                return fields
            except (ValueError, AttributeError):
                self.parse_errors_count += 1
                self.parse_errors_lines_list.append(self.lines_count)


if __name__ == "__main__":
    main()
