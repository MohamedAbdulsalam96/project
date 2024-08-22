import frappe
import calendar
from frappe.utils import getdate,add_to_date,time_diff_in_hours,flt

from datetime import datetime,timedelta


def execute(filters):
    data=getData(filters)
    chart = get_chart(data,filters)
    return getColumn(filters), getData(filters),None , chart



def condition(filters):
    conditions=""
    if filters.get('emp'):
        conditions +=" AND a.employee='%s'" % filters.get('emp') 
    if filters.get('company'):
        conditions +=" AND e.company='%s'" % filters.get('company') 
    print('conditions--',conditions)
    return conditions

def get_bonus_condition(employee_name=None,company_name=None):
    conditions=""
    if employee_name !=None:
        conditions +=" AND a.employee='%s'" % employee_name
    if company_name!=None:
        conditions +=" AND e.company='%s'" % company_name
    
    return conditions


def getColumn(filters):
    columns =[]
    
    date_ranges=[]
    
    columns.append( {
            "fieldname": "employee",
            "label": "Employee",
            "fieldtype": "Link",
            "options":'Employee'})
    columns.append( {
            "fieldname": "employee_name",
            "label": "Employee Name",
            "fieldtype": "Link",
            "options":'Employee'})
    columns.append({
            "fieldname": "report_to",
            "label": "Report To",
            "fieldtype": "Link",
            "options":'Employee'})
    columns.append({
            "fieldname": "department",
            "label": "Department",
             "fieldtype": "Link",
            "options":'Department',
            "width":"250px"}),
    columns.append({
            "fieldname": "designation",
            "label": "Designation",
            "fieldtype": "Link",
            "options":'Employee',
            "width":"250px"}),
    columns.append({
            "fieldname": "energy_point_rule",
            "label": "Energy point Rule",
            "fieldtype": "Link",
            "options":'Energy Point Rule',
            "width":"250px"},)
    columns.append({
            "fieldname": "weightage",
            "label": "Weightage",
            "fieldtype": "Data"})
    
    
    if filters.get("periodicity")=="Monthly":
        month=getMonths(filters)
        for key,value in month.items():
           
            columns.append({
        "fieldname":key+"target",
        "label": key+" Target",
        "fieldtype": "Float"}) 

            columns.append({
            "fieldname": key+"achieved",
            "label": key+(" Achieved"),
                "fieldtype": "Float"})
        
            
            columns.append({
        "fieldname":key+"score",
        "label": key+" Score",
        "fieldtype": "Float"})
            
    
       
       
       
    if filters.get("periodicity")=="Quatarly":
        months=getQuarters(filters)
       
        for key,value in months.items():
           
            columns.append({
        "fieldname":key+"target",
        "label": key+" Target",
        "fieldtype": "Float"})
            
            columns.append({
            "fieldname": key+"achieved",
            "label": key+(" Achieved"),
                "fieldtype": "Float"})
        
            columns.append({
        "fieldname":key+"score",
        "label": key+" Score",
        "fieldtype": "float"})
            
            
    if filters.get("periodicity")=="Half Yearly":
        halfyears=getHalfYearly(filters)

        for key,value in halfyears.items():
           
            columns.append({
        "fieldname":key+"target",
        "label": key+" Target",
        "fieldtype": "Float"})
            
            columns.append({
            "fieldname": key+"achieved",
            "label": key+(" Achieved"),
                "fieldtype": "Float"})
            
            
            columns.append({
        "fieldname":key+"score",
        "label": key+" Score",
        "fieldtype": "Float"})
            
    


    if filters.get("periodicity")=="Yearly":
        yers=getYears(filters)
        for x in yers:
            
            columns.append({
        "fieldname": x.get('from_date')+"-"+x.get('to_date')+"target",
        "label": x.get('from_date')+"-"+x.get('to_date')+" Target",
        "fieldtype": "Float"})

            columns.append({
        "fieldname": x.get('from_date')+"-"+x.get('to_date')+"achieved",
        "label": x.get('from_date')+"-"+x.get('to_date')+(" Achieved"),
        "fieldtype": "Float"})
            
            columns.append({
        "fieldname": x.get('from_date')+"-"+x.get('to_date')+"score",
        "label": x.get('from_date')+"-"+x.get('to_date')+" Score",
        "fieldtype": "Float"})    

  
    return columns



def getData(filters):
    lst=[]
    
    if filters.get("periodicity")=='Monthly' :
         lt=get_monthly_data(filters)
         lst.extend(lt)

    if filters.get("periodicity")=='Quatarly':
         lt=get_Data_Quarterly(filters)
         lst.extend(lt)

    if filters.get("periodicity")=='Half Yearly':
        lt=get_data_halfyearly(filters)
        lst.extend(lt)

    if filters.get("periodicity")=='Yearly':
        lt=get_data_yearly(filters)
        print(lt)
        lst.extend(lt)                
    
    return lst

    

def getMonths(filters,fiscal_year=None):
    start_date=''
    end_date=''
    year=[]
    if filters:
        year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(filters.get('fy')),as_dict=True)
    else:
         year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year),as_dict=True)   
    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    # frm = filters.get("from_date")
    # to = filters.get("to_date")
    months={}
    if start_year and end_year:
        start_date = datetime.strptime(str(start_year), "%Y-%m-%d")
        end_date = datetime.strptime(str(end_year), "%Y-%m-%d")
        
    while start_date <= end_date:
        month = start_date.strftime("%B %Y")
        
        months.update({start_date.strftime("%B %Y"):start_date.month})
        if start_date.month == 12:
            start_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            start_date = start_date.replace(month=start_date.month + 1, day=1)
    return months


def getQuarters(filters,fiscal_year=None):
    start_date=''
    end_date=''
    year=[]
    if filters:
        year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(filters.get('fy')),as_dict=True)
    else:
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
                q = (months[m], months[m + 1], months[m + 2])
                quarters.update({key+" "+str(start_date.year): q})
            start_date=start_date.replace(start_date.year+1)
    else:
        start_month=start_date.replace(month=1).month
        end_month=end_date.replace(month=12).month
        while start_month != end_month <=12:
            for m in range(0, len(months), 3):
                key = f"{months[m][:3]}-{months[m + 2][:3]}"
                q = (months[m], months[m + 1], months[m + 2])
                quarters.update({key+" "+str(start_date.year): q})
            start_month+=1
        
        
    return quarters


def getHalfYearly(filters,fiscal_year=None):
    start_date=''
    end_date=''
    year=[]
    if filters:
        year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(filters.get('fy')),as_dict=True)
    else:
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


def getYears(filters,fiscal_year=None):
    if filters:
        year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(filters.get('fy')),as_dict=True)
    else:
         year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fiscal_year),as_dict=True)
    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    if start_year and end_year:
        from_date = datetime.strptime(str(start_year), "%Y-%m-%d")
        to_date = datetime.strptime(str(end_year), "%Y-%m-%d")
    year_set=[]
    while from_date.year <= to_date.year:
            start_date = from_date.replace(month=1, day=1)
            end_date =  from_date.replace(month=12, day=31)
            
            
            if from_date.year == to_date.year:
                end_date = to_date
            
            year_set.append({"from_date": start_date.strftime("%d-%m-%Y"), "to_date": end_date.strftime("%d-%m-%Y")})
            
            from_date = from_date.replace(year=from_date.year + 1)


    return year_set

