import frappe
from datetime import datetime, timedelta
from frappe.utils.data import getdate, rounded
import json
def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    if filters.get("min_utilization"):
        min_utilization = float(filters.get("min_utilization"))
        data = [d for d in data if d.get("total_utilization", 0) <= min_utilization]

        chart = get_chart_data(data, filters)
        
        revenue_chart=get_summary(data)

    return columns, data,None, chart,revenue_chart


def get_columns(filters):
    columns = [
        {"label": "Employee", "fieldname": "employee_data", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": "Employee Name", "fieldname": "employee_name_data", "fieldtype": "Data", "width": 200}
    ]

    if filters.get("from_date") and filters.get("to_date"):
        from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
        to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
        periodicity = filters.get("periodicity")


        if periodicity == "Daily":
            delta = to_date - from_date
            for i in range(delta.days + 1):
                date = from_date + timedelta(days=i)
                date_str = date.strftime("%d-%m-%Y")
                print("hdchjjchhjzchjcbvhjcvbhcvbcvhjbhjvc",getdate(date_str))

                columns.extend([
                    {"label": f"{date_str} Working Hours", "fieldname": f"working_hours_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Billable Allocation (hrs)", "fieldname": f"billable_allocation_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Non Billable Allocation (hrs)", "fieldname": f"non_billable_allocation_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Total Allocation (hrs)", "fieldname": f"total_allocation_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Billable Timesheet (hrs)", "fieldname": f"billable_timesheet_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Non Billable Timesheet (hrs)", "fieldname": f"non_billable_timesheet_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Total Timesheet (hrs)", "fieldname": f"total_timesheet_{getdate(date)}", "fieldtype": "Float", "width": 200},
                    {"label": f"{date_str} Billable Utilization %", "fieldname": f"billable_utilization_{getdate(date)}", "fieldtype": "Percent", "width": 200},
                    {"label": f"{date_str} Non Billable Utilization %", "fieldname": f"non_billable_utilization_{getdate(date)}", "fieldtype": "Percent", "width": 200}
                ])

        if periodicity == "Weekly":
            delta = to_date - from_date
            num_weeks = (delta.days // 7) + 1
            for i in range(num_weeks):
                week_start_date = from_date + timedelta(weeks=i)
                week_end_date = week_start_date + timedelta(days=6)
                week_str = f"{week_start_date.strftime('%d-%m-%Y')}"

                columns.extend([
                    {"label": f"{week_str} Working Hours", "fieldname": f"working_hours_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Billable Allocation (hrs)", "fieldname": f"billable_allocation_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Non Billable Allocation (hrs)", "fieldname": f"non_billable_allocation_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Total Allocation (hrs)", "fieldname": f"total_allocation_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Billable Timesheet (hrs)", "fieldname": f"billable_timesheet_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Non Billable Timesheet (hrs)", "fieldname": f"non_billable_timesheet_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Total Timesheet (hrs)", "fieldname": f"total_timesheet_{week_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{week_str} Billable Utilization %", "fieldname": f"billable_utilization_{week_str}", "fieldtype": "Percent", "width": 200},
                    {"label": f"{week_str} Non Billable Utilization %", "fieldname": f"non_billable_utilization_{week_str}", "fieldtype": "Percent", "width": 200}
                ])

        if periodicity == "Monthly":
            start_date = from_date
            while start_date <= to_date:
                month_str = start_date.strftime('%b %Y')
                columns.extend([
                    {"label": f"{month_str} Working Hours", "fieldname": f"working_hours_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Billable Allocation (hrs)", "fieldname": f"billable_allocation_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Non Billable Allocation (hrs)", "fieldname": f"non_billable_allocation_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Total Allocation (hrs)", "fieldname": f"total_allocation_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Billable Timesheet (hrs)", "fieldname": f"billable_timesheet_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Non Billable Timesheet (hrs)", "fieldname": f"non_billable_timesheet_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Total Timesheet (hrs)", "fieldname": f"total_timesheet_{month_str}", "fieldtype": "Float", "width": 200},
                    {"label": f"{month_str} Billable Utilization %", "fieldname": f"billable_utilization_{month_str}", "fieldtype": "Percent", "width": 200},
                    {"label": f"{month_str} Non Billable Utilization %", "fieldname": f"non_billable_utilization_{month_str}", "fieldtype": "Percent", "width": 200}
                ])
                start_date = start_date.replace(day=1) + timedelta(days=32)
                start_date = start_date.replace(day=1)

    columns.append({"label": "Total Utilization %", "fieldname": "total_utilization", "fieldtype": "Percent", "width": 200})

    return columns


def get_data(filters=None):
    float_precision = frappe.db.get_single_value("System Settings", "float_precision")
    rounding_method = frappe.db.get_single_value("System Settings", "rounding_method")

    if not filters:
        filters = {}

    condition = get_condition(filters)
    employee_condition = []

    if filters.get("employee"):
        employees = filters.get("employee")
        if len(employees) == 1:
            employee_condition.append(f"e.employee = '{employees[0]}'")
        else:
            employee_list = "', '".join(employees)
            employee_condition.append(f"e.employee IN ('{employee_list}')")
    if filters.get("company"):
        company = filters.get("company")
        employee_condition.append(f"e.company='{company}'")
    if filters.get("report_to"):
        report_to = filters.get("report_to")
        employee_condition.append(f"e.reports_to='{report_to}'")
    if filters.get("considered_completed_task"):
        completed_task = "Completed"
    else:
        completed_task = ""

    employee_condition_str = " AND ".join(employee_condition) if employee_condition else "1=1"

    data = []

    employees = frappe.db.sql(f"""
        SELECT e.name, e.employee_name, e.holiday_list
        FROM `tabEmployee` e
        WHERE e.status = 'Active' AND ({employee_condition_str})
    """, as_dict=True)

    for emp in employees:
        employee = emp.get("name")
        employee_name = emp.get("employee_name")
        holiday_list = emp.get("holiday_list")
        from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
        to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
        delta = to_date - from_date

        aggregated_data = {
            "employee_data": employee,
            "employee_name_data": employee_name
        }

        periodicity = filters.get("periodicity")
        holiday_dates = [holiday.holiday_date for holiday in frappe.get_doc("Holiday List", holiday_list).holidays]
        hr_setting_working = frappe.db.get_value("HR Settings", None, "standard_working_hours")
       
       
        if periodicity == "Daily":
            total_allocation=0
            total_working_hours=0
            for i in range(delta.days + 1):
                date_str = from_date + timedelta(days=i)
                if getdate(date_str) not in holiday_dates:
                    emp_data = get_employee_data(employee, date_str, completed_task, condition, float_precision, rounding_method,hr_setting_working)
                    daily_data = aggregate_daily_data(emp_data, date_str, float_precision, rounding_method)
                    for key, uti in daily_data.items():
                        if key.startswith("working_hours"):
                            total_working_hours += uti
                        elif key.startswith("total_allocation"):
                            total_allocation += uti
                    if total_working_hours !=0:
                        total_utilization = (total_allocation / total_working_hours) * 100
                        daily_data["total_utilization"] = total_utilization

                    aggregated_data.update(daily_data)

        elif periodicity == "Weekly":
            total_allocation=0
            total_working_hours=0
            for i in range(0, delta.days + 1, 7):
                week_start_date = from_date + timedelta(days=i)
                week_end_date = min(week_start_date + timedelta(days=6), to_date)
                week_str = f"{week_start_date.strftime('%d-%m-%Y')}"

                weekly_data = {
                    f"working_hours_{week_str}": 0,
                    f"billable_allocation_{week_str}": 0,
                    f"non_billable_allocation_{week_str}": 0,
                    f"total_allocation_{week_str}": 0,
                    f"billable_timesheet_{week_str}": 0,
                    f"non_billable_timesheet_{week_str}": 0,
                    f"total_timesheet_{week_str}": 0,
                    f"billable_utilization_{week_str}": 0,
                    f"non_billable_utilization_{week_str}": 0
                }

                for j in range(7):
                    date_str = week_start_date + timedelta(days=j)
                    if date_str > to_date:
                        break
                    if getdate(date_str) not in holiday_dates:
                        emp_data = get_employee_data(employee, date_str, completed_task, condition, float_precision, rounding_method,hr_setting_working)
                        weekly_data = aggregate_weekly_data(emp_data, weekly_data, week_str, float_precision, rounding_method)

                if weekly_data[f"working_hours_{week_str}"] != 0:
                    weekly_data[f"billable_utilization_{week_str}"] = (weekly_data[f"billable_allocation_{week_str}"] / weekly_data[f"working_hours_{week_str}"]) * 100
                    weekly_data[f"non_billable_utilization_{week_str}"] = (weekly_data[f"non_billable_allocation_{week_str}"] / weekly_data[f"working_hours_{week_str}"]) * 100
                for key, uti in weekly_data.items():
                    if key.startswith("working_hours"):
                        total_working_hours += uti
                    elif key.startswith("total_allocation"):
                        total_allocation += uti

                if total_working_hours !=0:
                    total_utilization = (total_allocation / total_working_hours) * 100
                    weekly_data["total_utilization"] = total_utilization



                aggregated_data.update(weekly_data)

        elif periodicity == "Monthly":
            total_allocation=0
            total_working_hours=0
            current_date = from_date
           
            while current_date <= to_date:
                month_start_date = current_date.replace(day=1)
                next_month = month_start_date + timedelta(days=32)
                month_end_date = next_month.replace(day=1) - timedelta(days=1)
                month_str = f"{month_start_date.strftime('%B %Y')}"
                # print("month str in data hdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",month_str)

                if month_end_date > to_date:
                    month_end_date = to_date

                monthly_data = {
                    f"working_hours_{month_str}": 0,
                    f"billable_allocation_{month_str}": 0,
                    f"non_billable_allocation_{month_str}": 0,
                    f"total_allocation_{month_str}": 0,
                    f"billable_timesheet_{month_str}": 0,
                    f"non_billable_timesheet_{month_str}": 0,
                    f"total_timesheet_{month_str}": 0,
                    f"billable_utilization_{month_str}": 0,
                    f"non_billable_utilization_{month_str}": 0
                }

                current_day = month_start_date
                while current_day <= month_end_date:
                    if getdate(current_day) not in holiday_dates:
                        emp_data = get_employee_data(employee, current_day, completed_task, condition, float_precision, rounding_method,hr_setting_working)
                        monthly_data = aggregate_monthly_data(emp_data, monthly_data, month_str, float_precision, rounding_method)
                    current_day += timedelta(days=1)
                print("monthly data gdggggggggggggggggggggggggggggggggggggggggggggggggggdggdgdgdg",monthly_data)
                if monthly_data[f"working_hours_{month_str}"] != 0:
                    monthly_data[f"billable_utilization_{month_str}"] = (monthly_data[f"billable_allocation_{month_str}"] / monthly_data[f"working_hours_{month_str}"]) * 100
                    monthly_data[f"non_billable_utilization_{month_str}"] = (monthly_data[f"non_billable_allocation_{month_str}"] / monthly_data[f"working_hours_{month_str}"]) * 100
                for key, uti in monthly_data.items():
                    if key.startswith("working_hours_"):
                        total_working_hours += uti
                    elif key.startswith("total_allocation_"):
                        total_allocation += uti
                if total_working_hours !=0:
                    total_utilization = (total_allocation / total_working_hours) * 100
                    monthly_data["total_utilization"] = total_utilization


                aggregated_data.update(monthly_data)

                current_date = next_month
                # print("agreee gated data mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm00000000000000000000",aggregated_data)

        data.append(aggregated_data)
    
    return data


def get_employee_data(employee, date_str, completed_task, condition, float_precision, rounding_method,hr_setting_working):
    emp_data = frappe.db.sql(f"""
        SELECT 
            a.employee,
            a.attendance_date,
            a.working_hours,
            JSON_ARRAYAGG(
                DISTINCT JSON_OBJECT(
                    'task', t.name,
                    'is_billable', t.is_billable,
                    'duration_per_day_in_hours', t.duration_per_day_in_hours
                )
            ) AS tasks,
            JSON_ARRAYAGG(
                DISTINCT JSON_OBJECT(
                    'timesheet', ts.name,
                    'work_hours', ts.total_hours,
                    'is_billable', td.is_billable
                )
            ) AS timesheets
        FROM `tabAttendance` a
        LEFT JOIN `tabTask` t 
            ON a.employee = t.primary_consultant AND t.status IN ("Open", "Working", "Pending Review", "Overdue", %s)
            AND a.attendance_date BETWEEN t.exp_start_date AND t.exp_end_date
        LEFT JOIN `tabTimesheet Detail` td 
            ON a.attendance_date = td.from_date
        LEFT JOIN `tabTimesheet` ts 
            ON td.parent = ts.name AND a.employee = ts.employee
        WHERE a.employee = %s
            AND ({condition})
            AND (a.status = 'Present' OR a.status = 'Half Day')
        GROUP BY a.employee, a.attendance_date, a.working_hours
        HAVING a.attendance_date = %s
    """, (completed_task, employee, date_str), as_dict=True)
    if not emp_data:
        emp_data = frappe.db.sql(f"""
            SELECT 
                '{employee}' AS employee,
                '{getdate(date_str)}' AS attendance_date,
                {hr_setting_working} AS working_hours,
                JSON_ARRAYAGG(
                    DISTINCT JSON_OBJECT(
                        'task', t.name,
                        'is_billable', t.is_billable,
                        'duration_per_day_in_hours', t.duration_per_day_in_hours
                    )
                ) AS tasks,
                JSON_ARRAYAGG(
                    DISTINCT JSON_OBJECT(
                        'timesheet', ts.name,
                        'work_hours', ts.total_hours,
                        'is_billable', td.is_billable
                    )
                ) AS timesheets
            FROM `tabEmployee` e
            LEFT JOIN `tabTask` t 
                ON e.name = t.primary_consultant AND t.status IN ("Open", "Working", "Pending Review", "Overdue", %s)
                AND '{getdate(date_str)}' BETWEEN t.exp_start_date AND t.exp_end_date
            LEFT JOIN `tabTimesheet Detail` td 
                ON '{getdate(date_str)}' = td.from_date
            LEFT JOIN `tabTimesheet` ts 
                ON td.parent = ts.name AND e.name = ts.employee
            WHERE e.name = %s
            GROUP BY e.name
        """, (completed_task, employee), as_dict=True)

    return emp_data

def aggregate_daily_data(emp_data, date_str, float_precision, rounding_method):
    daily_data = {
        f"working_hours_{date_str.strftime('%Y-%m-%d')}": 0,
        f"billable_allocation_{date_str.strftime('%Y-%m-%d')}": 0,
        f"non_billable_allocation_{date_str.strftime('%Y-%m-%d')}": 0,
        f"total_allocation_{date_str.strftime('%Y-%m-%d')}": 0,
        f"billable_timesheet_{date_str.strftime('%Y-%m-%d')}": 0,
        f"non_billable_timesheet_{date_str.strftime('%Y-%m-%d')}": 0,
        f"total_timesheet_{date_str.strftime('%Y-%m-%d')}": 0,
        f"billable_utilization_{date_str.strftime('%Y-%m-%d')}": 0,
        f"non_billable_utilization_{date_str.strftime('%Y-%m-%d')}": 0
    }
    for emm in emp_data:
        tasks = frappe.parse_json(emm.get("tasks"))
        timesheets = frappe.parse_json(emm.get("timesheets"))

        billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if t.get("is_billable")
        )

        non_billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if not t.get("is_billable")
        )

        billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if ts.get("is_billable")
        )

        non_billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if not ts.get("is_billable")
        )

        daily_data[f"working_hours_{date_str.strftime('%Y-%m-%d')}"] += rounded(emm.get("working_hours", 0), float_precision, rounding_method)
        daily_data[f"billable_allocation_{date_str.strftime('%Y-%m-%d')}"] += billable_allocation
        daily_data[f"non_billable_allocation_{date_str.strftime('%Y-%m-%d')}"] += non_billable_allocation
        daily_data[f"total_allocation_{date_str.strftime('%Y-%m-%d')}"] += (billable_allocation + non_billable_allocation)
        daily_data[f"billable_timesheet_{date_str.strftime('%Y-%m-%d')}"] += billable_timesheet
        daily_data[f"non_billable_timesheet_{date_str.strftime('%Y-%m-%d')}"] += non_billable_timesheet
        daily_data[f"total_timesheet_{date_str.strftime('%Y-%m-%d')}"] += (billable_timesheet + non_billable_timesheet)

        if daily_data[f"working_hours_{date_str.strftime('%Y-%m-%d')}"] != 0:
            daily_data[f"billable_utilization_{date_str.strftime('%Y-%m-%d')}"] = (daily_data[f"billable_allocation_{date_str.strftime('%Y-%m-%d')}"] / daily_data[f"working_hours_{date_str.strftime('%Y-%m-%d')}"]) * 100
            daily_data[f"non_billable_utilization_{date_str.strftime('%Y-%m-%d')}"] = (daily_data[f"non_billable_allocation_{date_str.strftime('%Y-%m-%d')}"] / daily_data[f"working_hours_{date_str.strftime('%Y-%m-%d')}"]) * 100

    return daily_data

