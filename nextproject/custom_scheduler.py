# import frappe
# from frappe.utils.data import flt, getdate,get_time
# import processscheduler as ps
# # from processscheduler import Shift
# from datetime import timedelta, datetime
# # %config InlineBackend.figure_format = ['svg']
# import matplotlib.pyplot as plt



# @frappe.whitelist()
# def project_scheduler(values,project):
#     if project:
#         values=eval(values)
#         #problem defination
#         datetime_obj = datetime.strptime(values.get("plan_start_date"), '%Y-%m-%d %H:%M:%S')
#         new_date = datetime_obj + timedelta(days=int(values.get("planning_days")))
#         print("$$$$$$$$$$$$$$$$",new_date)
#         horizon=int(values.get("planning_days")) *24
#         problem = ps.SchedulingProblem(str(project),delta_time=timedelta(hours=1),
#                                     start_time=datetime_obj)


#         #Plan Objectives
#         if values.get("plan_objective")=="Flowtime":
#             problem.add_objective_flowtime(weight=1)
#         if values.get("plan_objective")=="Makespan":
#             problem.add_objective_makespan(weight=1)
#         if values.get("plan_objective")=="Priorities":
#             problem.add_objective_priorities(weight=1)
#         if values.get("plan_objective")=="Start Earliest":
#             problem.add_objective_start_earliest(weight=1)
#         if values.get("plan_objective")=="Start Latest":
#             problem.add_objective_start_latest(weight=1)


#         #Task Defination
#         task=frappe.db.get_all("Task",{"project":project,"status":["not in",["Completed","Cancelled","Hold"]]},["name"])
#         d={}
#         for j in task:
#             doc=frappe.db.get_value("Task",{"name":j.get("name"),"duration_type":"Fixed Duration","is_group":0},["name"])
#             pri={"Low":1,"Medium":2,"High":3,"Urgent":4}
#             if doc:
#                 taskdoc=frappe.get_doc("Task",doc)
#                 a=j.get("name")
#                 d.update({a:ps.FixedDurationTask(str(j.get("name")), duration=int(taskdoc.expected_time),priority=pri.get(str(taskdoc.priority)),optional=taskdoc.optional)})

#             else:
#                 taskdoc=frappe.get_doc("Task",j.name)
#                 a=j.get("name")
#                 d.update({a:ps.ZeroDurationTask(str(j.get("name")),optional=taskdoc.optional)})


#         #Task Constarints
#         hr=frappe.get_doc("HR Settings")
#         for j in task:
#             task1=frappe.get_doc("Task",j.name)
#             if task1.planning_constraint =="Fixed End On":
#                 data=getdate(task1.fixed_end_date)-getdate(values.get("plan_start_date"))
#                 duration=data.days*24
#                 if d.get(str(task1.name)):
#                     ps.TaskEndAt(d.get(str(task1.name)),duration,optional=task1.optional)
#                 else:
#                     task2=ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)
#                     ps.TaskEndAt(task2,duration,optional=task1.optional)



#             if task1.planning_constraint =="Starts After":
#                 if d.get(str(task1.name)):
#                     pass
#                 else:
#                     d.update({task1.name:ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)})
#                 dot=frappe.get_doc("Task",task1.start_after_task)
#                 if d.get(str(task1.start_after_task)):
#                     pass
#                 else:
#                     d.update({task1.start_after_task:ps.FixedDurationTask(str(task1.start_after_task), duration=int(dot.expected_time),priority=pri.get(str(task1.priority)),optional=dot.optional)})
#                 ps.TaskPrecedence(d.get(str(task1.start_after_task)),d.get(str(task1.name)),offset=task1.offset,kind=task1.precedence_type,optional=task1.optional)