#---------------------------------------------------------------------
# \\\\start ORIGINAL CODE////----------------------

def get_monthly_data(filters,fiscal_year=None,employee_name=None,company_name=None):
    lst=[]
    fy=0
    dynamic={}
    conditions=''
    if filters:
        fy=filters.get("fy")
        conditions=condition(filters)
    if fiscal_year:
         fy=fiscal_year
         conditions=get_bonus_condition(employee_name,company_name)

    year=frappe.db.sql("""SELECT year_start_date,year_end_date,YEAR(year_start_date) AS year FROM `tabFiscal Year` WHERE name='{}';""".format(fy),as_dict=True)
    print('year--',year)
    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    ex_year=year[0].get('year')
    
    
    employee_prasent=set()
  
    data=frappe.db.sql("""SELECT DISTINCT a.employee, a.employee_name,a.reports_to,a.department,a.designation,t.energy_point_rule,t.weightage_,e.user_id,a.disabled FROM `tabPerformance Target Variable` AS a, `tabPerformance Target Variable Items` AS t,`tabEmployee` AS e WHERE a.name = t.parent%s AND a.employee = e.name ORDER BY a.employee ASC , t.energy_point_rule ASC;""" % conditions)
    print('data------',data)
    rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent AND p.disabled=0 ORDER BY p.employee ASC;""",as_dict=True)
    print('rules--',rules)
    employee=frappe.db.get_all('Employee',{"status":"Active"},['*'])
    print('employee--',employee)
    for i in range(len(data)):
        temp=[]
        x=data[i]
        temp.append(x)
        
        employee_name=x[1]
        if employee_name not in employee_prasent and x[8] !=1:
            dynamic={ 
                "employee":x[0],
                "employee_name":x[1],
                "report_to":x[2],
                "department":x[3],
                "designation":x[4],  
                "energy_point_rule":"",
                "weightage":"100",
                "user":x[7],
                "employee_id":x[0]}
            employee_prasent.add(x[1])
            lst.append(dynamic)
        
        if x[8] !=1:
            for y in temp:
                dynamic={
                    "employee_name":"",
                    "employee":"",
                    "report_to":"",
                    "department":"",
                    "designation":"",
                    "energy_point_rule":y[5],
                    "weightage":x[6],
                    "user":x[7],
                    "employee_id":x[0]}

                lst.append(dynamic)
       
    months=getMonths(filters,fiscal_year=fiscal_year)
    
    # target_data=frappe.get_all('Performance Target Variable Items',['annual_target','energy_point_rule','weightage_'])
    target_data=frappe.db.sql(""" select pi.employee ,pi.maximum_allowed_score_in_lines,p.annual_target,p.energy_point_rule,p.weightage_ from `tabPerformance Target Variable Items` as p 
                              left outer join `tabPerformance Target Variable` as pi ON p.parent=pi.name 
                              left outer join `tabEmployee` as e ON e.employee=pi.employee;""",as_dict=1)
    print('target_data-',target_data)
    print('=====',lst)
    for rule in rules:
        emp=frappe.get_doc('Employee',rule.employee)
        for key,values in months.items():
            querry="""SELECT  name,creation ,points,user,rule
                FROM `tabEnergy Point Log`
                WHERE rule = %s
                AND MONTH(creation)=%s
                AND DATE(creation) BETWEEN %s AND %s AND YEAR(creation)=%s AND user=%s;"""
            rules_data=frappe.db.sql(querry, ( rule.get("energy_point_rule"), values, start_year, end_year,key.split(" ")[1],emp.user_id),as_dict=True)
            print('rules_data--',rules_data)           
            if rules_data:
                for dd in rules_data:
                    year=datetime.date(dd.get('creation')).year
                    userid_1=dd.get('user')
                    nkey=key.split(" ")
                  
                    # print("rulrulrrrrr",dd.get('rule') )
                    # print("poiiiiiiiii",dd.get('points'))
                    for item in lst:
                           
                            if item.get(key+"achieved")and item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
                                        val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                        item[key+"achieved"]+=dd.get('points')
                                        if val:
                                            item[key+"achieved"]+=val


                            elif item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
                                    val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                   
                                    item[key+"achieved"]=dd.get('points')
                                    if val:
                                            item[key+"achieved"]+=val
           
            for tar in target_data:
                for item in lst:
                    if item.get("energy_point_rule")==tar.get("energy_point_rule") and tar.get('employee')==item.get('employee_id'):
                        item[key+"target"]=round(tar.get("annual_target")/12,2)
                        pt_annual=round(tar.get("annual_target")/12,2)
                        pt_ac=item.get(key+"achieved")
                        pt_w=item.get("weightage")
                        if pt_annual< 0 and flt(pt_ac)==0:
                            item[key+"score"]=100
                        if pt_w and pt_ac and pt_annual:
                
                            
                            if pt_ac < pt_annual and pt_ac < 0 and pt_annual <0:
                                final=pt_ac-(pt_annual)
                                sc=round((final/pt_annual)*100,2)
                                item[key+"score"]=-sc
                            
                            elif pt_ac > pt_annual and pt_ac < 0 and pt_annual <0:
                                final=pt_ac-(pt_annual)
                                sc=round((final/pt_annual)*100,2)
                                item[key+"score"]=-round(sc, 2)
                            else:
                                sc=round((pt_ac/pt_annual)*100,2)
                                item[key+"score"]=round(sc, 2)
                        if flt(tar.get("maximum_allowed_score_in_lines"))>0:
                            if flt(item.get(str(key)+"score"))>flt(tar.get("maximum_allowed_score_in_lines")):
                                item[key+"score"]=flt(tar.get("maximum_allowed_score_in_lines"))
                            if flt(item.get(str(key)+"score"))< -flt(tar.get("maximum_allowed_score_in_lines")):
                                item[key+"score"]=-flt(tar.get("maximum_allowed_score_in_lines"))




                                        

    for key,value in months.items():
        e_rule=[]
        for emp in employee:
            target_achieved=[]
            target_target=[]
            target_score =[]
            ac_final=0.0
            final=0.0
            final_tar=0.0
            for item in lst:
                
                if item.get('user')==emp.get('user_id') and item.get('energy_point_rule') !='':
                    target_achieved.append(item.get(key+"achieved") if item.get(key+"achieved") else 0)
                    target_target.append(item.get(key+"target") if item.get(key+"target") else 0)
                    e_rule.append(item.get('energy_point_rule'))
                    target_score.append(item.get('weightage')*item.get(key+"score")/100 if item.get(key+"score") else 0)
            
            if target_achieved and len(target_achieved)>1:
                ac_final=sum(target_achieved)
            elif target_achieved and len(target_achieved)==1:
                ac_final=sum(target_achieved)
            if target_target and len(target_target)>1:
                final_tar=sum(target_target)
            
            elif target_achieved and len(target_achieved)==1:
                 final_tar=sum(target_target)

            if target_score and len(target_score)>1:
                final= sum(target_score)
            elif target_achieved and len(target_achieved)==1:
                final= sum(target_score)
                
            for item in lst:
                if item.get('energy_point_rule')=='' and item.get('user')==emp.get('user_id'):
                    if ac_final or final_tar:
                        item.update({key+"score":round(final,2)})
                        item.update({key+"achieved":round(ac_final,2)})
                        item.update({key+"target":round(final_tar,2)})             
                                               
    return lst

# end original code ------------------------------
#-----------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------

# optimise attempt 3 Start
# def get_monthly_data(filters, fiscal_year=None, employee_name=None, company_name=None):
#     lst = []
#     dynamic = {}
#     conditions = ''
#     fy = filters.get("fy") if filters else fiscal_year
#     conditions = condition(filters) if filters else get_bonus_condition(employee_name, company_name)
    
#     year = frappe.db.sql(f"""
#         SELECT year_start_date, year_end_date, YEAR(year_start_date) AS year
#         FROM `tabFiscal Year`
#         WHERE name='{fy}';
#     """, as_dict=True)[0]
    
