import sys
import logging
from logging.handlers import SysLogHandler

from bc import config
from bc import unitconvert

log_level_mapping = {
	"debug":   logging.DEBUG,
	"info":    logging.INFO,
	"warning": logging.WARNING,
	"error":   logging.ERROR
}

default_log_format  = '%(asctime)s.%(msecs)03d: %(levelname)s: %(filename)s: %(lineno)d: %(message)s'
default_date_format = '%Y.%m.%d %H:%M:%S'

LOGGER = None

def logger(subname, **kwargs):
	global LOGGER

	if LOGGER:
		return LOGGER

	conf      = config.read()
	log_type  = kwargs.get('type', conf['logging']['type']) or 'syslog'
	log_level = log_level_mapping[kwargs.get('level', conf['logging']['level']).lower()]

	if log_type == 'file':
		name          = kwargs.get('name', 'billing')
		log_file      = kwargs.get('log_file', conf['logging']['logdir']) + '/' + name + '.log'
		log_max_bytes = unitconvert.convert_from(conf['logging']['logsize'])
		log_count     = conf['logging']['backcount']

		handler = logging.handlers.RotatingFileHandler(
			log_file,
			maxBytes=log_max_bytes,
			backupCount=log_count)

	elif log_type == 'syslog':
		log_address   = kwargs.get('address', str(conf['logging']['address']))
		log_facility  = kwargs.get('facility', conf['logging']['facility'])

		handler = SysLogHandler(
			address=log_address,
			facility=SysLogHandler.facility_names[log_facility])

	elif log_type == 'stderr':
		handler = logging.StreamHandler(sys.stderr)

	LOGGER = logging.getLogger()
	LOGGER.setLevel(log_level)

	handler.setFormatter(logging.Formatter(
		kwargs.get('log_format',  default_log_format),
		kwargs.get('date_format', default_date_format)))

	LOGGER.addHandler(handler)

	return LOGGER