#             if task1.planning_constraint =="Fixed Start After" and task1.precedence_type=="strict":
#                 if d.get(str(task1.name)):
#                     pass
#                 else:
#                     d.update({task1.name:ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)})
#                 data=getdate(task1.fixed_start_date)-getdate(values.get("plan_start_date"))
#                 duration=data.days*24
#                 print("666666666666666",duration)
#                 ps.TaskStartAfterStrict(d.get(str(task1.name)),duration,optional=task1.optional)


#             if task1.planning_constraint =="Fixed Start After" and task1.precedence_type=="lax":
#                 print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
#                 if d.get(str(task1.name)):
#                     pass
#                 else:
#                     d.update({task1.name:ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)})
#                 data=getdate(task1.fixed_start_date)-getdate(values.get("plan_start_date"))
#                 duration=data.days*24
#                 print("666666666666666",duration)
#                 ps.TaskStartAfterLax(d.get(str(task1.name)),duration,optional=task1.optional)


#             if task1.planning_constraint =="Ends With":
#                 if d.get(str(task1.name)):
#                     pass
#                 else:
#                     d.update({task1.name:ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)})
#                 dot=frappe.get_doc("Task",task1.ends_with_task)
#                 if d.get(str(task1.ends_with_task)):
#                     pass
#                 else:
#                     d.update({task1.ends_with_task:ps.FixedDurationTask(str(task1.ends_with_task), duration=int(dot.expected_time),priority=pri.get(str(dot.priority)),optional=dot.optional)})
#                 ps.TasksEndSynced(d.get(str(task1.name)),d.get(str(task1.ends_with_task)),optional=task1.optional)


#             if task1.planning_constraint =="Starts With":
#                 if d.get(str(task1.name)):
#                     pass
#                 else:
#                     d.update({task1.name:ps.FixedDurationTask(str(task1.name), duration=int(task1.expected_time),priority=pri.get(str(task1.priority)),optional=task1.optional)})
#                 dot=frappe.get_doc("Task",task1.start_with_task)
#                 if d.get(str(task1.start_with_task)):
#                     pass
#                 else:
#                     d.update({task1.start_with_task:ps.FixedDurationTask(str(task1.start_with_task), duration=int(dot.expected_time),priority=pri.get(str(dot.priority)),optional=dot.optional)})
#                 ps.TasksStartSynced(d.get(str(task1.name)),d.get(str(task1.start_with_task)),optional=task1.optional)

#         #Resource Defination
        
#         z={}
#         for j in task:
#             doc=frappe.get_doc("Project",project)
#             eg=frappe.get_doc("Employee Group",doc.employee_group)
#             ts=frappe.get_doc("Task",j.get("name"))
#             employee=[]
#             for i in eg.employee_list:
#                 emp=frappe.get_doc("Employee",i.get("employee"))
#                 if emp.task_type==ts.type:
#                     cost=frappe.db.get_value("Activity Cost",{"employee":emp.name,"activity_type":doc.activity_type},"costing_rate")
#                     if not z.get(str(i.employee)):
#                         z.update({emp.name:ps.Worker(i.employee, productivity=int(emp.productivity_factor), cost=ps.ConstantCostPerPeriod(int(cost)))})
#                         # if emp.default_shift:
#                         #     shift=frappe.db.get_all("Shift Type",{"name":emp.default_shift},["start_time","end_time"])
#                         #     t1 = get_time(shift[0].get("start_time"))
#                         #     t2 = get_time(shift[0].get("end_time"))
#                         #     z.get(str(i.employee)).add_shifts(Shift(t1,t2))
#                         # print(z.get(str(i.employee)).get_unavailable_ranges(problem))
#                     employee.append(z.get(str(i.employee)))
#             if values.get("plan_objective")=="Resource Cost":
#                 problem.add_objective_resource_cost(employee, weight=1)
#             d.get(ts.name).add_required_resource(ps.SelectWorkers(employee,
#                                     nb_workers_to_select=1,
#                                     kind='exact'))
#             # print("*************",employee,z)
            


