# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
from frappe.utils import add_days
from frappe.model.docstatus import DocStatus

class GymMembership(Document):
	
	def validate(self):
		nb_days = frappe.db.get_single_value("Gym Settings", "number_of_days")
		self.to_date = add_days(self.from_date, nb_days or 30)

	# check before submitting this document
	def before_submit(self): 
		exists = frappe.db.exists(
			"Gym Membership",
			{
				"gym_member": self.gym_member,
				"docstatus": DocStatus.submitted(),
				# check if the membership's end date is later than this membership's start date
				"to_date": (">", self.from_date),
			},
		)
		if exists:
			frappe.throw("There is an active membership for this member") 


def process_workout_plan(json_params, messages,message):
	if len(json_params["ids"]) == 0 :
		message = "Select at least one plan, please!!! \n"
		messages.append({
					"type": "error",
					"message": message,
				})
	for i in json_params["ids"]:
		#frappe.msgprint(json_params["doctype"])
		gwp = frappe.get_doc("Gym Trainer Availability Details", i)
		#Check if Time slot exists in member table
		nb  = frappe.db.sql(
				"""
					SELECT count(*) 
					FROM `tabGym Membership Timing` 
					WHERE gym_day = %(gym_day)s 
						AND start_time BETWEEN %(start_time)s AND %(end_time)s
						AND end_time BETWEEN %(start_time)s AND %(end_time)s
						AND parent = %(parent_id)s
				""",{"gym_day": gwp.day, "start_time":gwp.start_time, "end_time":gwp.end_time, "parent_id":json_params["parent_id"]}
			)[0][0]

		if nb == 0:
			nb  = frappe.db.sql(
				"""
					SELECT count(*) 
					FROM `tabGym Member Appointment` 
					WHERE day = %(day)s 
						AND start_time >= %(start_time)s AND start_time >= %(end_time)s
						AND end_time <= %(start_time)s AND end_time <= %(end_time)s
						AND parent = %(parent)s
				""",{"day": gwp.day, "start_time":gwp.start_time, "end_time":gwp.end_time, "parent":gwp.parent}
			)[0][0]

			#if yes Check if Time slot exists in Trainer table
			if nb == 0:
				
				#if yes Save member appointments
				args = frappe._dict({
					'doctype': 'Gym Membership Timing',
					'parent': json_params["parent_id"],
					'parentfield': "timing",
					'parenttype': "Gym Membership",
					'gym_day': gwp.day,
					'start_time': gwp.start_time,
					'end_time': gwp.end_time,
					'gym_trainer': gwp.parent,
					'class_type': 'Gym Workout Plan',
					'class': gwp.workout_plan,
					'description': gwp.description,
				})
				ma = frappe.get_doc(args)
				#frappe.msgprint(str(ma))
				ma.insert()

				#if yes Save Trainer appointments
				args = frappe._dict({
					'doctype': 'Gym Member Appointment',
					'parent': gwp.parent,
					'parentfield': "member_appointment",
					'parenttype': "Gym Trainer",
					'gym_membership': json_params["parent_id"],
					'full_name': gwp.start_time,
					'program': gwp.description,
					'day': gwp.day,
					'start_time': gwp.start_time,
					'end_time': gwp.end_time,
				})
				ta = frappe.get_doc(args)
				#frappe.msgprint(str(ta))
				ta.insert()

				#check which machine might be used#########
				machines = frappe.db.sql(
					"""
						SELECT DISTINCT e.machine
						FROM `tabGym Membership Timing` t INNER JOIN `tabGym Workout Plan Exercice` e ON t.class = e.parent
						WHERE t.parent = %s AND NOT e.machine IS NULL
					""", (json_params["parent_id"]), as_dict = 1
				)
				for m in machines:
					#if not exist in member machine add it
					count = frappe.db.sql(
							"""
								SELECT count(*)
								FROM `tabGym Machine Booking`
								WHERE gym_machine = %s
							""",(m.machine)
						)[0][0]
					if count == 0 :
						mac = frappe.get_doc({
							'doctype': 'Gym Machine Booking',
							'gym_machine': m.machine,
							'parent': json_params["parent_id"],
							'parentfield': "gym_machine_booking",
							'parenttype': "Gym Membership",
						})
						#frappe.msgprint(str(mac))
						mac.insert()

				#check which metrics might be used###########
				metrics = frappe.db.sql(
					"""
						SELECT DISTINCT m.metric
						FROM `tabGym Membership Timing` t INNER JOIN `tabGym Metric Needed` m ON t.class = m.parent
						WHERE t.parent = %s
					""", (json_params["parent_id"]), as_dict = 1
				)
				for m in metrics:
					#if not exist in member metrics add it
					count = frappe.db.sql(
							"""
								SELECT count(*)
								FROM `tabGym Metric Used`
								WHERE gym_metric = %s
							""",(m.metric)
						)[0][0]
					if count == 0 :
						met = frappe.get_doc({
							'doctype': 'Gym Metric Used',
							'gym_metric': m.metric,
							'parent': json_params["parent_id"],
							'parentfield': "metric_used",
							'parenttype': "Gym Membership",

						})
						#frappe.msgprint(str(met))
						met.insert()
				
				message = "Your appointment of %s from %s to %s is recorded. \n" % (gwp.day, gwp.start_time, gwp.end_time)
				messages.append({
					"type": "success",
					"message": message,
				})
			else:
				message = "Coach %s has another appointment for %s from %s to %s!!! \n" % (gwp.parent, gwp.day, gwp.start_time, gwp.end_time)
				messages.append({
					"type": "error",
					"message": message,
				})
		else:
			message = "You have an appointment recorded on %s from %s to %s is recorded!!! \n" % (gwp.day, gwp.start_time, gwp.end_time)
			messages.append({
					"type": "error",
					"message": message,
				})
	return messages

