
SCHEMA = {
	'metrics': """
			CREATE TABLE `{0}` (
			  `id` varchar(128) NOT NULL,
			  `type` varchar(32) NOT NULL,
			  `formula` varchar(32) NOT NULL,
			  `aggregate` tinyint(1) NOT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",

	'queue': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `customer` varchar(36) NOT NULL,
			  `rid` varchar(36) NOT NULL,
			  `rate` bigint(20) NOT NULL DEFAULT '0',
			  `state` int NOT NULL,
			  `value` bigint(8) NOT NULL DEFAULT '1',
			  `time_check` int(11) NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL DEFAULT '0',
			  `target_user` varchar(36) DEFAULT '',
			  `target_uuid` varchar(36) DEFAULT '',
			  `target_descr` varchar(36) DEFAULT '',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `target_uuid_UNIQUE` (`target_uuid`),
			  KEY `search_INDEX` USING BTREE (`state`,`time_check`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'rates': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `metric_id` varchar(128) NOT NULL,
			  `tariff_id` varchar(36) NOT NULL,
			  `rate` bigint(20) NOT NULL,
			  `currency` int NOT NULL,
			  `state` int NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL,
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`state`,`metric_id`,`tariff_id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'tariffs': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `name` varchar(64) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL,
			  `state` int NOT NULL,
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`state`,`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'customers': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `login` varchar(64) NOT NULL,
			  `name_short` varchar(255)  NOT NULL,
			  `name_full` varchar(1024) NOT NULL DEFAULT '',
			  `comment` varchar(1024) NOT NULL DEFAULT '',
			  `contract_client` varchar(255) NOT NULL DEFAULT '',
			  `contract_service` varchar(255) NOT NULL DEFAULT '',
			  `tariff_id` varchar(36) NOT NULL DEFAULT '',
			  `contact_person` varchar(255) NOT NULL DEFAULT '',
			  `contact_email` varchar(255) NOT NULL DEFAULT '',
			  `contact_phone` varchar(30) NOT NULL DEFAULT '',
			  `state` int NOT NULL DEFAULT '0',
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL DEFAULT '0',
			  `wallet` bigint NOT NULL DEFAULT '0',
			  `wallet_mode` int NOT NULL DEFAULT '0',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `main_UNIQUE` (`login`, `state`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
	""",
	'auth': """
			CREATE TABLE `{0}` (
			  `role` varchar(64) NOT NULL,
			  `method` varchar(64) NOT NULL,
			  `secret` varchar(1024) NOT NULL,
			  `host` varchar(255) NOT NULL DEFAULT '',
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`role`, `method`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
	""",
}
