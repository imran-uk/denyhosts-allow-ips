#!/usr/bin/python

"""
Allow IP addresses that have been blocked by DenyHosts.

This script automates much of this process:
http://denyhosts.sourceforge.net/faq.html#3_19

THIS SCRIPT WILL OVERWRITE AND CHANGE FILES!

To be safe, backup /etc/hosts.deny and /var/lib/denyhosts beforehand!

eg.
tar -czvf /tmp/denyhosts.tar.gz /var/lib/denyhosts
cp /etc/hosts.deny /etc/hosts.deny.bak

Make sure the file of IPs is in dotted-quad format, newline delimited and 
with no leading or trailing spaces.

Stop denyhosts first. Run as root or with sudo. Assumes work-dir is /var/lib/denyhosts.

Allow 10.0.0.1: 
./denyhosts-allow-ips.py 10.0.0.1

Allow IPs in ips.txt and also remove them from /etc/hosts.deny:
./denyhosts-allow-ips.py --hosts-deny --ips ips.txt

Allow IPs in ips.txt, remove from hosts-deny but work-dir not default:
./denyhosts-allow-ips.py --work-dir /var/local/denyhosts --hosts-deny --ips ips.txt

TODO 
* An option to add the IP(s) to allowed-hosts
* Show a summary of how many IPs were removed
* auto-backup files
* Warn if user is not running as root
"""

__author__ = """Imran Chaudhry, ichaudhry@gmail.com

GPG Key fingerprint = B323 477E F6AB 4181 9C65  F637 BC5F 7FCC 9CC9 CC7F

This is "thankyou-ware" - send me a note of thanks if you have found this
script useful - thanks!
"""
__version__ = 1.01

import shutil
import sys
import re
import os

def	process_hosts_deny(ip_list):
	work_filename = '/etc/hosts.deny'
	tmp_filename = '/tmp/hosts.deny.tmp'
	wf = open(work_filename, 'r')
	tf = open(tmp_filename, 'w')
	file_lines = wf.readlines()
	for line in file_lines:
		if not process_line(line, ip_list):
			tf.write(line)
	wf.close()
	tf.close()
	shutil.move(tmp_filename, work_filename)
	return

def	process_files(work_dir, work_files, ip_list):
	for filename in work_files:
		work_filename = os.path.join(work_dir, filename)
		tmp_filename = os.path.join(work_dir, filename + '.tmp')
		wf = open(work_filename, 'r')
		tf = open(tmp_filename, 'w')
		file_lines = wf.readlines()
		for line in file_lines:
			if not process_line(line, ip_list):
				tf.write(line)
		wf.close()
		tf.close()
		shutil.move(tmp_filename, work_filename)
	return

def get_allow_ips(filename):
	f = open(filename, 'rU')
	ip_list = []
	for line in f:
		ip_list.append(line.strip('\n'))
	f.close()
	return ip_list 

def process_line(line, ip_list):
	for ip in ip_list:
		match = re.search(re.escape(ip), line)
		if match:
			return True
	return

def main():
	args = sys.argv[1:]

	ip_list = []
	work_files = ['hosts', 'hosts-restricted', 'hosts-root', 'hosts-valid',
'users-hosts']

	if not args:
		print 'usage: [--work-dir dir] [--hosts-deny] [--file file] [IP]'
		print 'pydoc ./allow-ips.py for docs'
		sys.exit(1)
	
	work_dir = '/var/lib/denyhosts'
	if args[0] == '--work-dir':
		work_dir = args[1]
		del args[:2]

	hosts_deny = False
	if args[0] == '--hosts-deny':
		hosts_deny = True
		del args[:1]

	allow_file = False
	if args[0] == '--file':
		allow_file = args[1]
		ip_list = get_allow_ips(allow_file)
		del args[:2]

	# If the args has something in it, assume the IP to allow
	if args:
		ip_list.append(args[0])

	process_files(work_dir, work_files, ip_list)

	if hosts_deny:
		process_hosts_deny(ip_list)

if __name__ == '__main__':
  main()