#         #Plan Selection indicator
#         if values.get("plan_select_indicator")=="Resource Utilization":
#             for k in employee:
#                 problem.add_indicator_resource_utilization(k)
#         if values.get("plan_select_indicator")=="Resource Cost":
#             problem.add_indicator_resource_cost(employee)
#         if values.get("plan_select_indicator")=="No of Tasks Assigned":
#             for k in employee:
#                 problem.add_indicator_number_tasks_assigned(k)
#         if values.get("plan_objective")=="Resource Utilization":
#             for k in employee:
#                 problem.add_objective_resource_utilization(k, weight=1)


#         #Resource constraint
#         #resource unavailable

#         doc=frappe.get_doc("Project",project)
#         eg=frappe.get_doc("Employee Group",doc.employee_group)
#         for i in eg.employee_list:
#             interval=[]
#             emp=frappe.get_doc("Employee",i.get("employee"))
#             datetime_obj = datetime.strptime(values.get("plan_start_date"), '%Y-%m-%d %H:%M:%S')
#             new_date = datetime_obj + timedelta(days=int(values.get("planning_days")))
#             date_list = []
#             # iterate over a range of dates and append each date to the list
#             for n in range(int ((new_date - datetime_obj).days)+1):
#                 date_list.append((datetime_obj + timedelta(n)).strftime('%Y-%m-%d'))
#             # for c in date_list:
#             doc=frappe.db.sql("""select shift_type from `tabShift Assignment` where employee='{0}' and end_date >= '{1}' and status="Active" and docstatus=1 or 
#                         employee='{0}'  and  status="Active" and end_date is NULL and docstatus=1""".format(emp.name,new_date),as_dict=1)
#             # print("&&&&&&&&&&&&&&&&&&&444444",doc)

#             if doc:
#                 shift=frappe.db.get_all("Shift Type",{"name":doc[0].get("shift_type")},["start_time","end_time"])
#                 t1 = get_time(shift[0].get("start_time"))
#                 t2 = get_time(shift[0].get("end_time"))
#                 if t2.hour>t1.hour:
#                     for n in range(1,int(values.get("planning_days"))+1):
#                         a=(0+(24*(n-1)),t1.hour+(24*(n-1)))
#                         b=(t2.hour+(24*(n-1)), 24+(24*(n-1)))
#                         interval.append(a)
#                         interval.append(b)
#                 if t1.hour>t2.hour:
#                     for n in range(1,int(values.get("planning_days"))+1):
#                         a=(0+(24*(n-1)),t1.hour+(24*(n-1)))
#                         b=(t2.hour+(24*(n-1)), t1.hour+(24*(n-1)))
#                         interval.append(a)
#                         interval.append(b)
#                 if t1.hour==0:
#                     for n in range(1,int(values.get("planning_days"))+1):
#                         b=(t2.hour+(24*(n-1)), 24+(24*(n-1)))
#                         interval.append(b)
#                 if t2.hour==0:
#                     for n in range(1,int(values.get("planning_days"))+1):
#                         b=(t2.hour+(24*(n-1)), t1.hour+(24*(n-1)))
#                         interval.append(b)

#             else:
#                 if emp.default_shift:
#                     shift=frappe.db.get_all("Shift Type",{"name":emp.default_shift},["start_time","end_time"])
#                     t1 = get_time(shift[0].get("start_time"))
#                     t2 = get_time(shift[0].get("end_time"))
#                     if t2.hour>t1.hour:
#                         for n in range(1,int(values.get("planning_days"))+1):
#                             a=(0+(24*(n-1)),t1.hour+(24*(n-1)))
#                             b=(t2.hour+(24*(n-1)), 24+(24*(n-1)))
#                             interval.append(a)
#                             interval.append(b)
#                     if t1.hour>t2.hour:
#                         for n in range(1,int(values.get("planning_days"))+1):
#                             a=(0+(24*(n-1)),t1.hour+(24*(n-1)))
#                             b=(t2.hour+(24*(n-1)), t1.hour+(24*(n-1)))
#                             interval.append(a)
#                             interval.append(b)
#                     if t1.hour==0:
#                         for n in range(1,int(values.get("planning_days"))+1):
#                             b=(t2.hour+(24*(n-1)), 24+(24*(n-1)))
#                             interval.append(b)
#                     if t2.hour==0:
#                         for n in range(1,int(values.get("planning_days"))+1):
#                             b=(t2.hour+(24*(n-1)), t1.hour+(24*(n-1)))
#                             interval.append(b)

            
            
