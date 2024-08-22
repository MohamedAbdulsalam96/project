#Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

import datetime
import frappe
from frappe import _
from frappe.utils import date_diff, add_to_date, getdate, add_months, add_years
from datetime import timedelta

def execute(filters=None):
    based_on = filters.get("based_on")
    if based_on == "Monthly":
        columns, data = get_monthly_report(filters)
    elif based_on == "Yearly":
        columns, data = get_yearly_report(filters)
    else:
        columns, data = [],[]
    return columns, data
def get_monthly_report(filters):
    columns = get_columns_monthly(filters)
    data = get_data_monthly(filters)
    return columns, data 

def get_yearly_report(filters):
    columns = get_columns_yearly(filters)
    data = get_data_yearly(filters)
    return columns, data

def get_columns_monthly(filters):
    columns = [
        {
            "label": "Employee_Name",
            "fieldname": "emp_name",
            "fieldtype": "Data"
        }
    ]
    all_dates = get_all_dates(filters.get("from_date"),filters.get("to_date"),"monthly")

    for date in all_dates:
        columns.append({
            "label": date.strftime("%B %Y"),
            "fieldname": date.strftime("%Y-%m-%d"),
            "fieldtype": "Data",
            "width":120
        })
    return columns
def get_columns_yearly(filters):
    columns = [{
        "label":"Employee_Name",
        "fieldname":"emp_name",
        "fieldtype":"Data"
    }]

    all_yearls = get_all_dates(filters.get("from_date"),filters.get("to_date"),"yearly")
    for year in all_yearls:
        columns.append({
            "label":str(year),
            "fieldname":str(year),
            "fieldtype":"Data",
            "width":120
        })
    return columns
def get_all_dates(from_date,to_date,frequency):
    if frequency == "monthly":
        all_dates = []

        current_date = getdate(from_date)
        end_date = getdate(to_date)
        while current_date <=end_date:
            all_dates.append(current_date)
            current_date = add_months(current_date,1)
            print("current_date",current_date)
        print("all_dates",all_dates)
        return all_dates

    elif frequency == "yearly":
        all_years = []
        current_year = getdate(from_date).year
        end_year = getdate(to_date).year
        while current_year <= end_year:
            all_years.append(current_year)
            current_year += 1
        return all_years

def get_data_monthly(filters):
    data = []
    all_dates = get_all_dates(filters.get("from_date"), filters.get("to_date"), "monthly")
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name","employee_name"])
    for employee in employees:
        employee_data = {
            "emp_name": employee.get("employee_name")
        }
        for date in all_dates:
            attendance_count = count_attendance_monthly(employee.get("name"), date)
            employee_data[date.strftime("%Y-%m-%d")] = attendance_count
        data.append(employee_data)
    return data

def get_data_yearly(filters):
    data = []
    all_yearls = get_all_dates(filters.get("from_date"),filters.get("to_date"),"yearly")
    employees = frappe.get_all("Employee",filters={"status":"Active"}, fields=["name","employee_name"])
    for employee in employees:
        employee_data = {
            "emp_name":employee.get("employee_name")
        }
        for year in all_yearls:
            attendance_count = count_attendance_yearly(employee.get("name"), year)
            employee_data[str(year)] = attendance_count

        data.append(employee_data)
    return data

def count_attendance_monthly(employee,date):
    start_date = date
    print("start_date",start_date)

    end_date = add_months(start_date, 1) - timedelta(days=1)

    print("end_date",end_date)

    attendance_count = frappe.get_all("Attendance",filters={"employee": employee, "status":"Present","attendance_date": ["between", [start_date, end_date]],"docstatus":1})
    print("attendance_count",len(attendance_count))

    return len(attendance_count)

def count_attendance_yearly(employee,year):

    start_date = datetime.date(year, 1, 1)

    end_date = datetime.date(year, 12, 31)

    attendance_count = frappe.get_all("Attendance",filters={"employee":employee, "status":"Present","attendance_date":["between",[start_date, end_date]],"docstatus":1})

    return len(attendance_count)