import os
import time
import smtplib
import string
import re

# FME Log file Parser
# This script reads in all log files in specified directories that have been run in the last 24hrs.
# It then parses them for errors and emails the GIS team if any are found.
#
# It also creates a summary report of all processes run in the last 24hrs (in the Automation Reports dir).
#
# Created by Jonathan Moules, 2011.
# Version 1 - First version
# Version 2 - Added ability to parse multiple direcotories
# Version 3 - 17/7/2012 - Better comments. Added new directory. General tweaks, improved error reporting.
 



############ Variables ############

#specifies the directory with the log files in. Double slashes are necessary.
#Can look in multiple locations
log_directorys = ["c:\\temp_directory\\fme_logs", "D:\\random_direcotry\\fme_logs"]


#Time since the last update. The program will only report on log files more recent than this.
#In hours.
var_time_since = 24



#Internal, do not touch, variables.
out = [] #output list initialisation
num = 0
total_warn = 0
total_error = 0
total_read = int(0)
total_write = int(0)
script_break = ""


######### Functions ##########


#function that parses a log file for various errors
#searches for:
#	WARN level events (only used for automation summary)
#	ERROR level events
#	Total Features Read exists
#	Total Features Written exists
#	FME Session Duration

def parse_file(filename, last_updated, log_dir):
    global out, num, total_warn, total_error, total_read, total_write, script_break
    
    basename = filename[:-4] #filename sans extension

    #create the list entry for this item
    out.append("");
    out[num] = "\n" + log_dir.replace("\\\\wcc-corp.ad\\BuData\\", "H:\\") + basename;
    out[num] += "\nLast Run: " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(last_updated));

    file = open(log_dir + "\\" + filename)

    #prep for parsing file
    count_warn = 0
    count_error = 0

    #these three are used to determine if any part of the file-end didn't parse.
    count_reads = False
    count_writes = False
    count_time = False

    this_error = "";

    re_read = re.compile(".*Total Features Read[ ]*([0-9]+)")
    re_write = re.compile(".*Total Features Written[ ]*([0-9]+)")
    re_time = re.compile(".*FME Session Duration: ([^\(]*).*");
    
    for line in file:
        if("|WARN  |" in line):
            count_warn = count_warn + 1;
        if("|ERROR |" in line):
            count_error = count_error + 1;
        if re_read.search(line):
            temp = re_read.match(line)
            out[num] += "\nFeatures Read: \t\t" + temp.group(1)
            total_read += int(temp.group(1))
            count_reads = True
        if re_write.search(line):
            temp = re_write.match(line)
            out[num] += "\nFeatures Written: \t" + temp.group(1)
            total_write += int(temp.group(1))
            count_writes = True
        if re_time.search(line):
            temp = re_time.match(line)
            out[num] += "\nTime Taken: \t\t" + temp.group(1)
            count_time = True


    if count_reads == False:
        this_error += "\nNo 'Total Features Read' found"
    if count_writes == False:
        this_error += "\nNo 'Total Features Written' found"
    if count_time == False:
        this_error += "\nNo 'FME Session Duration' found"

    out[num] += "\nWarnings: \t\t\t" + str(count_warn);
    total_warn += count_warn;
    out[num] += "\nErrors: \t\t\t" + str(count_error);
    total_error += count_error;
    if count_error > 0:
        this_error += "\n" + str(count_error) + " ERROR level FME event(s) occured while running the workspace."

    if this_error != "":
        script_break += "\n\n-------\nFile: " + log_dir + "\\" + filename + "\n" + this_error

###### END Functions ######

########## Start ##########

#Find all log files that have been changed in the last var_time_since
#Recurses through the two specified directories using os.walk.
for directory in log_directorys:
	for (path, dirs, files) in os.walk(directory):
		for this_file in files:
		
			if this_file[-3:] == "log": #.log files only

				last_updated = os.path.getmtime(path + "\\" + this_file) #gets time of last update in seconds.

				if (time.time() - last_updated) < 86400: #changed within the last 24hrs
					parse_file(this_file, last_updated, path);
					num = num + 1

#If no report logs from the period are found, report as error.
if num == 0:
    script_break = "\nNo log files were detected as having been changed in the last " + str(var_time_since) + " hours\nThis probably means no FME workspaces were run over that period.";


#print out
file_output = open('c:\\Automation_reports\\report_' + time.strftime("%Y%m%d", time.localtime()) + '.log', 'w') #outputs to a text file

#In case errors are detected. Yell in a really obnoxious CAPSY way!
if total_error > 0:
    print>>file_output, "\n!!!!!!!!!!!WARNING ERRORS DETECTED!!!!!!!!!!!\n!!!!!!!!!!!WARNING ERRORS DETECTED!!!!!!!!!!!\n!!!!!!!!!!!WARNING ERRORS DETECTED!!!!!!!!!!!\n!!!!!!!!!!!WARNING ERRORS DETECTED!!!!!!!!!!!"

#header summery analysis
print>>file_output, "\nTotal Errors in logs:\t" + str(total_error) + "\t\t\tTotal Warnings in logs:\t" + str(total_warn)
print>>file_output, "Total Features Read:\t" + str(total_read) + "\t\tTotal Features Written:\t" + str(total_write) + "\t\tDifference:\t" + str(total_write-total_read)

for this in out:
    print>>file_output, this
file_output.close()


#In case there is something that needs emailing.
if script_break != "":
    print script_break

    #email sending time
    SUBJECT = "FME Automation status update: " + time.strftime("%a, %d %b %Y", time.localtime())
    TO = ["me@example.com"]
    FROM = "me@example.com"
    text = "Hello GIS Team, \n\tI'm your Friendly Python Script (version 3, yay for evolution!) and I've discovered an error relating to the automated FME processes. The error follows: \n\n!!!!!!!!!!!!!!" + script_break + "\n!!!!!!!!!!!!!!\n\nI cordially recommend someone investigate this.\n\tYours insincerely,\n\tThe Friendly Python Script"
    BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT ,
            "",
            text
            ), "\r\n")
    server = smtplib.SMTP("your-smtp-server")
    server.sendmail(FROM, TO, BODY)
    server.quit()
