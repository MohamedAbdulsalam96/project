import frappe
from frappe.utils import getdate,add_to_date,time_diff_in_hours
from frappe.utils.data import get_time


def get_break_details(self,method):
    if self.break_start_time and self.break_end_time:
        if self.break_start_time > self.break_end_time:
            from datetime import datetime, timedelta

            
            start_time_str = self.break_start_time
            end_time_str = self.break_end_time

            
            start_time = datetime.strptime(start_time_str, "%H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%H:%M:%S") + timedelta(days=1)

            
            time_difference = end_time - start_time
            self.break_duration =get_time(time_difference).hour

        else:
            diff= time_diff_in_hours(self.break_end_time ,self.break_start_time)

            self.break_duration = float(diff)
    else:
        self.break_duration = 0.0

    
    if get_time(self.start_time) >= get_time(self.end_time) and self.start_time and self.end_time:
        if self.break_duration != 0.0:
            from datetime import datetime, timedelta

            start_time_str = self.start_time
            end_time_str = self.end_time

            start_time = datetime.strptime(start_time_str, "%H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%H:%M:%S")

            if end_time < start_time:
                end_time += timedelta(days=1)

            time_difference = end_time - start_time
            self.actual_working_hours_without_break = get_time(time_difference).hour- float(self.break_duration)
        else:
            from datetime import datetime, timedelta

            # Define the start and end times
            start_time_str = self.start_time
            end_time_str = self.end_time

            start_time = datetime.strptime(start_time_str, "%H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%H:%M:%S") + timedelta(days=1)

            time_difference = end_time - start_time
            self.actual_working_hours_without_break = get_time(time_difference).hour

    elif self.start_time and self.end_time:
        if self.break_duration != 0.0:
            diff_shift= time_diff_in_hours(self.end_time ,self.start_time)
            self.actual_working_hours_without_break = float(diff_shift)-float(self.break_duration)
        else:
            diff_shift= time_diff_in_hours(self.end_time ,self.start_time)
            self.actual_working_hours_without_break = float(diff_shift)


        
