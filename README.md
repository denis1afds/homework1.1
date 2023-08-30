![Buid Status](https://github.com/denis1afds/homework1.1/actions/workflows/checks.yml/badge.svg?branch=master)

![Logo of the project](./logo.png)

# Nginx log analyzer
>It's educational project. Python script for analyze nginx log and create html report

## Installing / Getting started

Clone project or copy it's catalog to working directory

For analyze and create report with default settings:
```shell
python ./LogAnalyzer.py
```

## Command line keys
###  Breifs description utility usage
> --help 

### Updates default parameters from json config file
> --config `json config filename`

### Stores result after merge or replace default config with import settings 
> --config-export `json config file path`  


## Configuration file specification
### Default settings
```shell
{
  "report_size": 1000,
  "report_dir": "E:\\Develop\\CoursePython\\Homeworks\\LogAnalyzer\\data\\reports",
  "report_template_path": "E:\\Develop\\CoursePython\\Homeworks\\LogAnalyzer\\data\\templates\\report.html",
  "report_filename_template": "^report-(?P<file_date>[0-9]{4}\\.[0-9]{2}\\.[0-9]{2})\\.html$",
  "report_filename_root": "report-{}.html",
  "report_filedate_format": "%Y.%m.%d",
  "log_dir": "E:\\Develop\\CoursePython\\Homeworks\\LogAnalyzer\\data\\logs",
  "log_filename_template": "^nginx-access-ui\\.log-(?P<file_date>[0-9]{8})\\.(?:log|gz)$",
  "log_filedate_format": "%Y%m%d",
  "log_line_template": "^(?P<remote_addr>\\S+)\\s+(?P<remote_user>\\S+)\\s+(?P<http_x_real_ip>\\S+)\\s+\\[(?P<time_local>[^\\]]+)\\]\\s+\\\"(?P<request>[^\\\"]+)\\\"\\s+(?P<status>\\d+)\\s+(?P<body_bytes_sent>\\d+)\\s+\\\"(?P<http_referer>[^\\\"]+)\\\"\\s+\\\"(?P<http_user_agent>[^\\\"]+)\\\"\\s+\\\"(?P<http_x_forwarded_for>[^\\\"]+)\\\"\\s+\\\"(?P<http_x_request_id>[^\\\"]+)\\\"\\s+\\\"(?P<http_rb_user>[^\\\"]+)\\\"\\s+(?P<request_time>\\S+)",
  "log_parse_error_threshold": 0.01,
  "internal_log_path": "E:\\Develop\\CoursePython\\Home
}
```
###  Setting parameters description

__report_size__: size of result report. It must contain less or equal {report_size} urls records\
__report_dir__: report destionation directory\
__report_template_path__: template file for fillig report\
__report_filename_template__: regex expression for identification ready report\
__report_filename_root__: root report file name\
__report_filedate_format__: report file name suffix date format\
__log_dir__: log files directory path\
__log_filename_template__: regex expression for identification log file\
__log_filedate_format__: log file name suffix date format\
__log_line_template__: regex expression for parse log line record\
__log_parse_error_threshold__: the threshold value of the precenrage of errors from the number of log lines, when exceeded, an warning message is displayed\
__internal_log_path__: LogAnalyzer internal log file path
```

## Testing list
```
test_init_analyzer - check init config settings. Check command line arguments actions
test_get_last_log_filename -testing the functions that determine the last log file to
generate the report
test_log_record_gen - testing generator class that opening and parsing log file
```

### Licensing

"The code in this project is licensed under MIT license."
