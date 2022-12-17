from __future__ import unicode_literals
import frappe

def message_body(activities, current_week):
    msg = """
            <pre>
            Hi %(full_name)s;
            During week %(number)s starting from %(first_day)s to %(last_day)s, on:
            <ul>
          """ % {"full_name":activities[0].full_name, "number":current_week.number, "first_day":current_week.first_day,"last_day":current_week.last_day,}
    array_message = []
    for activity in activities:
        array_message.append  ("""
                <li>%(gym_day)s %(date)s from %(real_start_time)s to %(real_end_time)s you participated in the 
                following activities {%(exercises_done)s}. your metrics was {%(metrics)s}. Your rating was %(rating)s.
                Coach notes: %(coach_note)s
                </li>
               """ % {
                        "gym_day":activity.gym_day, 
                        "date":activity.date, 
                        "real_start_time":activity.real_start_time,
                        "real_end_time":activity.real_end_time,
                        "exercises_done":activity.exercises_done, 
                        "metrics":activity.metrics, 
                        "rating":activity.rating,
                        "coach_note":activity.coach_note,
                    })
    end_msg = """
            </ul>
        </pre>
    """

    return msg + ''.join(array_message) + end_msg

def weekly():
    #current_week = frappe.db.sql(
    #    """
    #    SELECT date_add(curdate(), interval  -WEEKDAY(curdate())-1 day) first_day, 
    #           date_add(date_add(curdate(), interval  -WEEKDAY(curdate())-1 day), interval 6 day) last_day,
    #           week(curdate()) number;
    #    """, as_dict = 1
    #)[0]
    fake_current_week = frappe.db.sql(
        """
        SELECT date_add('2022-12-05', interval  -WEEKDAY('2022-12-05')-1 day) first_day, 
               date_add(date_add('2022-12-05', interval  -WEEKDAY('2022-12-05')-1 day), interval 6 day) last_day,
               week('2022-12-05') week_number;
        """, as_dict = 1
    )[0]
    email_ids = frappe.db.sql(
        """
        SELECT DISTINCT m.gym_member AS email
        FROM `tabGym Membership` m
        WHERE %s BETWEEN m.from_date AND m.to_date
        AND m.docstatus <> 2
        """, (fake_current_week.first_day)
    )
    for id in email_ids:
        member_weekly_activities = frappe.db.sql(
            """
            SELECT t.*, e.description as coach_note, e.start_time as real_start_time, e.end_time as real_end_time, GROUP_CONCAT(exercice_name) AS exercises_done
            FROM
            (
                SELECT m.name as membership, m.gym_member AS email, m.full_name, DATE(a.date) AS `date`, t.class, t.description, t.gym_day, t.start_time, t.end_time, a.gym_trainer, a.rating, 
                GROUP_CONCAT(CONCAT(gym_metric, ' : ',CAST(CAST(value AS DECIMAL(7,2)) AS CHAR))) AS metrics
                FROM `tabGym Membership Timing` t INNER JOIN `tabGym Membership` m ON m.name = t.parent INNER JOIN `tabGym Member Daily Appointment` a ON m.name = a.gym_membership AND t.gym_day = a.day 
                AND TIME(ADDTIME(a.date,'01:00:00')) BETWEEN TIMESTAMPADD(HOUR,-1,t.start_time) AND TIMESTAMPADD(HOUR,1,t.start_time) LEFT JOIN `tabGym Member Metric Submission` s ON s.parent = a.name
                WHERE m.docstatus <> 2  
                GROUP BY m.name, m.gym_member, m.full_name, DATE(a.date), t.class, t.description, t.gym_day, t.start_time, t.end_time, a.gym_trainer, a.rating
            ) AS t LEFT JOIN `tabGym Class Daily Exercice` e ON t.class = e.gym_class AND t.gym_day = e.day AND e.start_time BETWEEN TIMESTAMPADD(HOUR,-1,t.start_time) AND TIMESTAMPADD(HOUR,1,t.start_time)
            LEFT JOIN `tabGym Class Daily Exercice Details` d ON d.parent = e.name
            WHERE t.date BETWEEN %s AND %s AND t.email = %s
            GROUP BY t.membership, t.email, t.full_name, t.date, t.class, t.description, t.gym_day, t.start_time, t.end_time, t.gym_trainer, t.rating, t.metrics, e.description, e.start_time, e.end_time
            """, (fake_current_week.first_day, fake_current_week.last_day, id), as_dict = 1
        )

        if len(member_weekly_activities) > 0:
            msg = message_body(member_weekly_activities, fake_current_week)
            frappe.sendmail(
				recipients=id, subject="Weekly Report", message=msg
			)
    