def aggregate_weekly_data(emp_data, weekly_data, week_str, float_precision, rounding_method):
    for emm in emp_data:
        tasks = frappe.parse_json(emm.get("tasks"))
        timesheets = frappe.parse_json(emm.get("timesheets"))

        billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if t.get("is_billable")
        )

        non_billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if not t.get("is_billable")
        )

        billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if ts.get("is_billable")
        )

        non_billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if not ts.get("is_billable")
        )

        weekly_data[f"working_hours_{week_str}"] += rounded(emm.get("working_hours", 0), float_precision, rounding_method)
        weekly_data[f"billable_allocation_{week_str}"] += billable_allocation
        weekly_data[f"non_billable_allocation_{week_str}"] += non_billable_allocation
        weekly_data[f"total_allocation_{week_str}"] += (billable_allocation + non_billable_allocation)
        weekly_data[f"billable_timesheet_{week_str}"] += billable_timesheet
        weekly_data[f"non_billable_timesheet_{week_str}"] += non_billable_timesheet
        weekly_data[f"total_timesheet_{week_str}"] += (billable_timesheet + non_billable_timesheet)
        
    return weekly_data

def aggregate_monthly_data(emp_data, monthly_data, month_str, float_precision, rounding_method):
    
    for emm in emp_data:
        tasks = frappe.parse_json(emm.get("tasks"))
        timesheets = frappe.parse_json(emm.get("timesheets"))

        billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if t.get("is_billable")
        )

        non_billable_allocation = sum(
            rounded(t.get("duration_per_day_in_hours", 0) or 0, float_precision, rounding_method)
            for t in tasks if not t.get("is_billable")
        )

        billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if ts.get("is_billable")
        )

        non_billable_timesheet = sum(
            rounded(ts.get("work_hours", 0) or 0, float_precision, rounding_method)
            for ts in timesheets if not ts.get("is_billable")
        )

        monthly_data[f"working_hours_{month_str}"] += rounded(emm.get("working_hours", 0), float_precision, rounding_method)
        print(f"working_hours_{month_str}")
        monthly_data[f"billable_allocation_{month_str}"] += billable_allocation
        monthly_data[f"non_billable_allocation_{month_str}"] += non_billable_allocation
        monthly_data[f"total_allocation_{month_str}"] += (billable_allocation + non_billable_allocation)
        monthly_data[f"billable_timesheet_{month_str}"] += billable_timesheet
        monthly_data[f"non_billable_timesheet_{month_str}"] += non_billable_timesheet
        monthly_data[f"total_timesheet_{month_str}"] += (billable_timesheet + non_billable_timesheet)
        
    return monthly_data


