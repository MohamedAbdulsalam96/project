# Copyright (c) 2023, Dexciss and contributors
# For license information, please see license.txt
import calendar
import frappe
from frappe.model.document import Document
from nextproject.nextproject.report.performance_target_variable_report import performance_target_variable_report as pr
from datetime import datetime
from frappe.utils import getdate , flt,today
from datetime import datetime, timedelta

class PerformanceBonus(Document):

	# def validate(self):
	# 	print("ddddd",today().split('-'))
	# 	print("ccccccc",self.last_date_of_month())


	@frappe.whitelist()
	def get_bonus_emp(self):
		emp=[]
		doc =frappe.db.sql("""select p.employee as emp from `tabPerformance Target Variable` as p  
		left outer join `tabEmployee` as e on e.name=p.employee where e.status='Active' and p.bonus_paid=1;""",as_dict=1)
		
		for i in doc:
			emp.append(i.get('emp'))

		return emp


	def on_submit(self):
		
		employee=''
		payable_amount=''
		for x in self.performance_bonus_items:
			employee=x.employee
			payable_amount=x.payable_amount
			doc=frappe.new_doc('Additional Salary')
			last_date=self.last_date_of_month()
			dates=datetime.strptime(last_date,'%m-%d-%Y')
			doc.employee=employee
			print(employee,last_date,payable_amount)
			doc.amount=payable_amount
			doc.company=self.company
			com=frappe.get_doc("Company",self.company)
			doc.currency=com.default_currency
			doc.salary_component=self.salary_component
			doc.payroll_date=getdate(dates)
			doc.custom_performance_bonus=self.name
			doc.save(ignore_permissions=True)
			
		

 

	def last_date_of_month(self):
		month_number=[]
		last_day=''
		fis_year=0
		f_year=frappe.db.sql("""SELECT year_start_date,year_end_date,YEAR(year_start_date) AS year FROM `tabFiscal Year` WHERE name='{}';""".format(self.fiscal_year),as_dict=1)
		if self.bonus_periodicity=='Monthly':
				fiscal_year=today().split('-')[0]
				fis_year=today().split('-')[0]
				month_number = list(calendar.month_name).index(self.bonus_period_monthly.capitalize())
				last_day = calendar.monthrange(int(fiscal_year), month_number)[1]
				# else:
				# 	fis_year= end_year.year
				# 	month_number = list(calendar.month_name).index(self.bonus_period_monthly.capitalize())
				# 	last_day = calendar.monthrange( end_year.year, month_number)[1]
		
		if self.bonus_periodicity=='Quarterly':
               
			month_name=get_month_name(self)
              
			fiscal_year=today().split('-')[0]
			fis_year=today().split('-')[0]
			# start_year=f_year[0].get('year_start_date')
			# end_year=f_year[0].get('year_end_date')			
			month_number = list(calendar.month_name).index(month_name.capitalize())
			last_day = calendar.monthrange(int(fiscal_year), month_number)[1]
	
		if self.bonus_periodicity=='Half Yearly':
				month_name=get_month_name(self)
                
				fiscal_year=today().split('-')[0]
				fis_year=today().split('-')[0]
				month_number = list(calendar.month_name).index(month_name.capitalize())
				last_day = calendar.monthrange(int(fiscal_year), month_number)[1]

		if self.bonus_periodicity=='Yearly':
				month_name=get_month_name(self)

				fiscal_year=today().split('-')[0]
				fis_year=today().split('-')[0]
				month_number = list(calendar.month_name).index(month_name.capitalize())
				last_day = calendar.monthrange(int(fiscal_year), month_number)[1]


		return f"{month_number:02d}-{last_day:02d}-{str(fis_year)}"
			
				


	


	

	def get_condtion(self):

		condtion=''
		if self.bonus_periodicity=='Monthly':
			condtion=self.bonus_periodicity

		if self.bonus_periodicity=='Quarterly':
			contition=self.bonus_periodicity

		if self.bonus_periodicity=='Half Yearly':
			contition=self.bonus_periodicity

		if self.bonus_periodicity=='Yearly':
			contition=self.bonus_periodicity

		return condtion
	 
	 

	def get_fiscal_year(cls,self):
		return self.fiscal_year

	
	def get_company(self):
         return self.company

  

