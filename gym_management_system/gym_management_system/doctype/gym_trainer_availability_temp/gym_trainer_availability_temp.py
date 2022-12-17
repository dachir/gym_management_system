# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GymTrainerAvailabilityTemp(Document):
	
	def db_insert(self):
		pass

	def load_from_db(self):
		pass

	def db_update(self):
		pass

	@staticmethod
	def get_list(args,avails):
		#avails = get_availability(args.name)
		trainer_availability = []

		for row in avails.find():
			trainer_availability.append({
				**row,
				"_id": str(row["_id"])
			})

		return trainer_availability

	def get_count(self, args):
		pass

	def get_stats(self, args):
		pass

def get_availability(name):
	avails = frappe.db.sql(
	"""
		SELECT  CONCAT(a.name,r.name) as name, a.parent, a.parentfield, a.parenttype, a.gym_day, a.start_time, a.end_time, r.workout_plan, CONCAT(r.plan_name, ' ', r.level) AS description
		FROM `tabGym Trainer Availability` a  CROSS JOIN `tabGym Workout Plan Register` r
		WHERE parent = %s
		ORDER BY parent, gym_day, start_time 
	""",(name),as_dict = 1)
	return avails
