import subprocess
import re
import sys
import os
import time
from subprocess import call

# The list of SDcard Vendor and Product IDs - these will be used to check you are writing to the correct devices
VENDOR_PRODUCT_ID = "0bda:0109"
DEV_NAME_LIST = []
PARTITION_NAME_LIST = []

# Check am image file was given
# TODO: Add checks to confirm it is an image file
if (len(sys.argv) == 2):
	input_file = os.path.abspath("".join(sys.argv[1:]))

	# Getting the number of USB devices connected grepping for the correct IDs provided above
	# TODO: Make the IDs in to a list so we can use a variety of a sd card readers
	lsusb_proc = subprocess.Popen(["lsusb | grep 0bda:0109 | wc -l"], shell=True, stdout=subprocess.PIPE)
	data, err = lsusb_proc.communicate()
	usb_devices = int(data)

	# Get the dev paths of each connected drive
	lsblk_proc = subprocess.Popen(["lsblk -ln | awk '{print $1}'"], shell=True, stdout=subprocess.PIPE)

	sdcard_count = 0
	for line in lsblk_proc.stdout:
		# Check that it is the sd card readers we want by cycling through each drive and checking the IDs
		line = line.strip()
		udevadm_proc = subprocess.Popen(["udevadm info -q all -n " + line + " | grep \"0109\""], shell=True, stdout=subprocess.PIPE)
		for dev in udevadm_proc.stdout:
			m = re.search(r'\d+$', line)
			if m is None:
				# print line
				DEV_NAME_LIST.append(line)
				sdcard_count = sdcard_count + 1
			else:
				# print line
				umount_proc = subprocess.call(["sudo umount /dev/" + line], shell=True, stdout=subprocess.PIPE)

	print "Number of sdcard readers connected = " + str(usb_devices)
	print "Number of sdcards inserted = " + str(sdcard_count)
	answer = raw_input("Would you like to continue? (y/n)")

	if str(answer) == 'y':
		start_time = time.time()
		of_argument = ""
		for device in DEV_NAME_LIST:
			of_argument = of_argument + "of=/dev/" + device + " "
		command = "sudo dcfldd if=" + input_file + " statusinterval=2 bs=1M sizeprobe=if " + of_argument
		print command
		dd_command = subprocess.call([command], shell=True, bufsize=-1)
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
