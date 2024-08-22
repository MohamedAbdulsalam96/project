
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import getdate
import pytz

class PMOMeetings(Document):
    def before_save(self):
        if self.meeting_type in ['Daily (Planned)', 'Weekly (Planned)', 'Monthly (Planned)']:
            if not self.attach_plan_sheet:
                frappe.throw("You have selected {} so please attach plan sheet".format(self.meeting_type))

    @frappe.whitelist()
    def validate_date(self):
        current_datetime = datetime.now().date()
        return self.date if getdate(self.date) < getdate(current_datetime) else None

    @frappe.whitelist()
    def create_event(self):
        participants_list = []

        starts_on = datetime.strptime(self.meeting_date, '%Y-%m-%d %H:%M:%S')
        ends_on = starts_on + timedelta(seconds=self.duration)
        ends_onn = ends_on.strftime('%Y-%m-%d %H:%M:%S')

        event = frappe.get_doc({
            'doctype': 'Event',
            'subject': self.meeting_subject,
            'starts_on': starts_on,
            'ends_on': ends_onn,
            'status': 'Open',
            'event_type': 'Private',
            'event_category': 'Meeting',
            'assigned_to': self.meeting_host,
            'send_reminder': 1,
            'description': self.agenda,
        })

        attendees = frappe.get_all("PMO Meeting Attendees", filters={"parent": self.name}, fields=["contact_person"])

        if attendees:
            for attendee in attendees:
                contact_person = attendee["contact_person"]
                participants_list.append({
                    'doctype': 'Event Participants',
                    'reference_doctype': 'Contact',
                    'reference_docname': contact_person
                })

        current_user_id = frappe.session.user
        user = frappe.get_doc("User", current_user_id)
        cal = frappe.db.get_value("Google Calendar", {'user': frappe.session.user}, ["name"])
        
        event = frappe.new_doc("Event")
        event.subject = self.meeting_subject 
        event.starts_on = starts_on
        event.ends_on = ends_onn
        event.status = "Open"
        event.event_type = "Private"
        event.event_category = "Meeting"
        event.send_reminder = 1
        event.description = self.agenda
        event.assigned_to = self.meeting_host
        if self.sync_with_google_calendar:
            if cal:
                event.sync_with_google_calendar = 1
                event.google_calendar = cal
        if self.all_day:
            event.all_day=1
        if self.send_an_email_reminder_in_the_morning:
            event.send_reminder=1
        if self.repeat_this_event:
            event.repeat_this_event=1
            event.repeat_on=self.meeting_scheduled_time
            start_date_str=self.meeting_date
            if self.meeting_scheduled_time=="Daily":
                if self.count_daily==0:
                    frappe.throw("Count Daily must be greater than zero. Please set another value.")

                daily_date_range=self.calculate_daily_date(start_date_str)
                event.repeat_till=daily_date_range

            if self.meeting_scheduled_time=="Weekly":
                if self.count_week==0:
                    frappe.throw("Month Count must be greater than zero. Please set another value.")

                number_of_weeks=self.count_week
                repeat_till=self.calculate_end_date(start_date_str, number_of_weeks)
                event.repeat_till=repeat_till
                if self.sunday:
                    event.sunday=1
                if self.monday:
                    event.monday=1
                if self.tuesday:
                    event.tuesday=1
                if self.wednesday:
                    event.wednesday=1
                if self.thursday:
                    event.thursday=1
                if self.friday:
                    event.friday=1
                if self.saturday:
                    event.saturday=1
            if self.meeting_scheduled_time=="Monthly":
                if self.month_count==0:
                    frappe.throw("Count Month must be greater than zero. Please set another value.")
                month_count=self.month_count
                if self.select_month:
                    month_count=month_count*self.select_month
                mont_end_date=self.calculate_month_end_date(start_date_str)
                event.repeat_till=mont_end_date
            if self.meeting_scheduled_time=="Yearly":
                if self.year_count==0:
                    frappe.throw("Count Year must be greater than zero. Please set another value.")
                year_date_count=self.calculate_year_end_date(start_date_str)
                event.repeat_till=year_date_count

        event.set("event_participants", participants_list)
        event.insert(ignore_permissions=True)
        self.invite_send = 1
        self.create_an_ics_event()
        self.save()

        return event.name if event.name else None
    
    @frappe.whitelist()
    def calculate_daily_date(self,start_date_str):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        number_of_days = self.count_daily
        end_date = start_date + timedelta(days=number_of_days)
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        return end_date_str
    
    @frappe.whitelist()
    def calculate_end_date(self,start_date_str, number_of_weeks):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        number_of_days = number_of_weeks * 7
        end_date = start_date + timedelta(days=number_of_days)
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        return end_date_str
    
    @frappe.whitelist()
    def calculate_month_end_date(self, start_date_str):
        month_count = self.month_count
        if self.select_month:
            select_mont=int(self.select_month)
            month_count=month_count*select_mont
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        
        current_date = start_date
        for _ in range(month_count):
            next_month = current_date.replace(day=28) + timedelta(days=4)
            end_of_month = next_month - timedelta(days=next_month.day)
            current_date = end_of_month + timedelta(days=1)
            
        end_date_str = end_of_month.strftime("%Y-%m-%d %H:%M:%S")
        
        return end_date_str
    
    @frappe.whitelist()
    def calculate_year_end_date(self, start_date_str):
        yaer_count = int(self.year_count)*12
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
        
        current_date = start_date
        for _ in range(yaer_count):
            next_month = current_date.replace(day=28) + timedelta(days=4)
            end_of_month = next_month - timedelta(days=next_month.day)
            current_date = end_of_month + timedelta(days=1)
        end_date_str = end_of_month.strftime("%Y-%m-%d %H:%M:%S")
        
        return end_date_str

	
    @frappe.whitelist()
    def create_an_ics_event(self):

        starts_on = datetime.strptime(self.meeting_date, '%Y-%m-%d %H:%M:%S')
        ends_on = starts_on + timedelta(seconds=self.duration)
        
        meeting_time= self.get_meeting_time_rule()

        timezone = frappe.get_value("User", filters={"name": self.meeting_host}, fieldname="time_zone") or "Asia/Kolkata"
        tz = pytz.timezone(timezone)
        tz_offset = tz.utcoffset(starts_on).total_seconds()
        tz_offset_hours = int(tz_offset // 3600)
        tz_offset_minutes = int((tz_offset % 3600) // 60)
        tz_offset_str = f"{'+' if tz_offset_hours >= 0 else '-'}{abs(tz_offset_hours):02}{abs(tz_offset_minutes):02}"

        attendees_str = ""
        attendees_str+=f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={self.host_name};X-NUM-GUESTS=0:mailto:{self.meeting_host}\n"
        for attendee in self.pmo_meeting_attendees:
            attendees_str += f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={attendee.first_name} {attendee.last_name};X-NUM-GUESTS=0:mailto:{attendee.email_address}\n"

        ics_data = f"""BEGIN:VCALENDAR
PRODID:-//{self.company}//Dexciss//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VTIMEZONE
TZID:{timezone}
X-LIC-LOCATION:{timezone}
BEGIN:STANDARD
TZOFFSETFROM:{tz_offset_str}
TZOFFSETTO:{tz_offset_str}
TZNAME:STANDARD
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
DTSTART;TZID={timezone}:{starts_on.strftime('%Y%m%dT%H%M%S')}
DTEND;TZID={timezone}:{ends_on.strftime('%Y%m%dT%H%M%S')}
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
ORGANIZER;CN={self.host_name}:mailto:{self.meeting_host}
UID:{self.name}.com
{attendees_str}
CREATED:{starts_on.strftime('%Y%m%dT%H%M%SZ')}
DESCRIPTION:{self.agenda}\\n\\n{self.online_meeting_link}
LAST-MODIFIED:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
LOCATION:
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:{self.meeting_subject}
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR"""
        
        if meeting_time:
            ics_data = ics_data.replace("END:VEVENT", f"RRULE:{meeting_time}\nEND:VEVENT")


        file_name = "invite.ics"
        file_path = frappe.get_site_path(f"public/files/{file_name}")
        with open(file_path, "w") as fp:
            fp.write(ics_data)

        my_attachment = []
        attachment = {
            "fname": file_name,
            "fcontent": open(file_path, "rb").read()
        }
        my_attachment.append(attachment)

        employee = [attendee.email_address for attendee in self.pmo_meeting_attendees]
        employee.append(self.meeting_host)
        start_time_str = starts_on.strftime('%Y-%m-%d %H:%M')
        end_time_str = ends_on.strftime('%H:%M')

        email_args = {
            "recipients": employee,
            "subject": f"Invitation: {self.meeting_subject} {start_time_str} - {end_time_str} ({self.meeting_host})",
            "message": f"{self.agenda} \n {self.online_meeting_link}",
            "attachments": my_attachment
        }
        frappe.sendmail(**email_args)
        frappe.msgprint("Email sent successfully")
        self.save()
        participant=self.meeting_host
        self.create_communication(participant)
       

    def create_communication(self, participant):
        communication = frappe.new_doc("Communication")
        self.update_communication(participant, communication)
        self.communication = communication.name

    def update_communication(self, participant, communication):
        communication.communication_medium = "Event"
        communication.subject = participant
        communication.content = self.agenda if self.agenda else self.meeting_subject
        communication.communication_date = self.creation
        communication.sender = self.owner
        communication.sender_full_name = frappe.utils.get_fullname(self.owner)
        communication.reference_doctype = self.doctype
        communication.reference_name = self.name
        communication.status = "Linked"
        communication.read_by_recipient=1
        communication.read_receipt=1
    
        email_addresses = [parti.email_address for parti in self.pmo_meeting_attendees]
        employee_participant = ','.join(email_addresses)
        communication.recipients = employee_participant
        communication.save(ignore_permissions=True)
       

    def get_meeting_time_rule(self):
        meeting_time = ""
        if self.meeting_scheduled_time == "Daily":
            meeting_time = f"FREQ=DAILY;COUNT={self.count_daily}"

        elif self.meeting_scheduled_time == "Weekly":
            days=[]
            if self.sunday:
                days.append("SU")
            if self.monday:
                days.append("MO")
            if self.tuesday:
                days.append("TU")
            if self.wednesday:
                days.append("WE")
            if self.thursday:
                days.append("TH")
            if self.friday:
                days.append("FR")
            if self.saturday:
                days.append("SA")
            day_string = ",".join(days)
            meeting_time = f"FREQ=WEEKLY;BYDAY={day_string};COUNT={self.count_week}"

        elif self.meeting_scheduled_time == "Monthly":
            meeting_time=f"FREQ=MONTHLY;"
            if self.select_month:
                meeting_time+=f"INTERVAL={self.select_month};"
            meeting_time+=f"BYMONTHDAY={self.monthly_date};COUNT={self.month_count}"
                
        elif self.meeting_scheduled_time == "Yearly":
            meeting_time = "FREQ=YEARLY;"
            if self.interval_year:
                meeting_time += f"INTERVAL={self.interval_year};"
            meeting_time += f"BYMONTH={self.month};BYMONTHDAY={self.select_date};COUNT={self.year_count};"
      
        return meeting_time
    
    
    @frappe.whitelist()
    def get_matching_link_names(self):
        names = []
        child_records = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": self.customer}, fields=["parent"])
        for record in child_records:
            names.append(record.parent)
        emp = frappe.get_all("Employee", filters={"status": "Active"}, fields=["user_id"])
        for k in emp:
            child_records = frappe.get_all("Contact", filters={"user": k.user_id}, fields=["name"])
            for record in child_records:
                names.append(record.name)
        names = list(set(names))
        return names