#             hr=frappe.get_doc("HR Settings")
#             doc=frappe.get_doc("Project",project)
#             # print("&&&&&&&&&&&&&&&&&33333333",z.get(str(i.name)),"$$$$$$$$$$$$$$$",z,"&&&&&&&&&&&&&",i.name)
#             if z.get(str(i.get("employee"))):
#                 # print("&&&&&&&&&&&&&&&&&",z.get(str(i.name)))
#                 hlist=frappe.db.get_all("Holiday",{"holiday_date":[">=",getdate(values.get("plan_start_date"))],
#                                                    "parent":emp.holiday_list,},"holiday_date")
#                 for j in hlist:
#                     data=getdate(j.holiday_date)-getdate(values.get("plan_start_date"))
#                     duration=data.days*24
#                     a=(duration,duration+24)
#                     interval.append(a)
#                 plist=frappe.db.get_all("Holiday",{"holiday_date":[">=",getdate(values.get("plan_start_date"))],
#                                                    "parent":doc.holiday_list},"holiday_date")
#                 for k in plist:
#                     data=getdate(k.holiday_date)-getdate(values.get("plan_start_date"))
#                     duration=data.days*24
#                     a=(duration,duration+24)
#                     interval.append(a)
#                 rlist=frappe.db.get_all("Resource Allocation",{"date":[">=",getdate(values.get("plan_start_date"))]},["date"])
#                 for m in rlist:
#                     data=getdate(m.date)-getdate(values.get("plan_start_date"))
#                     duration=data.days*24
#                     a=(duration,duration+int(m.allocation))
#                     interval.append(a)
#                 lalist=frappe.db.get_all("Leave Application",{"from_date":[">=",getdate(values.get("plan_start_date"))],"half_day":0},"name")
#                 for n in lalist:
#                     la=frappe.get_doc("Leave Application",n.name)
#                     data=getdate(la.to_date)-getdate(values.get("plan_start_date"))+1
#                     # data.days=data.days+1
#                     daten=getdate(la.from_date)-getdate(values.get("plan_start_date"))
#                     duration=daten.days*24

#                     a=(duration,24*data.days)
#                     interval.append(a)
#                 alist=frappe.db.get_all("Leave Application",{"from_date":[">=",getdate(values.get("plan_start_date"))],"half_day":1},"name")
#                 for n in alist:
#                     la=frappe.get_doc("Leave Application",n.name)
#                     daten=getdate(la.from_date)-getdate(values.get("plan_start_date"))
#                     duration=daten.days*24
#                     a=(duration,duration+(int(hr.standard_working_hours)/2))
#                     interval.append(a)
#             print("&&7777777777777777",interval)
#             # interval=[]
#             ps.ResourceUnavailable(z.get(i.get("employee")), interval, optional=False)

#         #Problem Solver
#         solver = ps.SchedulingSolver(problem,optimizer="optimize")
#         solution = solver.solve()
#         # solver.print_solution()
#         # solver.print_assertions()
#         # print("&&&&&&&&&&&&&&&&",solver.print_statistics())
#         # frappe.msgprint("{0}".format(solver.print_assertions()))
        
#         if solution:
#             solution.render_gantt_plotly()

#         # ps.solution.SchedulingSolution(problem)
#         #Problem Solution
#         # ps.SchedulingSolution()
#         # solver.resourcesolution()
#         print(solution)
    

