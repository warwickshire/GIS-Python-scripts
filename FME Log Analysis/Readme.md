About
=====

This script is designed to read in a directory of FME log files. It will parse all files that have been edited in the last n hours (default 24) and create a summary report. It will also email if any ERROR level events have been detected.

How to use
----------
There are a few things to configure. Once they've been configured you can schedule it as a regular task using something like task scheduler or cron.


* Line 25

Specify the directory(s) that contain the log files.

* Line 30 [optional]

How far back in time should the timestamp on the file be (in hours) to be read. This stops old log files being parsed.

* Line 62 [optional]

If you want to change paths between what the input reads and what's written to the output log file, you can do so here. This has no functional change to the script.

* Line 144

Set the destination directory for the summary log file.

* Line 165, 166

Set the from and to email addresses.

* Line 175
Set the SMTP server.