def process_group_class(json_params, messages,message):
	if len(json_params["ids"]) == 0 :
		message = "Select at least one group class, please!!! \n"
		messages.append({
					"type": "error",
					"message": message,
				})
	for i in json_params["ids"]:
		#frappe.msgprint(json_params["doctype"])
		gwp = frappe.db.sql(
				"""
					SELECT p.*, t.name as trainer, t.class_name as description
					FROM `tabGym Program` p INNER JOIN `tabGym Trainer` t ON t.gym_class = p.parent
					WHERE p.name =  %s
				""",(i), as_dict  = 1
			)[0]
		#Check if Time slot already exists in member table
		nb  = frappe.db.sql(
				"""
					SELECT count(*) 
					FROM `tabGym Membership Timing` 
					WHERE gym_day = %(gym_day)s 
						AND start_time BETWEEN %(start_time)s AND %(end_time)s
						AND end_time BETWEEN %(start_time)s AND %(end_time)s
						AND parent = %(parent_id)s
				""",{"gym_day": gwp.gym_day, "start_time":gwp.start_time, "end_time":gwp.end_time, "parent_id":json_params["parent_id"]}
			)[0][0]

		if nb == 0:
				
			#if yes Save member appointments
			args = frappe._dict({
				'doctype': 'Gym Membership Timing',
				'parent': json_params["parent_id"],
				'parentfield': "timing",
				'parenttype': "Gym Membership",
				'gym_day': gwp.gym_day,
				'start_time': gwp.start_time,
				'end_time': gwp.end_time,
				'gym_trainer': gwp.trainer,
				'class_type': 'Gym Class',
				'class': gwp.parent,
				'description': gwp.description,
			})
			ma = frappe.get_doc(args)
			#frappe.msgprint(str(ma))
			ma.insert()
			
			#check which metrics might be used###########
			machines = frappe.db.sql(
					"""
						SELECT DISTINCT e.machine
						FROM `tabGym Membership Timing` t INNER JOIN `tabGym Workout Plan Exercice` e ON t.class = e.parent
						WHERE t.parent = %s AND NOT e.machine IS NULL
					""", (json_params["parent_id"]), as_dict = 1
				)
			for m in machines:
					#if not exist in member machine add it
					count = frappe.db.sql(
							"""
								SELECT count(*)
								FROM `tabGym Machine Booking`
								WHERE gym_machine = %s
							""",(m.machine)
						)[0][0]
					if count == 0 :
						mac = frappe.get_doc({
							'doctype': 'Gym Machine Booking',
							'gym_machine': m.machine,
							'parent': json_params["parent_id"],
							'parentfield': "gym_machine_booking",
							'parenttype': "Gym Membership",
						})
						#frappe.msgprint(str(mac))
						mac.insert()

			#check which metrics might be used###########
			metrics = frappe.db.sql(
				"""
					SELECT DISTINCT m.metric
					FROM `tabGym Membership Timing` t INNER JOIN `tabGym Metric Needed` m ON t.class = m.parent
					WHERE t.parent = %s
				""", (json_params["parent_id"]), as_dict = 1
			)
			for m in metrics:
				#if not exist in member metrics add it
				count = frappe.db.sql(
						"""
							SELECT count(*)
							FROM `tabGym Metric Used`
							WHERE gym_metric = %s
						""",(m.metric)
					)[0][0]
				if count == 0 :
					met = frappe.get_doc({
						'doctype': 'Gym Metric Used',
						'gym_metric': m.metric,
						'parent': json_params["parent_id"],
						'parentfield': "metric_used",
						'parenttype': "Gym Membership",

					})
					#frappe.msgprint(str(met))
					met.insert()
		
			message = "Your appointment of %s from %s to %s is recorded. \n" % (gwp.gym_day, gwp.start_time, gwp.end_time)
			messages.append({
				"type": "success",
				"message": message,
			})
		else:
			message = "You have an appointment recorded on %s from %s to %s is recorded!!! \n" % (gwp.gym_day, gwp.start_time, gwp.end_time)
			messages.append({
					"type": "error",
					"message": message,
				})
	return messages

@frappe.whitelist()
def activity_registration(params):
	json_params = json.loads(params)
	messages = []
	message = ""
	if json_params["allow_child_item_selection"] == 1: 
		if(json_params["doctype"] == "Gym Workout Plan"):
			return process_workout_plan(json_params, messages,message)
		else:
			return process_group_class(json_params, messages,message)
	
	else:
		message = "Check ---Select Gym Trainer Availability Details--- Box, please!!! \n"
		messages.append({
				"type": "error",
				"message": message,
			})

	return messages
		
					
				

	