#     start_year = year.get('year_start_date')
#     end_year = year.get('year_end_date')
#     ex_year = year.get('year')

#     employee_prasent = set()
#     print(conditions)
#     data = frappe.db.sql(f"""
#         SELECT DISTINCT a.employee, a.employee_name, a.reports_to, a.department, a.designation,
#                         t.energy_point_rule, t.weightage_, e.user_id, a.disabled
#         FROM `tabPerformance Target Variable` AS a
#         JOIN `tabPerformance Target Variable Items` AS t ON a.name = t.parent
#         JOIN `tabEmployee` AS e ON a.employee = e.name
#         WHERE 1=1 {conditions}
#         ORDER BY a.employee ASC, t.energy_point_rule ASC;
#     """, as_dict=True)
#     print('data--3',data)
#     rules = frappe.db.sql(f"""
#         SELECT DISTINCT i.energy_point_rule, a.employee
#         FROM `tabPerformance Target Variable Items` AS i
#         JOIN `tabPerformance Target Variable` AS a ON a.name = i.parent
#         JOIN `tabEmployee` AS e ON a.employee = e.name
#         WHERE a.disabled = 0 {conditions}
#         ORDER BY a.employee ASC;
#     """, as_dict=True)

#     # employees = frappe.db.get_all('Employee', {"status": "Active"},['user_id'])
    
#     employees_query = f"""
#             SELECT e.user_id
#             FROM `tabPerformance Target Variable` AS a
#             JOIN `tabEmployee` AS e ON a.employee = e.name
#             WHERE a.disabled = 0 {conditions}
#             """
#     employees = frappe.db.sql(employees_query, as_dict=True)

#     for x in data:
#         if x['employee_name'] not in employee_prasent and x['disabled'] != 1:
#             dynamic = { 
#                 "employee": x['employee'],
#                 "employee_name": x['employee_name'],
#                 "report_to": x['reports_to'],
#                 "department": x['department'],
#                 "designation": x['designation'],  
#                 "energy_point_rule": "",
#                 "weightage": "100",
#                 "user": x['user_id'],
#                 "employee_id": x['employee']
#             }
#             employee_prasent.add(x['employee_name'])
#             lst.append(dynamic)
        
#         if x['disabled'] != 1:
#             dynamic = {
#                 "employee_name": "",
#                 "employee": "",
#                 "report_to": "",
#                 "department": "",
#                 "designation": "",
#                 "energy_point_rule": x['energy_point_rule'],
#                 "weightage": x['weightage_'],
#                 "user": x['user_id'],
#                 "employee_id": x['employee']
#             }
#             lst.append(dynamic)
    
#     months = getMonths(filters, fiscal_year=fiscal_year)
    
#     target_data = frappe.db.sql(f"""
#         SELECT DISTINCT a.employee, a.maximum_allowed_score_in_lines,i.annual_target, i.energy_point_rule, i.weightage_
#         FROM `tabPerformance Target Variable Items` AS i
#         JOIN `tabPerformance Target Variable` AS a ON a.name = i.parent
#         JOIN `tabEmployee` AS e ON a.employee = e.name
#         WHERE a.disabled = 0 {conditions}
#         ORDER BY a.employee ASC;
#     """, as_dict=True)
    
#     for rule in rules:
#         emp=frappe.get_doc('Employee',rule.employee)
#         for key,values in months.items():
#             querry="""SELECT  name,creation ,points,user,rule
#                 FROM `tabEnergy Point Log`
#                 WHERE rule = %s
#                 AND MONTH(creation)=%s
#                 AND DATE(creation) BETWEEN %s AND %s AND YEAR(creation)=%s AND user=%s;"""
#             rules_data=frappe.db.sql(querry, ( rule.get("energy_point_rule"), values, start_year, end_year,key.split(" ")[1],emp.user_id),as_dict=True)
#             # print('rules_data--',rules_data)           
#             if rules_data:
#                 for dd in rules_data:
#                     year=datetime.date(dd.get('creation')).year
#                     userid_1=dd.get('user')
#                     nkey=key.split(" ")
                  
#                     # print("rulrulrrrrr",dd.get('rule') )
#                     # print("poiiiiiiiii",dd.get('points'))
#                     for item in lst:
                           
#                             if item.get(key+"achieved")and item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
#                                         val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
#                                         item[key+"achieved"]+=dd.get('points')
#                                         if val:
#                                             item[key+"achieved"]+=val


#                             elif item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
#                                     val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                   
#                                     item[key+"achieved"]=dd.get('points')
#                                     if val:
#                                             item[key+"achieved"]+=val
           
#             for tar in target_data:
#                 for item in lst:
#                     if item.get("energy_point_rule")==tar.get("energy_point_rule") and tar.get('employee')==item.get('employee_id'):
#                         item[key+"target"]=round(tar.get("annual_target")/12,2)
#                         pt_annual=round(tar.get("annual_target")/12,2)
#                         pt_ac=item.get(key+"achieved")
#                         pt_w=item.get("weightage")
#                         if pt_annual< 0 and flt(pt_ac)==0:
#                             item[key+"score"]=100
#                         if pt_w and pt_ac and pt_annual:
                
                            
#                             if pt_ac < pt_annual and pt_ac < 0 and pt_annual <0:
#                                 final=pt_ac-(pt_annual)
#                                 sc=round((final/pt_annual)*100,2)
#                                 item[key+"score"]=-sc
                            
