import logging, time, sys 
from datetime import date, datetime
from c2 import mongodb

from billing import constants as b_constants
from billing import utils
from billing import tariffs
from billing import customers

from bc.queue import BC_QUEUES


def billing_float_nice(arg):
	"format float value to string for WebUI"
	return "{0:.2f}".format(float(utils.rate_to_money(str(arg))))


def billing_float_ugly(arg):
	"format float value to string for WebUI"
	return (utils.rate_to_money(str(arg)))


class pseudo_dict(dict):
	def __getitem__(self, key):

		if key not in self.keys():
			dict.__setitem__(self, key, {})
			return dict.__getitem__(self, key)
		else:
			return dict.__getitem__(self, key)


class report(object):
	def __init__(self, customer_id, start_time, stop_time):
		self.__dict__.update(locals())
		self.total=0
		self.items=pseudo_dict()
		self.tariff_types=pseudo_dict()
		self.currency=customers.get(customer_id)["tariff_currency"]
		self.__get_data()
		self.__user_dict={}
		self.__tariff_dict={}


	def __parse(self, task):
		start_time = task["time-create"]
		stop_time = task["time-destroy"]
		queue = task["queue"]
		info = task["info"]
		tariff_id = task["tariff"]
		userid = task["user"]
		if queue == "billing-addresses":
			uuid = task["info"]["addrs"]
		elif queue == "billing-traffic":
			uuid = task["info"]["ip"]
		elif queue == "billing-volumes-io":
			uuid = task["info"]["volume_uuid"]
		else:
			uuid = task["info"]["uuid"]
		return (uuid, start_time, stop_time, queue, info, tariff_id, userid) 


	def __update(self, task, money):
		uuid, start_time, stop_time, queue, info, tariff_id, userid = self.__parse(task)
		tariff_type = BC_QUEUES[queue]['describe'](info)
		key = '.'.join([tariff_id,uuid])
		if not money:
			money = 0
		if key not in self.items.keys():
			self.items[key]={"money":money,
					"start_time":start_time,
					"stop_time":stop_time,
					"info":BC_QUEUES[queue]['get_name'](info),
					"type":tariff_type,
					"tariff_id":tariff_id,
					"uuid":uuid,
					"user_id":userid,
					}
		else:
			self.items[key]["money"] += money
			if self.items[key]["start_time"] > start_time:
				self.items[key]["start_time"] = start_time
			if 0 < self.items[key]["stop_time"] < stop_time or stop_time == 0:
				self.items[key]["stop_time"] = stop_time

		if tariff_type not in self.tariff_types[tariff_id].keys():
			self.tariff_types[tariff_id][tariff_type] = money
		else:
			self.tariff_types[tariff_id][tariff_type] += money

		self.total += money


	def __get_data(self):
		"""
		create report from billing queues
		"""
		query_dead = {"time-create":{"$lt":self.stop_time},
				"customer":self.customer_id,
				"time-destroy":{"$gt":self.start_time}}

		query_live = {"time-create":{"$lt":self.stop_time},
				"customer":self.customer_id,
				"time-destroy":0}


		for queue in b_constants.BC_QUEUES:
			dead = mongodb.billing_collection("queue-"+queue).find(query_dead)
			live = mongodb.billing_collection("queue-"+queue).find(query_live)

			for i in dead:
				temp = i

				if temp['time-destroy'] > self.stop_time:
					temp['time-destroy'] = self.stop_time

				if temp['time-create'] < self.start_time:
					temp['time-create'] = self.start_time

				temp['time-check'] = temp['time-create']
				self.__update(temp, BC_QUEUES[queue]['withdraw'](temp)[1])
			
			for i in live:
				temp = i
				temp['time-check'] = 0
				temp['time-destroy'] = self.stop_time
				
				if temp['time-create'] < self.start_time:
					temp['time-create'] = self.start_time

				temp['time-check'] = temp['time-create']
				self.__update(temp, BC_QUEUES[queue]['withdraw'](temp)[1])


	def __normolize_names(self, tariff_id, name):
		if name.startswith("os_types"):
			return " ".join(tariffs.describe_ostypes(tariff_id, name.split(".")[1]))
		else:
			return "_".join(name.split("."))


	def __user_names(self, user_id):
		if not user_id in self.__user_dict.keys():
			self.__user_dict[user_id]=mongodb.billing_collection("log_accounts").find_one({"user":user_id}, ["name"])["name"]
		return self.__user_dict[user_id]


	def __tariff_names(self, tariff_id):
		if not tariff_id in self.__tariff_dict.keys():
			self.__tariff_dict[tariff_id]=tariffs.get(tariff_id)["name"]
		return self.__tariff_dict[tariff_id]

	def format_simple_report(self):
		answer=[]
		for tariff_id in self.tariff_types:
			for tariff_type in self.tariff_types[tariff_id]:
				self.tariff_types[tariff_id][tariff_type] = billing_float_nice(self.tariff_types[tariff_id][tariff_type])
				answer.append({"name":self.__normolize_names(tariff_id, tariff_type),
					"value":self.tariff_types[tariff_id][tariff_type],
					"tariff":tariff_id,
					"tariff_name":self.__tariff_names(tariff_id)})
		return {"total": billing_float_nice(self.total),
				"report": answer,
				"currency": self.currency} 


	def format_detailed_report(self):
		for i in self.items:
				self.items[i]["type"] = self.__normolize_names(self.items[i]["tariff_id"], self.items[i]["type"])
				self.items[i]["money"] = float(billing_float_ugly(self.items[i]["money"]))
				self.items[i]["start_time"] = datetime.fromtimestamp(self.items[i]["start_time"])
				self.items[i]["stop_time"] = datetime.fromtimestamp(self.items[i]["stop_time"])
				self.items[i]["tariff_id"] = self.__tariff_names(self.items[i]["tariff_id"])
				self.items[i]["user_id"] = self.__user_names(self.items[i]["user_id"])
		return {"total": billing_float_ugly(self.total),
				"report": self.items.values(),
				"currency": self.currency}