@frappe.whitelist()
def get_performance_bonus_item(filters,fiscal_year,employee_name,company,periodicity,periods): 
	report_data=[]
	res_ob=[]
	dic={}
	months={}
	quaters={}
	start_year=0
	dic.update({'target':100})
	score=0.0
	if company and fiscal_year and periodicity:
        
		months=getMonths(fiscal_year)

		quaters=getQuarters(fiscal_year)

		half_year=getHalfYearly(fiscal_year)

		get_years=pr.getYears(filters=None,fiscal_year=fiscal_year)


		report_data=pr.get_bonus_data(filters,fiscal_year,employee_name,company,periodicity)

	variable_data=frappe.get_all('Performance Target Variable',filters={'employee':employee_name},fields=['*'])

	f_year=frappe.db.sql("""SELECT year_start_date,year_end_date,YEAR(year_start_date) AS year FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year),as_dict=1)
	
    
	
	
	if f_year:
		start_year = f_year[0].get('year_start_date')
		end_year = f_year[0].get('year_end_date')
		
		while start_year.year <= end_year.year:
			year=start_year.year
			if start_year.year == end_year.year:
				year = end_year.year

			
			for items in report_data:
				    
				if periodicity == 'Monthly':
					for key, value in months.items():
						if items['employee'] == employee_name and items['energy_point_rule'] == '' and periods + ' ' + str(year) == key:
							dic.update({'achieved': items.get(key + 'achieved')})
							score = items.get(key + 'score')
							if score > 0:
								break

				if periodicity == 'Quarterly':
					for key, value in quaters.items():
						if items['employee'] == employee_name and items['energy_point_rule'] == '' and periods + ' ' + str(year) == key:
							dic.update({'achieved': items.get(key + 'achieved')})
							score = items.get(key + 'score')
							if score > 0:
								break

				if periodicity == 'Half Yearly':
					for key, value in half_year.items():
						if items['employee'] == employee_name and items['energy_point_rule'] == '' and periods + ' ' + str(year) == key:
							dic.update({'achieved': items.get(key + 'achieved')})
							score = items.get(key + 'score')
							if score > 0:
								break

				if items['employee'] == employee_name and items['energy_point_rule'] == '' and periodicity == 'Yearly':
					if periodicity == 'Yearly':
						break
					for years in get_years:
						year = years.get('from_date')
						if today().split('-')[0] == year.split('-')[2]:
							key = years.get('from_date') + '-' + years.get('to_date')
							dic.update({'achieved': items.get(key + 'achieved')})
							score = items.get(key + 'score')

			
			start_year = start_year.replace(year=start_year.year + 1)

			
		# for items in report_data:
		# 	if periodicity=='Monthly':
				
		# 		for key,value in months.items():
		# 			if items['employee'] ==employee_name and items['energy_point_rule']=='' and periods+' '+str(today().split('-')[0])==key:
		# 				dic.update({'achieved':items.get(key+'achieved')})
		# 				score=items.get(key+'score')
		# 				# print(items[periods+' '+final_year+'score'])
		# 				# dic.update({'score':items.get(periods+' '+final_year+'score')})
		# 	if periodicity=='Quarterly':
		# 		for key,value in quaters.items():
		# 			if items['employee'] ==employee_name and items['energy_point_rule']=='' and periods+' '+str(today().split('-')[0])==key:
		# 					dic.update({'achieved':items.get(key+'achieved')})
		# 					score=items.get(key+'score')
				

		# 	if periodicity=='Half Yearly':
		# 		for key,value in half_year.items():
		# 			if items['employee'] ==employee_name and items['energy_point_rule']=='' and periods+' '+str(today().split('-')[0])==key:
		# 					dic.update({'achieved':items.get(key+'achieved')})
		# 					score=items.get(key+'score')
							
			
		# 	if items['employee'] ==employee_name and items['energy_point_rule']=='' and periodicity=='Yearly':

		# 		for years in get_years:
		# 			year=years.get('from_date')
		# 			if today().split('-')[0]==year.split('-')[2]:
		# 				key=years.get('from_date')+'-'+years.get('to_date')
		# 				dic.update({'achieved':items.get(key+'achieved')})
		# 				score=items.get(key+'score')
						

					
						
				
			


				
			
				# dic.update({"achieved":items[years+'achieved']})
				# score=items[years+'score']
				
				# print(items[years+'achieved'])
				
				# print(items[years+'score'])
				# dic.update({'score':items[years+'score']})
		
				
		
		
		for j in variable_data:
			if j.get('bonus_paid')==1 and periodicity=='Monthly':
					final_amount=round(j.get('annual_bonus')/12,2)
					dic.update({'maximum_amount':final_amount})
					if score:
						if j.get('maximum_score_allowed')>0 and flt(score) > j.get('maximum_score_allowed'):
							dic.update({'score':j.get('maximum_score_allowed')})
							final_payble=round(j.get('maximum_score_allowed')/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
						else:
							
							dic.update({'score':score})
							final_payble=round(score/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
					res_ob.append(dic)
			
			
			elif j.get('bonus_paid')==1 and periodicity=='Quarterly':
					final_amount=round(j.get('annual_bonus')/4,2)
					dic.update({'maximum_amount':final_amount})
					if score:
						if flt(j.get('maximum_score_allowed'))>0 and score > j.get('maximum_score_allowed'):
							dic.update({'score':j.get('maximum_score_allowed')})
							final_payble=round(j.get('maximum_score_allowed')/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
						else:
							
							dic.update({'score':flt(score)})
							final_payble=round(score/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
					res_ob.append(dic)
			
			elif j.get('bonus_paid')==1 and periodicity=='Half Yearly':
					final_amount=round(j.get('annual_bonus')/6,2)
					dic.update({'maximum_amount':final_amount})
					if score:
						if flt(j.get('maximum_score_allowed'))>0 and score > j.get('maximum_score_allowed'):
							dic.update({'score':j.get('maximum_score_allowed')})
							final_payble=round(j.get('maximum_score_allowed')/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
						else:
							
							dic.update({'score':score})
							final_payble=round(score/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
					res_ob.append(dic)
			elif j.get('bonus_paid')==1 and periodicity=='Yearly':
					final_amount=round(j.get('annual_bonus'),2)
					dic.update({'maximum_amount':final_amount})
					if score:
						if j.get('maximum_score_allowed')>0 and score > j.get('maximum_score_allowed'):
							dic.update({'score':j.get('maximum_score_allowed')})
							final_payble=round(j.get('maximum_score_allowed')/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
						else:
							
							dic.update({'score':score})
							final_payble=round(score/100*final_amount,2)
							dic.update({'payable_amount':final_payble})
					res_ob.append(dic)
			else:
				frappe.msgprint("Please Enable Is bonus to be paid")
		return res_ob


def get_month_name(self):
	month_name=''
	if self.bonus_periodicity=='Quarterly':		
		if self.bonus_period_quarterly=='Jan-Mar':
			month_name='March'
		if self.bonus_period_quarterly=='Apr-Jun':
			month_name='June'
		
		if self.bonus_period_quarterly=='Jul-Sept':
			month_name='September'

		if self.bonus_period_quarterly=='Oct-Dec':
			month_name='December'

	if self.bonus_periodicity=='Half Yearly':
		if self.bonus_period_half_yearly=='Jan-Jun':
			month_name='June'
		if self.bonus_period_half_yearly=='Jul-Dec':
			month_name='December'

	if self.bonus_periodicity=='Yearly':
			month_name='December'
		
	return month_name


def getMonths(fiscal_year):
	start_date = ''
	end_date = ''
	year = []
	start_year=None
	end_date=None
	months={}

	year = frappe.db.sql("""SELECT year_start_date, year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year), as_dict=True)
	if year:
		start_year = year[0].get('year_start_date')
		end_year = year[0].get('year_end_date')

    
	if start_year and end_year:
		start_date = datetime.strptime(str(start_year), "%Y-%m-%d")
		end_date = datetime.strptime(str(end_year), "%Y-%m-%d")
		
	while start_date <= end_date:
		month = start_date.strftime("%B %Y")
		
		months.update({start_date.strftime("%B %Y"):start_date.year})
		if start_date.month == 12:
			start_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
		else:
			start_date = start_date.replace(month=start_date.month + 1, day=1)
	return months

   