#                             elif pt_ac > pt_annual and pt_ac < 0 and pt_annual <0:
#                                 final=pt_ac-(pt_annual)
#                                 sc=round((final/pt_annual)*100,2)
#                                 item[key+"score"]=-round(sc, 2)
#                             else:
#                                 sc=round((pt_ac/pt_annual)*100,2)
#                                 item[key+"score"]=round(sc, 2)
#                         if flt(tar.get("maximum_allowed_score_in_lines"))>0:
#                             if flt(item.get(str(key)+"score"))>flt(tar.get("maximum_allowed_score_in_lines")):
#                                 item[key+"score"]=flt(tar.get("maximum_allowed_score_in_lines"))
#                             if flt(item.get(str(key)+"score"))< -flt(tar.get("maximum_allowed_score_in_lines")):
#                                 item[key+"score"]=-flt(tar.get("maximum_allowed_score_in_lines"))


#     for key, value in months.items():

#         for emp in employees:
#             target_achieved = sum(item.get(f"{key}achieved", 0) for item in lst if item['user'] == emp['user_id'] and item['energy_point_rule'])
#             target_target = sum(item.get(f"{key}target", 0) for item in lst if item['user'] == emp['user_id'] and item['energy_point_rule'])
#             target_score = sum(item.get("weightage", 0) * item.get(f"{key}score", 0) / 100 for item in lst if item['user'] == emp['user_id'] and item['energy_point_rule'])
            
#             for item in lst:
#                 if item['energy_point_rule'] == '' and item['user'] == emp['user_id']:
#                     item.update({
#                         f"{key}score": round(target_score, 2),
#                         f"{key}achieved": round(target_achieved, 2),
#                         f"{key}target": round(target_target, 2)
#                     })

#     return lst


def get_Data_Quarterly(filters,fiscal_year=None,employee_name=None,company_name=None):
    lst=[]
    dynamic={}
    tncp={}
    fy=0
    # print("gggggg",fiscal_year)
    # fy=filters.get("fy")
    # fys=fy.split("-")
    conditions=''
    if filters:
        fy=filters.get("fy")
        conditions=condition(filters)
    if fiscal_year:
         fy=fiscal_year
         conditions=get_bonus_condition(employee_name,company_name)
    
    year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fy),as_dict=True)
        
    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    employee_prasent=set()
    # conditions=condition(filters)
    rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)
   
    data=frappe.db.sql("""SELECT DISTINCT a.employee, a.employee_name,a.reports_to,a.department,a.designation,t.energy_point_rule,t.weightage_,e.user_id,a.disabled FROM `tabPerformance Target Variable` AS a, `tabPerformance Target Variable Items` AS t,`tabEmployee` AS e WHERE a.name = t.parent%s AND a.employee = e.name ORDER BY a.employee ASC, t.energy_point_rule ASC;""" % conditions)
   
    employee=frappe.get_all('Employee',['*'])
    
    for i in range(len(data)):
            temp=[]
            x=data[i]
            temp.append(x)
            
            employee_name=x[1]
            if employee_name not in employee_prasent and x[8] !=1:
                dynamic={ 
                    "employee":x[0],
                    "employee_name":x[1],
                    "report_to":x[2],
                    "department":x[3],
                    "designation":x[4],  
                    "energy_point_rule":"",
                    "weightage":"100",
                    "user":x[7],
                    "employee_id":x[0]
                }
                employee_prasent.add(x[1])
                lst.append(dynamic)
            if  x[8] !=1:
                for y in temp:
                    dynamic={
                        "employee_name":"",
                        "employee":"",
                        "report_to":"",
                        "department":"",
                        "designation":"",
                        "energy_point_rule":y[5],
                        "weightage":x[6],
                        "user":x[7],
                        "employee_id":x[0]}

                    lst.append(dynamic)
   
    months=getQuarters(filters,fiscal_year)
    
    # target_data=frappe.db.get_all('Performance Target Variable Items',['annual_target','energy_point_rule','weightage_'])
    target_data=frappe.db.sql(""" select pi.employee ,pi.maximum_allowed_score_in_lines,p.annual_target,p.energy_point_rule,p.weightage_ from `tabPerformance Target Variable Items` as p 
                              left outer join `tabPerformance Target Variable` as pi ON p.parent=pi.name 
                              left outer join `tabEmployee` as e ON e.employee=pi.employee;""",as_dict=1)
    
    for rule in rules:
        emp=frappe.get_doc('Employee',rule.employee)
        for key,values in months.items():
           
            querry="""SELECT  creation ,points,user,rule
                FROM `tabEnergy Point Log`
                WHERE rule = %s
                AND MONTHNAME(creation) IN %s
                AND DATE(creation) BETWEEN %s AND %s AND YEAR(creation)=%s AND user=%s;"""
            rules_data=frappe.db.sql(querry, ( rule.get("energy_point_rule"), values, start_year, end_year,key.split(" ")[1],emp.user_id),as_dict=True)
                    
          

            if rules_data:
                for dd in rules_data:
              
                    year=datetime.date(dd.get('creation')).year
                    userid_1=dd.get('user')
                    nkey=key.split(" ")
            
                    for item in lst:
                            if item.get(key+"achieved")and item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                item[key+"achieved"]+=dd.get('points')
                                if val:
                                    item[key+"achieved"]+=val

                            elif item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                item[key+"achieved"]=dd.get('points')
                                if val:
                                    item[key+"achieved"]+=val

            for tar in target_data:
                for item in lst:
                    if item.get("energy_point_rule")==tar.get("energy_point_rule") and tar.get('employee')==item.get('employee_id'):
                            item[key+"target"]=tar.get("annual_target")/4
                            pt_annual=round(tar.get("annual_target")/4,2)
                            pt_ac=item.get(key+"achieved")
                            pt_w=item.get("weightage")
                            if pt_annual< 0 and flt(pt_ac)==0:
                                item[key+"score"]=100
                            if pt_w and pt_ac and pt_annual:

                                
                                if pt_ac < pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_ac-(pt_annual)
                                    sc=round((final/pt_annual)*100,2)
                                    item[key+"score"]=-sc
                                
                                elif pt_ac > pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_annual-(pt_ac)
                                    sc=round((final/pt_annual)*100,2)
                                    item[key+"score"]=-round(sc, 2)
                                else:
                                    sc=round((pt_ac/pt_annual)*100,2)
                                    item[key+"score"]=round(sc, 2)
            
                    if flt(tar.get("maximum_allowed_score_in_lines"))>0:
                        if flt(item.get(str(key)+"score"))>flt(tar.get("maximum_allowed_score_in_lines")):
                            item[key+"score"]=flt(tar.get("maximum_allowed_score_in_lines"))
                        if flt(item.get(str(key)+"score"))< -flt(tar.get("maximum_allowed_score_in_lines")):
                            item[key+"score"]=-flt(tar.get("maximum_allowed_score_in_lines"))
            # target_score = list(filter(None, map(lambda x: x.get(key+"score") if x.get('user')==emp.user_id else None, lst)))
            # target_achieved= list(filter(None, map(lambda x: x.get(key+"achieved") if x.get('user')==emp.user_id else None, lst)))
            # target_target=list(filter(None, map(lambda x: x.get(key+"target")  if x.get('user')==emp.user_id else None, lst)))
            # final=0
            # ac_final=0
            # final_tar=0
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/len(target_score)
            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)/len(target_achieved)
            
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)/len(target_target)


            #     for item in lst:
            #         if item.get('energy_point_rule')=='' and item.get('user')==emp.user_id:
            #             if final_tar and ac_final:
            #                 item.update({key+"score":round(final,2)})
            #                 item.update({key+"achieved":round(ac_final,2)})
            #             item.update({key+"target":round(final_tar,2)})

    for key,value in months.items():
        for emp in employee:
            target_achieved=[]
            target_target=[]
            target_score =[]
            ac_final=0.0
            final=0.0
            final_tar=0.0
            for item in lst:
                if item.get('user')==emp.get('user_id') and item.get('energy_point_rule') !='':
                    target_achieved.append(item.get(key+"achieved") if item.get(key+"achieved") else 0)
                    target_target.append(item.get(key+"target") if item.get(key+"target") else 0)
                    target_score.append(item.get('weightage')*item.get(key+"score")/100 if item.get(key+"score") else 0)
            
            
            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/100    
            if target_achieved and len(target_achieved)>1:
                ac_final=sum(target_achieved)
            elif target_achieved and len(target_achieved)==1:
                ac_final=sum(target_achieved)
            if target_target and len(target_target)>1:
                final_tar=sum(target_target)
            
            elif target_achieved and len(target_achieved)==1:
                 final_tar=sum(target_target)

            if target_score and len(target_score)>1:
                final= sum(target_score)
            elif target_achieved and len(target_achieved)==1 :
                final= sum(target_score)
                
            for item in lst:
                if item.get('energy_point_rule')=='' and item.get('user')==emp.get('user_id'):
                    if ac_final or final_tar:
                        item.update({key+"score":round(final,2)})
                        item.update({key+"achieved":round(ac_final,2)})
                        item.update({key+"target":round(final_tar,2)})             
           
                   
    
        
    return lst