def get_condition(filters):
    conditions = ["1=1"]
    if filters.get("from_date") and filters.get("to_date"):
        from_date = filters["from_date"]
        to_date = filters["to_date"]
        conditions.append(f"a.attendance_date BETWEEN '{from_date}' AND '{to_date}'")

    return " AND ".join(conditions)


def get_chart_data(data, filters):

    periodicity = filters.get("periodicity")
    metrics = [
        "working_hours", "billable_allocation", "non_billable_allocation",
        "total_allocation", "billable_timesheet", "non_billable_timesheet",
        "total_timesheet"
    ]
    chart_data = {
        'data': {
            'labels': [d["employee_name_data"] for d in data],
            'datasets': []
        },
        'type': 'bar'
    }
    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
    period_labels = []

    if periodicity == "Daily":
        delta = to_date - from_date
        period_labels = [
            (from_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
        ]
    elif periodicity == "Weekly":
        delta = to_date - from_date
        num_weeks = (delta.days // 7) + 1
        for i in range(num_weeks):
            week_start_date = from_date + timedelta(weeks=i)
            week_end_date = week_start_date + timedelta(days=6)
            period_labels.append(f"{week_start_date.strftime('%d-%m-%Y')}")
    elif periodicity == "Monthly":
        start_date = from_date
        while start_date <= to_date:
            month_str = start_date.strftime('%b %Y')
            period_labels.append(month_str)
            start_date = start_date.replace(day=1) + timedelta(days=32)
            start_date = start_date.replace(day=1)
    
    for metric in metrics:
        dataset = {
            'name': metric.replace("_", " ").title(),
            'values': []
        }
        
        for emp in data:
            emp_total = 0
            for period in period_labels:
                emp_total += emp.get(f"{metric}_{period}", 0)
                emp_total = float("{:.2f}".format(emp_total))
            dataset['values'].append(emp_total)
        chart_data['data']['datasets'].append(dataset)
    
    return chart_data


def get_summary(data):
    total_working_hours=0
    total_billable_allocation=0
    total_non_billable_allocation=0
    total_billable_timesheet=0
    total_non_billable_timesheet=0
    total_allocation_hours = 0
    total_timesheet_hours = 0

    for row in data:
        for key in row:
            if key.startswith('working_hours'):
                total_working_hours += row[key]
            if key.startswith('total_allocation'):
                total_allocation_hours += row[key]
            if key.startswith('total_timesheet'):
                total_timesheet_hours += row[key]
            if key.startswith('billable_allocation'):
                total_billable_allocation+=row[key]
            if key.startswith('non_billable_allocation'):
                total_non_billable_allocation+=row[key]
            if key.startswith('billable_timesheet'):
                total_billable_timesheet+=row[key]
            if key.startswith('non_billable_timesheet_'):
                total_non_billable_timesheet+=row[key]
    
    if total_working_hours !=0:
        total_utillization= (total_allocation_hours/total_working_hours)*100
        total_billable_uti=(total_billable_allocation/total_working_hours)*100
        total_non_billable_uti=(total_non_billable_allocation/total_working_hours)*100
    else:
        total_utillization=0
        total_billable_uti=0
        total_non_billable_uti=0

        

    summary = [
            {
				"value": total_working_hours,
                "indicator": "Green",
				"label": ("Total Working Hours"),
				"datatype": 'Float'
			},
            {
				"value": total_billable_allocation,
                "indicator": "Green",
				"label": ("Total  Billable Allocation Hours"),
				"datatype": 'Float'
			},
            {
				"value": total_non_billable_allocation,
                "indicator": "Green",
				"label": ("Total  Non Billable Allocation Hours"),
				"datatype": 'Float'
			},
            {
				"value": total_allocation_hours,
                "indicator": "Green",
				"label": ("Total Allocation Hours"),
				"datatype": 'Float'
			},
            {
				"value": total_billable_timesheet,
                "indicator": "Green",
				"label": ("Total Billable Timesheet Hours"),
				"datatype": 'Float',
			},
            {
				"value": total_non_billable_timesheet,
                "indicator": "Green",
				"label": ("Total Non Billable Timesheet Hours"),
				"datatype": 'Float',
			},
			{
				"value": total_timesheet_hours,
                "indicator": "Green",
				"label": ("Total Timesheet Hours"),
				"datatype": 'Float',
			},
            {
				"value": total_billable_uti,
				"indicator": "Green",
				"label": ("Total Billable Utilization %"),
				"datatype": "Percent"
			},
            {
				"value": total_non_billable_uti,
				"indicator": "Green",
				"label": ("Total Non Billable Utilization %"),
				"datatype": "Percent"
			},
			{
				"value": total_utillization,
				"indicator": "Green",
				"label": ("Total Utilization %"),
				"datatype": "Percent"
			}
    ]

    return summary