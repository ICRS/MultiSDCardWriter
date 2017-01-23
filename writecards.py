import subprocess
import re
import sys
import os
import time
from subprocess import call


VENDOR_PRODUCT_ID = "0bda:0109"
DEV_NAME_LIST = []

if (len(sys.argv) == 2):
	input_file = os.path.abspath("".join(sys.argv[1:]))

	lsusb_proc = subprocess.Popen(["lsusb | grep 0bda:0109 | wc -l"], shell=True, stdout=subprocess.PIPE)
	data, err = lsusb_proc.communicate()
	usb_devices = int(data)

	lsblk_proc = subprocess.Popen(["lsblk -ln | awk '{print $1}'"], shell=True, stdout=subprocess.PIPE)

	sdcard_count = 0
	for line in lsblk_proc.stdout:
		# line = proc.stdout
		line = line.strip()
		m = re.search(r'\d+$', line)
		if m is None:
			udevadm_proc = subprocess.Popen(["udevadm info -q all -n " + line + " | grep \"0109\""], shell=True, stdout=subprocess.PIPE)
			for dev in udevadm_proc.stdout:
				DEV_NAME_LIST.append(line)
				sdcard_count = sdcard_count + 1
				# subprocess.call(["umount "])

	print "Number of sdcard readers connected = " + str(usb_devices)
	print "Number of sdcards inserted = " + str(sdcard_count)
	answer = raw_input("Would you like to continue? (y/n)")

	if str(answer) == 'y':
		start_time = time.time()
		of_argument = ""
		for device in DEV_NAME_LIST:
			of_argument = of_argument + "of=/dev/" + device + " "
		command = "sudo dcfldd if=" + input_file + " statusinterval=64 bs=1M sizeprobe=if " + of_argument
		print command
		dd_command = subprocess.call([command], shell=True)
		# dd_command = subprocess.call(["sudo dcfldd if=/home/icrs/Desktop/shrunkimage.img statusinterval=64 bs=1M sizeprobe=if of=/dev/sdb"], shell=True)
		# for line in iter(dd_command.stdout.readline(), ""):
			# print line
		# dd_command.communicate()
		print("--- %s seconds ---" % round((time.time() - start_time)),2)

	else:
		print "Quitting.... "
		quit()
else:
	print "Incorrect number of arguments - please provide the input file"