#!/usr/bin/python

import re

UNITS = {}

def add_unit(typ, k, suffix, alias):
	if typ not in UNITS:
		UNITS[typ] = {
			'direct':  {},
			'reverse': {},
		}

	value = ((k[1] * k[0] ** k[2]) + k[3])

	UNITS[typ]['direct'][suffix.lower()] = value
	for n in alias:
		UNITS[typ]['direct'][n.lower()] = value

	UNITS[typ]['reverse'][value] = suffix


add_unit('byte_binary', [2,1, 0,0], 'B',   ['byte','bytes'])
add_unit('byte_binary', [2,1,10,0], 'KiB', ['kibibyte','kibibytes'])
add_unit('byte_binary', [2,1,20,0], 'MiB', ['mebibyte','mebibytes'])
add_unit('byte_binary', [2,1,30,0], 'GiB', ['gebibyte','gebibytes'])
add_unit('byte_binary', [2,1,40,0], 'TiB', ['tebibyte','tebibytes'])
add_unit('byte_binary', [2,1,50,0], 'PiB', ['pebibyte','pebibytes'])
add_unit('byte_binary', [2,1,60,0], 'EiB', ['exbibyte','exbibytes'])
add_unit('byte_binary', [2,1,70,0], 'ZiB', ['zebibyte','zebibytes'])
add_unit('byte_binary', [2,1,80,0], 'YiB', ['yobibyte','yobibytes'])

add_unit('byte_decimal', [10,1, 0,0], 'B',  ['byte','bytes'])
add_unit('byte_decimal', [10,1, 3,0], 'KB', ['kilobyte','kilobytes'])
add_unit('byte_decimal', [10,1, 6,0], 'MB', ['megabyte','megabytes'])
add_unit('byte_decimal', [10,1, 9,0], 'GB', ['gigabyte','gigabytes'])
add_unit('byte_decimal', [10,1,12,0], 'TB', ['terabyte','terabytes'])
add_unit('byte_decimal', [10,1,15,0], 'PB', ['petabyte','petabytes'])
add_unit('byte_decimal', [10,1,18,0], 'EB', ['exabyte','exabytes'])
add_unit('byte_decimal', [10,1,21,0], 'ZB', ['zettabyte','zettabytes'])
add_unit('byte_decimal', [10,1,24,0], 'YB', ['yottabyte','yottabytes'])

add_unit('time', [60,1,  0,0], 'Sec',  ['second','seconds'])
add_unit('time', [60,1,  1,0], 'Min',  ['minute','minutes'])
add_unit('time', [60,1,  2,0], 'Hour', ['hours'])
add_unit('time', [60,24, 2,0], 'Day',  ['days'])
add_unit('time', [60,168,2,0], 'Week', ['weeks'])


def convert_from(x):
	parts = re.findall(r'^([0-9.]+)(.*)$', x)
	if not parts:
		return None

	num = parts[0][0].strip()
	suf = parts[0][1].lower().strip()

	if '.' in num:
		value = float(num)
	else:
		value = long(num)

	for t,u in UNITS.iteritems():
		if suf in u['direct']:
			return (value * u['direct'][suf],t)


def convert_to(typ, x):
	if typ not in UNITS:
		raise ValueError("type not found")

	arr = UNITS[typ]['reverse'].keys()
	arr.sort()
	arr.reverse()

	for n in arr:
		if n > x:
			continue
		y = x / n
		if (y * n) != x:
			y = float(x) / n
		return (y, UNITS[typ]['reverse'][n])
	return None
