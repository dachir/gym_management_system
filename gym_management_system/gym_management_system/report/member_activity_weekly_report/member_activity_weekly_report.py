# Copyright (c) 2022, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
import datetime

def execute(filters=None):
    #frappe.msgprint("<pre>{}</pre>".format(filters))
    columns = [
        {'fieldname':'name','label':'ID','fieldtype':'Data'},
        {'fieldname':'first_name','label':'First Name','fieldtype':'Data'},
        {'fieldname':'last_name','label':'Last Name','fieldtype':'Data'},
        {'fieldname':'creation','label':'Creation','fieldtype':'Date'}
    ]
    data = frappe.db.get_all('User', ['name','first_name','last_name','creation'])
    frappe.msgprint("<span style='color:Red;'>Once this popup has served it's purpose, then comment out it's invocation, viz. #frappe.msgprint...</span><br><br>" + "<pre>{}</pre>".format(frappe.as_json(data)))
    datefilter = datetime.datetime.strptime(filters.date_filter,"%Y-%m-%d").date()
    today = datetime.datetime.now(tz=None).date()
    data = [dic for dic in data if dic.creation.date() > datefilter]
    data = sorted(data, key=lambda k: k['first_name'])
    chart = {
        'title':"Script Chart Tutorial : Days since the user's database record was created",
        'data':{
            'labels':[str(dic.first_name) + " " + str(dic.last_name) for dic in data],
            'datasets':[{'values':[(today - dic.creation.date()).days for dic in data]}]
        },
        'type':'line',
        'height':300,
        'colors':['#F16A61'],
        'lineOptions':{'hideDots':0, 'dotSize':6, 'regionFill':1}
    }
    report_summary = [{"label":"Count","value":len(data),'indicator':'Red' if len(data) < 10 else 'Green'}]
    return columns, data, None, chart, report_summary
