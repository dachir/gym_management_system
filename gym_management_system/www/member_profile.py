from __future__ import unicode_literals
import frappe
from frappe.utils import now, date_diff

def get_context(context):
    #user_email = frappe.db.get_value("User", frappe.session.user, ["email"])
    user_email = "richard_amouzou@yahoo.fr"
    membership = frappe.get_list("Gym Membership", 
        fields = ["*"],
        filters = {
            "from_date": ['<=', now()],
            "to_date": ['>=', now()],
            "gym_member": user_email
        },
        limit = 1
    )

    trainers = frappe.get_list("Gym Membership Timing", 
        fields = ["gym_trainer"],
        filters = {
            "parent": membership[0].name,
        },
        group_by='gym_trainer'
    )
    real_trainers = [t for t in trainers if t['gym_trainer'] != None] # [{'gym_trainer': 'Patrick NGANGU'}]

    trainers = []
    for t in real_trainers:
        trainers.append(t.gym_trainer)

    context.active_plan =  frappe._dict({
        "membership" : membership[0].name,
        "membership_type" : membership[0].membership_type,
        "from_date" : membership[0].from_date,
        "to_date": membership[0].to_date,
        "remaining_days": date_diff(membership[0].to_date,now()),
        "trainers" : ''.join(trainers),
    })

    #///// All plans
    memberships = frappe.get_list("Gym Membership", 
        fields = ["*"],
        filters = {
            #"from_date": ['<=', now()],
            #"to_date": ['>=', now()],
            "gym_member": user_email
        },
        order_by= "to_date"
    )
    plans = []
    for membership in memberships:
        trainers = frappe.get_list("Gym Membership Timing", 
            fields = ["gym_trainer"],
            filters = {
                "parent": membership.name
            },
            group_by='gym_trainer'
        )
        real_trainers = [t for t in trainers if t['gym_trainer'] != None] # [{'gym_trainer': 'Patrick NGANGU'}]

        trainers = []
        for t in real_trainers:
            trainers.append(t.gym_trainer)

        plan =  frappe._dict({
            "membership" : membership.name,
            "membership_type" : membership.membership_type,
            "from_date" : membership.from_date,
            "to_date": membership.to_date,
            "remaining_days": date_diff(membership.to_date,now()),
            "trainers" : ''.join(trainers),
        })
        if plan != context.active_plan :
            plans.append(plan)
    
    context.past_plans = plans

     