def get_data_halfyearly(filters,fiscal_year=None,employee_name=None,company_name=None):

    lst=[]
    dynamic={}
    tncp={}
    fy=0
    conditions=''
    if filters:
        fy=filters.get("fy")
        conditions=condition(filters)
    if fiscal_year:
         fy=fiscal_year
         conditions=get_bonus_condition(employee_name,company_name)

    year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fy),as_dict=True)

    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')

    # fys=fy.split("-")
    # conditions=condition(filters)
    employee_prasent=set()

   
    data=frappe.db.sql("""SELECT DISTINCT a.employee, a.employee_name,a.reports_to,a.department,a.designation,t.energy_point_rule,t.weightage_,e.user_id,a.disabled FROM `tabPerformance Target Variable` AS a, `tabPerformance Target Variable Items` AS t,`tabEmployee` AS e WHERE a.name = t.parent%s AND a.employee = e.name ORDER BY a.employee ASC, t.energy_point_rule ASC;""" % conditions)
 
    rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)

    employee=frappe.get_all('Employee',['*'])
    
    for i in range(len(data)):
            temp=[]
            x=data[i]
            temp.append(x)
           


            employee_name=x[1]
            if employee_name not in employee_prasent and x[8] !=1:
                dynamic={ 
                    "employee":x[0],
                    "employee_name":x[1],
                    "report_to":x[2],
                    "department":x[3],
                    "designation":x[4],  
                    "energy_point_rule":"",
                    "weightage":"100",
                    "user":x[7],
                    "employee_id":x[0]
                }
                employee_prasent.add(x[1])
                lst.append(dynamic)
            if x[8] !=1:
                for y in temp:
                    dynamic={
                        "employee_name":"",
                        "employee":"",
                        "report_to":"",
                        "department":"",
                        "designation":"",
                        "energy_point_rule":y[5],
                        "weightage":x[6],
                        "user":x[7],
                        "employee_id":x[0]}

                lst.append(dynamic)
 
    months=getHalfYearly(filters,fiscal_year)
    
    # target_data=frappe.db.get_all('Performance Target Variable Items',['annual_target','energy_point_rule','weightage_'])
    target_data=frappe.db.sql(""" select pi.employee ,pi.maximum_allowed_score_in_lines,p.annual_target,p.energy_point_rule,p.weightage_ from `tabPerformance Target Variable Items` as p 
                              left outer join `tabPerformance Target Variable` as pi ON p.parent=pi.name 
                              left outer join `tabEmployee` as e ON e.employee=pi.employee;""",as_dict=1)
  
    for rule in rules:
        emp=frappe.get_doc('Employee',rule.employee)
        for key,values in months.items():
    
            querry="""SELECT  creation ,points,user,rule
                FROM `tabEnergy Point Log`
                WHERE rule = %s
                AND MONTHNAME(creation) IN %s
                AND DATE(creation) BETWEEN %s AND %s AND YEAR(creation)=%s AND user=%s;"""
            rules_data=frappe.db.sql(querry, ( rule.get("energy_point_rule"), values, start_year, end_year,key.split(" ")[1],emp.user_id),as_dict=True)
                    
                 

            if rules_data:
                for dd in rules_data:
                    
                    year=datetime.date(dd.get('creation')).year
                    userid_1=dd.get('user')
                    nkey=key.split(" ")
                 
                    for item in lst:
                           
                            if item.get(key+"achieved")and item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):    
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                item[key+"achieved"]+=dd.get('points')
                                if val:
                                    item[key+"achieved"]+=val

                            elif item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey[1]):
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                item[key+"achieved"]=dd.get('points')
                                if val:
                                    item[key+"achieved"]+=val

            for tar in target_data:
                for item in lst:
                    if item.get("energy_point_rule")==tar.get("energy_point_rule") and tar.get('employee')==item.get('employee_id'):
                            item[key+"target"]=round(tar.get("annual_target")/6,2)
                            pt_annual=round(tar.get("annual_target")/6,2)
                            pt_ac=item.get(key+"achieved")
                            pt_w=item.get("weightage")
                            if pt_annual< 0 and flt(pt_ac)==0:
                                item[key+"score"]=100
                            if pt_w and pt_ac and pt_annual:

                                
                                if pt_ac < pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_ac-(pt_annual)
                                    sc=round((final/pt_annual)*100,2)
                                    item[key+"score"]=-sc
                                
                                elif pt_ac > pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_annual-(pt_ac)
                                    sc=round((final/pt_annual)*100,2)
                                    item[key+"score"]=-round(sc, 2)
                                else:
                                    sc=round((pt_ac/pt_annual)*100,2)
                                    item[key+"score"]=round(sc, 2)
                              
                    if flt(tar.get("maximum_allowed_score_in_lines"))>0:
                        print(item)
                        if flt(item.get(str(key)+"score"))>flt(tar.get("maximum_allowed_score_in_lines")):
                            item[key+"score"]=flt(tar.get("maximum_allowed_score_in_lines"))
                        if flt(item.get(str(key)+"score"))< -flt(tar.get("maximum_allowed_score_in_lines")):
                            item[key+"score"]=-flt(tar.get("maximum_allowed_score_in_lines"))
            # target_score = list(filter(None, map(lambda x: x.get(key+"score") if x.get('user')==emp.user_id else None, lst)))
            # target_achieved= list(filter(None, map(lambda x: x.get(key+"achieved") if x.get('user')==emp.user_id else None, lst)))
            # target_target=list(filter(None, map(lambda x: x.get(key+"target")  if x.get('user')==emp.user_id else None, lst)))
            # final=0
            # ac_final=0
            # final_tar=0
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/len(target_score)
            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)/len(target_achieved)
            
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)/len(target_target)


            #     for item in lst:
            #         if item.get('energy_point_rule')=='' and item.get('user')==emp.user_id:
            #             if final_tar and ac_final:
            #                 item.update({key+"score":round(final,2)})
            #                 item.update({key+"achieved":round(ac_final,2)})
            #             item.update({key+"target":round(final_tar,2)})
    for key,value in months.items():
       
        for emp in employee:
            target_achieved=[]
            target_target=[]
            target_score =[]
            ac_final=0.0
            final=0.0
            final_tar=0.0
            for item in lst:
                
                if item.get('user')==emp.get('user_id') and item.get('energy_point_rule') !='':
                    target_achieved.append(item.get(key+"achieved") if item.get(key+"achieved") else 0)
                    target_target.append(item.get(key+"target") if item.get(key+"target") else 0)
                    target_score.append(item.get('weightage')*item.get(key+"score")/100 if item.get(key+"score") else 0)
            

            if target_achieved and len(target_achieved)>1:
                ac_final=sum(target_achieved)
            elif target_achieved and len(target_achieved)==1:
                ac_final=sum(target_achieved)
            if target_target and len(target_target)>1:
                final_tar=sum(target_target)
            
            elif target_achieved and len(target_achieved)==1:
                 final_tar=sum(target_target)

            if target_score and len(target_score)>1:
                final= sum(target_score)
            elif target_achieved and len(target_achieved)==1 :
                final= sum(target_score)
                
 

            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/100 
                
            for item in lst:
                if item.get('energy_point_rule')=='' and item.get('user')==emp.get('user_id'):
                    if ac_final or final_tar:
                        item.update({key+"score":round(final,2)})
                        item.update({key+"achieved":round(ac_final,2)})
                        item.update({key+"target":round(final_tar,2)})      

 
    return lst




