# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, date               
from frappe import get_all,db
from frappe.model.document import Document
from ...report.performance_target_variable_report.performance_target_variable_report import get_monthly_data, get_Data_Quarterly,get_data_halfyearly, get_data_yearly

class PIPThreshold(Document):
    pass

def create_performance_notice(performace_score,threshold_score,var):
    if performace_score <= threshold_score:
        doc = frappe.new_doc('Performance Improvement Notice')
        doc.employee = var['employee']
        doc.employee_name = var['employee_name']
        doc.department = var['department']
        doc.designation = var['designation']
        doc.pip_cutoff = threshold_score
        doc.score = performace_score
        doc.status ="Open"
        doc.date = date.today()
        doc.insert()
        doc.submit()

@frappe.whitelist()    
def threshold_crone_job():

    year = datetime.now().year 
    day = datetime.now().day
    current_month = datetime.now().month
    
    pip = frappe.get_doc('PIP Threshold')

    trigger_date = pip.pip_trigger_date
    if day == trigger_date:
        threshold_score = pip.minimum_required_performance_score
        threshold_periodicity = pip.performance_evaluation_periodicity

        target_variables = db.sql("select DISTINCT employee,employee_name,fiscal_year from `tabPerformance Target Variable`")

        if threshold_periodicity == "Monthly":
            
            monthly_data_list =[]
            for items in target_variables:       
                data_list = get_monthly_data(filters={"fy":items[2]}, employee_name=items[1]) 

                for data in data_list:
                    if data['employee'] != '':
                        monthly_data_list.append(data)
            
            unique_set = {tuple(d.items()) for d in monthly_data_list}
            unique_list = [dict(item) for item in unique_set]
                    
            for var in unique_list:
                    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    
                    if current_month == 1 and day == trigger_date:
                        month = "December"
                        year1 = year - 1
                        performace_score = var[f'{month} {year1}score']
                        create_performance_notice(performace_score,threshold_score,var)

                    elif 2 <= current_month <= 12 and day ==trigger_date :

                        month = months[current_month - 2]
                        year1 = year
                        performace_score = var[f'{month} {year1}score']
                        create_performance_notice(performace_score,threshold_score,var)
                    
        if threshold_periodicity == "Quarterly":
            
            quarterly_data_list =[]
            for items in target_variables:           
                data_list = get_Data_Quarterly(filters={"fy":items[2]},employee_name = items[1])

                for data in data_list:
                    if data['employee'] != '':
                        quarterly_data_list.append(data)

            unique_set = {tuple(d.items()) for d in quarterly_data_list}
            unique_list = [dict(item) for item in unique_set]

            for var in unique_list:   
                if current_month ==1 and day == trigger_date:
                    month = 'Oct-Dec'
                    year1 = year - 1
                    performace_score = var[f'{month} {year1}score']
                    create_performance_notice(performace_score,threshold_score,var)
                elif current_month == 4 and day == trigger_date:
                    month = 'Jan-Mar'
                    performace_score = var[f'{month} {year}score']
                    create_performance_notice(performace_score,threshold_score,var)
                elif current_month == 7 and day == trigger_date:
                    month = 'Apr-Jun'
                    performace_score = var[f'{month} {year}score']
                    create_performance_notice(performace_score,threshold_score,var)
                elif current_month == 10 and day == trigger_date:
                    month = 'Jul-Sep'       
                    performace_score = var[f'{month} {year}score']
                    create_performance_notice(performace_score,threshold_score,var)
                    
        if threshold_periodicity == "Bi Yearly":             

            halfyearly_data_list =[]
            for items in target_variables:           
                data_list = get_data_halfyearly(filters={"fy":items[2]},employee_name = items[0])

                for data in data_list:
                    if data['employee'] != '':
                        halfyearly_data_list.append(data)

            unique_set = {tuple(d.items()) for d in halfyearly_data_list}
            unique_list = [dict(item) for item in unique_set]

            for var in unique_list:
                if current_month == 1 and day == trigger_date:
                    month = 'Jul-Dec'
                    year1 = year - 1
                    performace_score = var[f'{month} {year1}score']
                    create_performance_notice(performace_score,threshold_score,var)
                    
                elif current_month == 7 and day == trigger_date:
                    month = 'Jan-Jun'
                    performace_score = var[f'{month} {year}score']
                    create_performance_notice(performace_score,threshold_score,var)
                
        if threshold_periodicity == "Yearly":

            yearly_data_list =[]
            for items in target_variables:           
                data_list =  get_data_yearly(filters={"fy":items[2]},employee_name = items[0])

                for data in data_list:
                    if data['employee'] != '':
                        yearly_data_list.append(data)
            
            unique_set = {tuple(d.items()) for d in   yearly_data_list}
            unique_list = [dict(item) for item in unique_set]
                
            for var in unique_list:
                if current_month ==1 and day == trigger_date:
                    year3 = year-1

                    performace_score = var[f'01-01-{year3}-31-12-{year3}score']
                    create_performance_notice(performace_score,threshold_score,var)
                



def pip_enqueue_cron_job():
    frappe.enqueue(
    threshold_crone_job, # python function or a module path as string
    queue="default", # one of short, default, long
    timeout=86400, # pass timeout manually
    is_async=True, # if this is True, method is run in worker
    now=False, # if this is True, method is run directly (not in a worker) 
    job_name="PIP Background Job", # specify a job name
)
    

                        




            



    


               
                
              
                

                

   
   

   