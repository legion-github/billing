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
default_namespace   = ''


def logger(name, **kwargs):
	"""Sets up simple logging"""

	conf = config.read()

	if kwargs.get('syslog', True) and conf['logging']['type'] == 'syslog':
		return syslog(**kwargs)

	name          = kwargs.get('name', 'billing')
	log_level     = kwargs.get('level', conf['logging']['level'])
	log_file      = kwargs.get('log_file', conf['logging']['logdir']) + '/' + name + '.log'
	log_max_bytes = unitconvert.convert_from(conf['logging']['logsize'])
	log_count     = conf['logging']['backcount']
	log_format    = kwargs.get('log_format',  default_log_format)
	date_format   = kwargs.get('date_format', default_date_format)
	namespace     = kwargs.get('namespace',   default_namespace)

	log = logging.getLogger(namespace)
	log.setLevel(log_level_mapping[log_level])

	handler = logging.handlers.RotatingFileHandler(
		log_file,
		maxBytes = log_max_bytes,
		backupCount = log_count)

	handler.setFormatter(logging.Formatter(log_format, date_format))
	log.addHandler(handler)

	if not name:
		return log
	return logging.getLogger(namespace + "." + name)



def syslog(**kwargs):
	"""Sets up syslog logging"""

	conf = config.read()

	name          = kwargs.get('name', None)
	log_level     = kwargs.get('level', conf['logging']['level'])
	log_address   = kwargs.get('address', str(conf['logging']['address']))
	log_facility  = kwargs.get('facility', conf['logging']['facility'])
	log_format    = kwargs.get('log_format',  default_log_format)
	date_format   = kwargs.get('date_format', default_date_format)
	namespace     = kwargs.get('namespace',   default_namespace)

	log = logging.getLogger(namespace)
	log.setLevel(log_level_mapping[log_level])

	syslog = SysLogHandler(
		address = log_address,
		facility = SysLogHandler.facility_names[log_facility])

	formatter = logging.Formatter(log_format or '%(name)s: %(levelname)s: %(message)s',
	                              date_format or '%Y.%m.%d %H:%M:%S')

	syslog.setFormatter(formatter)
	log.addHandler(syslog)

	if not name:
		return log
	return logging.getLogger(namespace + "." + name)