def get_data_yearly(filters,fiscal_year=None,employee_name=None,company_name=None):
    lst=[]
    dynamic={}
    tncp={}
    fy=0
    conditions=''
    if filters:
        fy=filters.get("fy")
        conditions=condition(filters)
    if fiscal_year:
         fy=fiscal_year
         conditions=get_bonus_condition(employee_name,company_name)

    year=frappe.db.sql("""SELECT year_start_date,year_end_date FROM `tabFiscal Year` WHERE name='{}';""".format(fy),as_dict=True)

    start_year=year[0].get('year_start_date')
    end_year=year[0].get('year_end_date')
    # conditions=condition(filters)
    employee_prasent=set()

    
    data=frappe.db.sql("""SELECT DISTINCT a.employee, a.employee_name,a.reports_to,a.department,a.designation,t.energy_point_rule,t.weightage_,e.user_id,a.disabled  FROM `tabPerformance Target Variable` AS a, `tabPerformance Target Variable Items` AS t,`tabEmployee` AS e WHERE a.name = t.parent%s AND a.employee = e.name ORDER BY a.employee ASC, t.energy_point_rule ASC;""" % conditions)
   
  

   
    rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)

    
    for i in range(len(data)):
            temp=[]
            x=data[i]
            temp.append(x)
          


            employee_name=x[1]
            if employee_name not in employee_prasent and x[8] !=1:
                dynamic={ 
                    "employee":x[0],
                    "employee_name":x[1],
                    "report_to":x[2],
                    "department":x[3],
                    "designation":x[4],  
                    "energy_point_rule":"",
                    "weightage":"100",
                    "user":x[7],
                    "employee_id":x[0]
                }
                employee_prasent.add(x[1])
                lst.append(dynamic)
            if x[8] !=1:
                for y in temp:
                    dynamic={
                        "employee_name":"",
                        "employee":"",
                        "report_to":"",
                        "department":"",
                        "designation":"",
                        "energy_point_rule":y[5],
                        "weightage":x[6],
                        "user":x[7],
                        "employee_id":x[0]}

                lst.append(dynamic)
  
    years=getYears(filters,fiscal_year)
    target_data=frappe.db.sql(""" select pi.employee ,pi.maximum_allowed_score_in_lines,p.annual_target,p.energy_point_rule,p.weightage_ from `tabPerformance Target Variable Items` as p 
                              left outer join `tabPerformance Target Variable` as pi ON p.parent=pi.name 
                              left outer join `tabEmployee` as e ON e.employee=pi.employee;""",as_dict=1)
    for rule in rules:
        emp=frappe.get_doc('Employee',rule.employee)
        for x in years:
        
            querry="""SELECT  creation ,points,user,rule
                FROM `tabEnergy Point Log`
                WHERE rule = %s
                AND DATE(creation) BETWEEN %s AND %s  AND user=%s;"""
            rules_data=frappe.db.sql(querry, ( rule.get("energy_point_rule"), start_year, end_year,emp.user_id),as_dict=True)
                    
                  

            if rules_data:
                for dd in rules_data:
                   
                    year=datetime.date(dd.get('creation')).year
                    userid_1=dd.get('user')
                    nkey=x.get('from_date').split("-")[2]
                   
                    for item in lst:
                            
                            if item.get(x.get('from_date')+"-"+x.get('to_date')+"achieved")and item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey):
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])

                                item[x.get('from_date')+"-"+x.get('to_date')+"achieved"]+=dd.get('points')
                                if val:
                                    item[x.get('from_date')+"-"+x.get('to_date')+"achieved"]+=val


                            elif item['energy_point_rule'] == dd.get('rule') and item['user']==userid_1 and str(year)==str(nkey):
                                val=frappe.db.get_value("Energy Point Log",{"revert_of":dd.get("name")},["points"])
                                item[x.get('from_date')+"-"+x.get('to_date')+"achieved"]=dd.get('points')
                                if val:
                                    item[x.get('from_date')+"-"+x.get('to_date')+"achieved"]+=val

            for tar in target_data:
                for item in lst:
                    # doc=frappe.get_doc("Performance Target Variable",tar.parent)
                    # print(tar.employee,item.get('employee'),tar.get("energy_point_rule"),item.get("energy_point_rule"))
                    if item.get("energy_point_rule")==tar.get("energy_point_rule") and tar.get('employee')==item.get('employee_id'):
                            
                            item[x.get('from_date')+"-"+x.get('to_date')+"target"]=tar.get("annual_target")
                            pt_annual=tar.get("annual_target")
                            pt_ac=item.get(x.get('from_date')+"-"+x.get('to_date')+"achieved")
                            pt_w=item.get("weightage")
                            # if pt_w and pt_ac and pt_annual:
                            #     sc=round((pt_ac/pt_annual)*100,2)
                            #     item[x.get('from_date')+"-"+x.get('to_date')+"score"]=round(sc, 2)

                            if pt_annual< 0 and flt(pt_ac)==0:
                                item[x.get('from_date')+"-"+x.get('to_date')+"score"]=100

                            if pt_w and pt_ac and pt_annual:

                                
                                if pt_ac < pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_ac-(pt_annual)
                                    sc=round((final/pt_annual)*100,2)
                                    item[x.get('from_date')+"-"+x.get('to_date')+"score"]=-sc
                                elif pt_ac > pt_annual and pt_ac < 0 and pt_annual <0:
                                    final=pt_annual-(pt_ac)
                                    sc=round((final/pt_annual)*100,2)
                                    item[x.get('from_date')+"-"+x.get('to_date')+"score"]=-round(sc, 2)
                                else:
                                    sc=round((pt_ac/pt_annual)*100,2)
                                    item[x.get('from_date')+"-"+x.get('to_date')+"score"]=round(sc, 2)
                
                    if flt(tar.get("maximum_allowed_score_in_lines"))>0:
                        print(item)
                        if flt(item.get(str(x.get('from_date'))+"-"+str(x.get('to_date'))+"score"))>flt(tar.get("maximum_allowed_score_in_lines")):
                            item[x.get('from_date')+"-"+x.get('to_date')+"score"]=flt(tar.get("maximum_allowed_score_in_lines"))
                        if flt(item.get(str(x.get('from_date'))+"-"+str(x.get('to_date'))+"score"))< -flt(tar.get("maximum_allowed_score_in_lines")):
                            item[x.get('from_date')+"-"+x.get('to_date')+"score"]=-flt(tar.get("maximum_allowed_score_in_lines"))                      
                               

            # target_score = list(filter(None, map(lambda y: y.get(x.get('from_date')+"-"+x.get('to_date')+"score") if y.get('user')==emp.user_id else None, lst)))
            # target_achieved= list(filter(None, map(lambda y: y.get(x.get('from_date')+"-"+x.get('to_date')+"achieved") if y.get('user')==emp.user_id else None, lst)))
            # target_target=list(filter(None, map(lambda y: y.get(x.get('from_date')+"-"+x.get('to_date')+"target")  if y.get('user')==emp.user_id else None, lst)))
            # final=0
            # ac_final=0
            # final_tar=0
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/len(target_score)
            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)/len(target_achieved)
            
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)/len(target_target)


            #     for item in lst:
            #         if item.get('energy_point_rule')=='' and item.get('user')==emp.user_id:
            #             if final_tar and ac_final:
            #                 item.update({x.get('from_date')+"-"+x.get('to_date')+"score":round(final,2)})
            #                 item.update({x.get('from_date')+"-"+x.get('to_date')+"achieved":round(ac_final,2)})
            #             item.update({x.get('from_date')+"-"+x.get('to_date')+"target":round(final_tar,2)})
    employee=frappe.get_all('Employee',['*'])

    for x in years:
       
        for emp in employee:
            target_achieved=[]
            target_target=[]
            target_score =[]
            ac_final=0.0
            final=0.0
            final_tar=0.0
            for item in lst:
                
                if item.get('user')==emp.get('user_id') and item.get('energy_point_rule') !='':
                    target_achieved.append(item.get(x.get('from_date')+"-"+x.get('to_date')+"achieved") if item.get(x.get('from_date')+"-"+x.get('to_date')+"achieved") else 0)
                    target_target.append(item.get(x.get('from_date')+"-"+x.get('to_date')+"target") if item.get(x.get('from_date')+"-"+x.get('to_date')+"target") else 0)
                    target_score.append(item.get('weightage')*item.get(x.get('from_date')+"-"+x.get('to_date')+"score")/100  if item.get(x.get('from_date')+"-"+x.get('to_date')+"score") else 0)
            
            if target_achieved and len(target_achieved)>1:
                ac_final=sum(target_achieved)
            elif target_achieved and len(target_achieved)==1:
                ac_final=sum(target_achieved)
            if target_target and len(target_target)>1:
                final_tar=sum(target_target)
            
            elif target_achieved and len(target_achieved)==1:
                 final_tar=sum(target_target)

            if target_score and len(target_score)>1:
                final= sum(target_score)
            elif target_achieved and len(target_achieved)==1 :
                final= sum(target_score)

            # if target_achieved and len(target_achieved)>1:
            #     ac_final=sum(target_achieved)
            # if target_target and len(target_target)>1:
            #     final_tar=sum(target_target)
            # if target_score and len(target_score)>1:
            #     final=sum(target_score)/100 
                
            for item in lst:
                if item.get('energy_point_rule')=='' and item.get('user')==emp.get('user_id'):
                    if ac_final or final_tar:
                        item.update({x.get('from_date')+"-"+x.get('to_date')+"score":round(final,2)})
                        item.update({x.get('from_date')+"-"+x.get('to_date')+"achieved":round(ac_final,2)})
                        item.update({x.get('from_date')+"-"+x.get('to_date')+"target":round(final_tar,2)})                      
    

    return lst