def getQuarters(fiscal_year):
	start_date=''
	end_date=''
	year=[]


	year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year),as_dict=True)

	start_year=year[0].get('year_start_date')
	end_year=year[0].get('year_end_date')
	if start_year and end_year:
		start = datetime.strptime(str(start_year), "%Y-%m-%d")
		end = datetime.strptime(str(end_year), "%Y-%m-%d")
	start_date = start.replace(month=1)
	end_date = end.replace(month=12)

	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

	quarters = {}

	# if filters.get("periodicity")=='Quatarly':
	if start_date.year!=end_date.year:
		while start_date.year <= end_date.year:
			for m in range(0, len(months), 3):
				key = f"{months[m][:3]}-{months[m + 2][:3]}"
				# q = (months[m], months[m + 1], months[m + 2])
				quarters.update({key+" "+str(start_date.year):key})
			start_date=start_date.replace(start_date.year+1)
	else:
		start_month=start_date.replace(month=1).month
		end_month=end_date.replace(month=12).month
		while start_month != end_month <=12:
			for m in range(0, len(months), 3):
				key = f"{months[m][:3]}-{months[m + 2][:3]}"
				# q = (months[m], months[m + 1], months[m + 2])
				quarters.update({key+" "+str(start_date.year): start_date.year})
			start_month+=1
		
        
	return quarters


def getHalfYearly(fiscal_year=None):
    start_date=''
    end_date=''
    year=[]
    year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year),as_dict=True)
    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    if start_year and end_year:
        start = datetime.strptime(str(start_year), "%Y-%m-%d")
        end = datetime.strptime(str(end_year), "%Y-%m-%d")

    # Initialize the start_date to the first day of the year
    start_date = start.replace(month=1)
    end_date = end.replace(month=12)

    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    half_yearly_periods = {}

    if start_date.year!=end_date.year:
        while start_date.year <= end_date.year:
            for m in range(0, len(months), 6):
                key = f"{months[m][:3]}-{months[m + 5][:3]}"
                period = (months[m], months[m + 1], months[m + 2], months[m + 3], months[m + 4], months[m + 5])
                half_yearly_periods.update({key + " " + str(start_date.year): period})
            start_date = start_date.replace(year=start_date.year + 1)

    else:
        start_month=start_date.replace(month=1).month
        end_month=end_date.replace(month=12).month
        while start_month != end_month <=12:
            for m in range(0, len(months), 6):
                key = f"{months[m][:3]}-{months[m + 5][:3]}"
                period = (months[m], months[m + 1], months[m + 2],months[m + 3], months[m + 4], months[m + 5])
                half_yearly_periods.update({key + " " + str(start_date.year): period})
            start_month+=1

    
             
    

    return half_yearly_periods