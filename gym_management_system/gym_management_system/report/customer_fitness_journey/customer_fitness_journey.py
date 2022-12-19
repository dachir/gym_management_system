# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
import datetime


def execute(filters=None):
    #frappe.msgprint("<pre>{}</pre>".format(filters))
    columns = [
        {'fieldname':'gym_membership','label':'ID','fieldtype':'Data'},
        {'fieldname':'full_name','label':'Full Name','fieldtype':'Data'},
        {'fieldname':'gym_trainer','label':'Trainer','fieldtype':'Data'},
		{'fieldname':'class_name','label':'Class Name','fieldtype':'Data'},
		{'fieldname':'year_of_event','label':'Year','fieldtype':'Int'},
		{'fieldname':'month_of_event','label':'Month','fieldtype':'Int'},
		{'fieldname':'monthname_of_event','label':'Month Name','fieldtype':'Data'},
		{'fieldname':'rating','label':'Rating','fieldtype':'Float'},
		{'fieldname':'gym_metric','label':'Metric','fieldtype':'Data'},
		{'fieldname':'unit','label':'Unit','fieldtype':'Data'},
		{'fieldname':'value','label':'Value','fieldtype':'float'},
        {'fieldname':'attendance','label':'Attendance','fieldtype':'Float'}
    ]
    data = frappe.db.sql(
		"""
		SELECT a.gym_membership, a.full_name, a.gym_trainer, YEAR(a.date) AS year_of_event, MONTH(a.date) AS month_of_event, MONTHNAME(a.date) AS monthname_of_event,a.group_class, 
			CASE WHEN c.class_name IS NULL THEN 'Fitness' ELSE c.class_name END AS class_name, 
			AVG(a.rating) AS rating, m.gym_metric, m.unit, AVG(m.value) AS value, COUNT(a.name) AS attendance
		FROM `tabGym Member Daily Appointment` a INNER JOIN `tabGym Member Metric Submission` m on m.parent = a.name LEFT JOIN `tabGym Class` c ON a.group_class = c.name
		WHERE a.docstatus <> 2
		GROUP BY a.gym_membership, a.full_name, a.gym_trainer, MONTH(a.date), m.unit,m.gym_metric,a.group_class, c.class_name, YEAR(a.date), MONTHNAME(a.date) 
		ORDER BY YEAR(a.date),MONTH(a.date), a.gym_membership, m.gym_metric
		""", as_dict = 1
	)
    #frappe.msgprint("<span style='color:Red;'>Once this popup has served it's purpose, then comment out it's invocation, viz. #frappe.msgprint...</span><br><br>" + "<pre>{}</pre>".format(frappe.as_json(data)))
    #datefilter = datetime.datetime.strptime(filters.date_filter,"%Y-%m-%d").date()
    #today = datetime.datetime.now(tz=None).date()
    #data = [dic for dic in data if dic.creation.date() > datefilter]
    #data = sorted(data, key=lambda k: k['first_name'])
    chart = {
        'title':"Script Chart Tutorial : Days since the user's database record was created",
        'data':{
            'labels':[str(dic.monthname_of_event) + " " + str(dic.gym_metric) for dic in data],
            'datasets':[
							{'name':'Rating','values':[dic.rating for dic in data],'chartType':'bar'},
							{'name':'Value','values':[dic.value for dic in data],'chartType':'bar'},
							{'name':'Attendance','values':[dic.attendance for dic in data],'chartType':'line'},
			           ]
        },
        'type':'line',
        'height':300,
        'colors':['#F16A61'],
        'lineOptions':{'hideDots':0, 'dotSize':6, 'regionFill':1}
    }
    report_summary = [{"label":"Count","value":len(data),'indicator':'Red' if len(data) < 10 else 'Green'}]
    return columns, data, None, chart, report_summary