def get_chart(data,filters):
   
    tnc_chart={}
    if filters.get("periodicity")=="Monthly": 
        conditions=chart_condition(filters)
        data=getData(filters)
        # rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)
        emp=frappe.db.sql("""select e.name, e.user_id from `tabEmployee` as e right outer join `tabPerformance Target Variable` as p ON p.employee=e.employee where p.disabled=0 {};""".format(conditions),as_dict=True)             
        months=getMonths(filters)
        
        finaldata=[]
        lable=[]
        for name in emp:
            lable.append(name.get('name'))
            rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent AND p.employee='{}';""".format(name.get('name')), as_dict=True)
            for rule in rules:
                rule_present=set()
                final_tnc=[]
                
               
                for key ,values in months.items():
                    tnc_pt=0
                    tnc_pt_float=0
                    for dd in data:
                            
                        if dd['energy_point_rule']==rule.get('energy_point_rule') and dd['user']==name.get('user_id'):
                           
                          
                           
                            tnc_pt+= dd.get(key+"achieved") if dd.get(key+"achieved") else 0
                            tnc_pt_float = "{:.2f}".format(tnc_pt)
                            # tnc_sc_pt+=dd.get(key+"score") if dd.get(key+"score") else 0
                            # tnc_pt_sc_float = "{:.2f}".format(tnc_sc_pt) left outer join `tabAttendance`
                            final_tnc.append(tnc_pt_float)
                            rule_present.add(rule.get('energy_point_rule'))
                if final_tnc:
                    finaldata.append({'name':rule.get('energy_point_rule'), 'values': final_tnc})
                  
             
                    tnc_chart= {
                                "data": {
                                    'labels': lable,
                                    'datasets': finaldata,
                                    
                                },
                                
                            }
                    tnc_chart["type"] = "line"

                    # tnc_chart["height"] = 1000
                    # tnc_chart['axisOptions']=  {'xAxisMode': 'tick'}

        
                 
        
    
 
    if filters.get("periodicity")=="Quatarly": 
        data=getData(filters)
        lable=[]
        # rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)
        emp=frappe.db.sql("""select e.name, e.user_id from `tabEmployee` as e right outer join `tabPerformance Target Variable` as p ON p.employee=e.employee where p.disabled=0;""",as_dict=True)       
        months=getQuarters(filters)
        finaldata=[]
        
        for name in emp:
            lable.append(name.get('name'))
            rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee,p.disabled from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent AND p.employee='{}';""".format(name.get('name')), as_dict=True)
            for rule in rules:
                rule_present=set()
                final_tnc=[]
               
                print("Employee= {} Rule= {}".format(rule.get('employee'),rule.get('energy_point_rule')))
                for key ,values in months.items():
                    tnc_pt=0
                    tnc_pt_float=0
                    for dd in data:
                            
                        if dd['energy_point_rule']==rule.get('energy_point_rule') and dd['user']==name.get('user_id'):
                         
                          
                            tnc_pt+= dd.get(key+"achieved") if dd.get(key+"achieved") else 0
                            tnc_pt_float = "{:.2f}".format(tnc_pt)
                            # tnc_sc_pt+=dd.get(key+"score") if dd.get(key+"score") else 0
                            # tnc_pt_sc_float = "{:.2f}".format(tnc_sc_pt)
                            final_tnc.append(tnc_pt_float)
                            rule_present.add(rule.get('energy_point_rule'))
                if final_tnc:
                    finaldata.append({'name':rule.get('energy_point_rule'), 'values': final_tnc})
             
             
                    tnc_chart= {
                                "data": {
                                    'labels': lable,
                                    'datasets': finaldata,
                                },
                            }
                    tnc_chart["type"] = "bar"
                        
    

    if filters.get("periodicity")=="Half Yearly": 
        data=getData(filters)
        # print(data)
        # rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)
        emp=frappe.db.sql("""select e.name, e.user_id from `tabEmployee` as e right outer join `tabPerformance Target Variable` as p ON p.employee=e.employee where p.disabled=0;""",as_dict=True)        
        months=getHalfYearly(filters)
        finaldata=[]
        lable=[]
        for name in emp:
            final_tnc=[]
            lable.append(name.get('name'))
            rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent AND p.employee='{}';""".format(name.get('name')), as_dict=True)
            for rule in rules:
                rule_present=set()
        
             
                # print("Employee= {} Rule= {}".format(rule.get('employee'),rule.get('energy_point_rule')))
                for key ,values in months.items():
                    tnc_pt=0
                    tnc_pt_float=0
                    for dd in data:
                            
                        if dd['energy_point_rule']==rule.get('energy_point_rule') and dd['user']==name.get('user_id'):
                           
                          
                            tnc_pt+= dd.get(key+"achieved") if dd.get(key+"achieved") else 0
                            tnc_pt_float = "{:.2f}".format(tnc_pt)
                            # tnc_sc_pt+=dd.get(key+"score") if dd.get(key+"score") else 0
                            # tnc_pt_sc_float = "{:.2f}".format(tnc_sc_pt)
                            final_tnc.append(tnc_pt_float)
                            rule_present.add(rule.get('energy_point_rule'))
            if final_tnc:
                finaldata.append({'name':rule.get('energy_point_rule'), 'values': final_tnc})
            
            
                tnc_chart= {
                            "data": {
                                'labels': lable,
                                'datasets': finaldata,
                                
                            },
                        }
                tnc_chart["type"] = "bar"
                
                print("caaaaa",tnc_chart)
  

    if filters.get("periodicity")=="Yearly": 
        data=getData(filters)
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",data)
        # rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent ORDER BY p.employee ASC;""", as_dict=True)
        emp=frappe.db.sql("""select e.name, e.user_id from `tabEmployee` as e right outer join `tabPerformance Target Variable` as p ON p.employee=e.employee where p.disabled=0;""",as_dict=True)
      
        years=getYears(filters)
        finaldata=[]

        for name in emp:

           
            rules=frappe.db.sql("""select DISTINCT i.energy_point_rule,p.employee from `tabPerformance Target Variable Items` as i,`tabPerformance Target Variable` as p WHERE p.name=i.parent AND p.employee='{}';""".format(name.get('name')), as_dict=True)
            for rule in rules:
                rule_present=set()
                tnc_pt=0
                
                for x in years:
                    lable=[] 
                    final_tnc=[]
                    tnc_pt_float=0
                    for dd in data:
                        
                        if dd['energy_point_rule']==rule.get('energy_point_rule') and dd['user']==name.get('user_id'): 
                            lable.append(x.get('from_date')+"-"+x.get('to_date'))  
                            # tnc_pt+= dd.get(x.get('from_date')+"-"+x.get('to_date')+"achieved") if dd.get(x.get('from_date')+"-"+x.get('to_date')+"achieved") else 0
                            # tnc_pt_float = "{:.2f}".format(tnc_pt)
                            tnc_sc_pt+=dd.get(key+"score") if dd.get(key+"score") else 0
                            # tnc_pt_sc_float = "{:.2f}".format(tnc_sc_pt)
                            final_tnc.append(tnc_pt)
                            rule_present.add(rule.get('energy_point_rule'))
                
                            if final_tnc:
                                
                                finaldata.append({'name':rule.get('energy_point_rule'), 'values': final_tnc})
                        
                        
                                tnc_chart.update({
                                            "data": {
                                                'labels': lable,
                                                'datasets': finaldata,
                                            },
                                            'type':'bar'
                                           
                                        })
                                # tnc_chart["type"] = "bar"
             
                    print("caaaaa",tnc_chart)
                    

        
    return tnc_chart
    

def get_bonus_data(filters,fiscal_year=None,employee_name=None,company_name=None,periodicity=None):
      ls=[]
      print(fiscal_year,employee_name,company_name,periodicity)
      if periodicity=='Monthly':
        ls=get_monthly_data(filters,fiscal_year=fiscal_year,employee_name=employee_name,company_name=company_name)
      
      if periodicity=='Quarterly':
           ls=get_Data_Quarterly(filters,fiscal_year=fiscal_year,employee_name=employee_name,company_name=company_name)

      if periodicity=='Half Yearly':
          ls =get_data_halfyearly(filters,fiscal_year=fiscal_year,employee_name=employee_name,company_name=company_name)
      
      if periodicity=='Yearly':
          ls =get_data_yearly(filters,fiscal_year=fiscal_year,employee_name=employee_name,company_name=company_name)
          print(ls)
      return ls




def chart_condition(filters):
    conditions=""
    if filters.get('emp'):
        conditions +=" AND e.name='%s'" % filters.get('emp') 
    return conditions