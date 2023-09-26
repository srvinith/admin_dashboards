from django.shortcuts import render
import pyrebase
from django.http import JsonResponse
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import keys
import pytz
import datetime

import calendar

Config = {
    "apiKey": "AIzaSyCCTeiCYTB_npcWKKxl-Oj0StQLTmaFOaE",
    "authDomain": "marketing-data-d141d.firebaseapp.com",
    "databaseURL": "https://marketing-data-d141d-default-rtdb.firebaseio.com/",
    "storageBucket": "marketing-data-d141d.appspot.com",
}

firebase = pyrebase.initialize_app(Config)
db = firebase.database()

my_app_id = '622623732603375'
my_app_secret = '0137ae3314de2038f8984483045eeae4'
my_access_token = keys.facebook_acces_token
add_acc_id = "act_407900737581426"
FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

# def get_iso_week_numbers(year, month):
#     # Create the first day of the month
#     first_day = datetime.date(year, month, 1)

#     # Find the ISO week number for the first day
#     first_week_number = first_day.isocalendar()[1]

#     # Initialize a list to store the week numbers
#     iso_week_numbers = [first_week_number]

#     # Calculate ISO week numbers for the remaining days of the month
#     last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])
#     current_day = first_day + datetime.timedelta(days=1)
    
#     while current_day <= last_day:
#         iso_week_number = current_day.isocalendar()[1]
#         if iso_week_number != iso_week_numbers[-1]:
#             iso_week_numbers.append(iso_week_number)
#         current_day += datetime.timedelta(days=1)

#     return iso_week_numbers

def get_month_dates(year, month):
    # Find the number of days in the given month
    num_days = calendar.monthrange(year, month)[1]

    # Create a list to store the dates
    month_dates = []

    # Generate all the dates in the month
    for day in range(1, num_days + 1):
        date = datetime.date(year, month, day)
        formatted_date = date.strftime("%d-%m-%Y")  # Format as "day-month-year"
        month_dates.append(formatted_date)

    return month_dates  

# def get_month_dates_with_time(year, month):
#     # Find the number of days in the given month
#     num_days = calendar.monthrange(year, month)[1]

#     # Create a list to store the dates with time
#     month_dates_with_time = []

#     # Generate all the dates in the month with time
#     for day in range(1, num_days + 1):
#         date = datetime.date(year, month, day)
#         formatted_date_with_time = date.strftime("%d-%m-%Y_%H:%M")  # Format as "day-month-year_hour:minute"
#         month_dates_with_time.append(formatted_date_with_time)

#     return month_dates_with_time

def get_absentees():
    fingerPrintCount, absentCount, proxyCount = 0, 0, 0
    # fp = db.child("fingerPrint").get().val()
    # va = db.child("virtualAttendance").get().val()
    staffDB = db.child("staff").get().val()
    fpDB = db.child("fingerPrint").get().val()
    pxDB = db.child("proxy_attendance").get().val()
    dtNow = datetime.datetime.now()
    todaysDate = dtNow.strftime("%Y-%m-%d")
    thisDa = dtNow.strftime("%d")
    currentyear = dtNow.strftime("%Y")
    currentmonth = dtNow.strftime("%m")
    for staff in staffDB:
        if staffDB[staff]['department'] != "ADMIN":
            try:
                fpDB[staff][todaysDate]
                fingerPrintCount += 1
            except:
                try:
                    pxDB[staff][todaysDate]['Check-in']
                    proxyCount += 1
                except:
                    absentCount += 1

    presentCount = fingerPrintCount + proxyCount
    return presentCount, absentCount, proxyCount
    
def home(request):
    try:

        dtNow = datetime.datetime.now()
        curr_day = int(dtNow.strftime("%d"))
        # time= dtNow.strftime("%I:%M:%S %p")
        # curr_mon_year = str(dtNow.strftime("%Y-%m"))
        curr_year = dtNow.year
        current_month = dtNow.month
        current_month_name = calendar.month_name[dtNow.month]
        curr_month = str(dtNow.month).zfill(2)
        curr_date=dtNow.strftime("%d-%m-%Y")
        year = dtNow.isocalendar()[0]
        curr_week = dtNow.isocalendar()[1]
       
        # curr_monthname=dtNow.strftime("%B")

        allDataBase = db.get().val()
        PRpoints = allDataBase["PRPoints"]
    
        # print("prpoints",PRpoints)
        month_dates=get_month_dates(curr_year,current_month) 
    

        #Sales perfomance table and visit arranged table
        user_data = []

        
        try:
            for uid in PRpoints:   
                name = PRpoints[uid].get("name")
                if uid in allDataBase["staff"]:
                    mobilenum = allDataBase["staff"][uid].get("mobile", None)
                else:
                    # If uid is not found in staff data, set mobilenum to None
                    mobilenum = None

                print("mobile",mobilenum)   

                if name:
                    achieved_points = 0
                    sales=0
                    visits_arranged=0
                    visiteds=0
                    try:
                        for date in month_dates:
                            target_point = PRpoints[uid].get(str(curr_year), {}).get(str(curr_month), {}).get(str("total"), {}).get('total_monthly_points',0)
                            achieved_point = PRpoints[uid].get(str(curr_year), {}).get(str(curr_month), {}).get(date, {}).get('points')
                            sale=PRpoints[uid].get(str(curr_year), {}).get(str(curr_month), {}).get(date, {}).get('sales')
                            visit_arranged=PRpoints[uid].get(str(curr_year), {}).get(str(curr_month), {}).get(date, {}).get('visit_arranged')
                            visited=PRpoints[uid].get(str(curr_year), {}).get(str(curr_month), {}).get(date, {}).get('visited')
                            if achieved_point is not None:
                                achieved_points += achieved_point
                            if sale is not None:
                                sales += sale
                            if visit_arranged is not None:
                                visits_arranged += visit_arranged
                            if visited is not None:
                                visiteds += visited            
                    except Exception as e:
                        print("An error:", str(e))
                    user_data.append({"name": name,
                                       "achieved_points": achieved_points,
                                       "sales":sales,
                                       "visits_arranged":visits_arranged,
                                       "visited":visiteds,
                                       "target_points":target_point,
                                       "mobilenumber":mobilenum
                                       })
        except Exception as e:
            print("An error occurred:", str(e))
        # else:
        #     # print("user_data:", user_data)
        
        #Today overall calls

        try:
            overall_calls=0
            for uid in PRpoints:
                calls=PRpoints[uid].get(str(curr_year),{}).get(str(curr_month),{}).get(str(curr_date),{}).get('calls')
                if calls is not None:
                    overall_calls += calls

            # print("overall_calls",overall_calls)
        except Exception as e:
            print("error",str(e))

        # Total customers
        # try:
        #     customer = allDataBase["customer"]
        #     num_customers = len(customer)
        #     print("Total number of customers:", num_customers)

        # except KeyError:
        #     print("The 'customer' key does not exist in the database.")





         
         
        # user_data_achieved = sorted(user_data, key=lambda user: user['achieved_points'], reverse=True)

        # # Sort user_data by visits in descending order
        # user_data_visits = sorted(user_data, key=lambda user: user['visits_arranged'], reverse=True) 

        presentCount, absentCount, proxyCount = get_absentees() 
        # print("absentees",presentCount, absentCount, proxyCount)
        
        context={
            "user_data":user_data,
            # "user_data_visits":user_data_visits,
            "overall_calls":overall_calls,
            "presentCount":presentCount,
            "absentCount":absentCount,
            "proxyCount":proxyCount,
            "curr_year":curr_year,
            "curr_week":curr_week,
            "curr_date":curr_date,
            "curr_month":current_month_name,
            # "num_customers":num_customers
        }
    
        return render(request,'home.html',context)
    except:
        context={
            "data":True
        }
        return render(request,'home.html',context) 


def get_data(request):
    asiaTime = pytz.timezone("Asia/Kolkata")
    asiaTime = datetime.datetime.now(asiaTime)
    t1 =  asiaTime.strftime("%I:%M:%S %p")
    t2 = asiaTime.strftime("%Y-%m-%d %H:%M:%S")
    data={
        "time":t1,
        "time2":t2,
    }
    # print("data",data)
    return JsonResponse(data)


def flead(request):
    ad_account = AdAccount(add_acc_id)
    fields = [
        AdsInsights.Field.ad_name,
        AdsInsights.Field.actions,
    ]
    params = {
        'level': 'ad',
        'date_preset': 'today',
        'action_breakdowns': ['action_type'],
        'filtering': [
            {
                'field': 'ad.effective_status',
                'operator': 'IN',
                'value': ['ACTIVE']
            },
        ],
    }
    insights = ad_account.get_insights(fields=fields, params=params)
    ad_data = []
    total_leads = 0
    for insight in insights:
        lead_count = 0
        if 'actions' in insight:
            for action in insight['actions']:
                if action['action_type'] == 'lead':
                    lead_count = int(action['value'])
                    break
        ad_data.append({
            'ad_name': insight['ad_name'],
            'lead_count': lead_count,
        })
        total_leads += lead_count
    adnamelist=[]
    leadslist=[]
    for a in ad_data:
        adnamelist.append(a['ad_name'])
        leadslist.append(a['lead_count'])
    totaladleads=sum(leadslist)
    faceboodklead=zip(adnamelist,leadslist)
    faceboodklead = []
    for name, lead in zip(adnamelist, leadslist):
        faceboodklead.append({"ad_name": name, "lead_count": lead})
    data={
        "totaladleads":totaladleads,
        "faceboodklead":faceboodklead
    }
    # print("data",data)
    return JsonResponse(data)           

#  def home(request):
#     user_data_dict = {}
#     user_data_list = []
#     current_datetime = datetime.datetime.now()
#     current_month = current_datetime.month
#     current_year = current_datetime.year
#     overall_total_calls = 0
#     alphaamount = 0  # Default value
#     betaamount = 0  # Default value
#     deltaamount = 0 
#     total_salary_expense = 0
#     total_equipment_expense = 0
#     total_visit_expense = 0
#     total_ebbills_expense = 0
#     try:
        
#         # Retrieve data from the Firebase database (inside the "pr" key)
#         all_user_data = db.child("pr").get()

#         all_team = db.child("allteam").get().val()
     
 

#         alphaamount=all_team["team1"]["amount"]
#         print("alphaamount",alphaamount)
#         #alphasales=[all_team]["team1"]["sales"]
#         betaamount=all_team["team2"]["amount"]
#         #betasales=[all_team]["team2"]["sales"]
#         # charlieamount=dashboardDB["allteam"]["team3"]["amount"]
#         # charliesales=dashboardDB["allteam"]["team3"]["sales"]
#         deltaamount=all_team["team3"]["amount"]
#         #deltasales=[all_team]["team3"]["sales"]
#         #salestotal=int(alphasales)+int(betasales)+int(deltasales)
#         #prcharttotal=int(alphaamount)+int(betaamount)+int(deltaamount)
        
        


#             # Convert the Firebase data to a Python dictionary
#         pr_data = all_user_data.val()
       
        
        
#         # Initialize a list to store mobile numbers and their monthly point
#           # Initialize overall total calls

#         current_datetime = datetime.datetime.now()
#         current_year = current_datetime.year
#         current_month = current_datetime.month
#             # Get the current date

#         # Calculate ISO week numbers for the current year and month using the new function
#         current_week = get_iso_week_numbers(current_year, current_month)  

#         month_date = get_month_dates(current_year, current_month)  

#         month_datetime = get_month_dates_with_time(current_year, current_month) 

#         finance = db.child("FinancialAnalyzing").get().val()
       
        
#         for date_with_time in month_datetime:
#             # Split the date with time to separate date and time parts
#             date_parts = date_with_time.split("_")
#             date_part = date_parts[0]  # Get the date part in the format 'dd-mm-yyyy'

#             # Parse the date part into a datetime object
#             for date_with_time in month_datetime:
#                 formatted_date = datetime.datetime.strptime(date_with_time, "%d-%m-%Y_%H:%M").date()

#                 # Check if the date exists in the finance data
#                 current_month_padded = str(current_month).zfill(2)
#                 current_year_str = str(current_year)

#                 if current_year_str in finance['expense']:
#                     if current_month_padded in finance['expense'][current_year_str]:
#                         if date_with_time in finance['expense'][current_year_str][current_month_padded]:
#                             expenses_data = finance['expense'][current_year_str][current_month_padded][date_with_time]
                         

#                             for hour, expense_item in expenses_data.items():
#                                 purchasedfor = expense_item['purchaseFor']
#                                 amount = expense_item['amount']

#                                 # Check if purchasedfor matches one of the specific categories
#                                 if purchasedfor == 'salary':
#                                     total_salary_expense += amount
#                                 elif purchasedfor == 'Equipment':
#                                     total_equipment_expense += amount
#                                 elif purchasedfor == 'visit_expense':
#                                     total_visit_expense += amount
#                                 elif purchasedfor == 'ebbills':
#                                     total_ebbills_expense += amount
#                         else:
#                             pass
#                             # print(f"No expenses found for date with time: {date_with_time}")
#                     else:
#                         pass
#                         # print(f"No expenses found for month {current_month_padded}")
#                 else:
#                     pass
#                     # print(f"No expenses found for year {current_year}")


       

#         # Initialize variables to keep track of totals for each category
        


       

# #             # Check if the date with time exists in the finance data
# #         current_month_padded = str(current_month).zfill(2)    
# #         print("st",current_year,current_month_padded)
# #         # List of months to iterate through
# #         months_to_check = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# #         for month_padded in months_to_check:
# #             print("Checking for month:", month_padded)
# #             print("current_year",current_year)
# #             print("fin",finance['expense'])

# #             if current_year in finance['expense']:
# #                 print("first")
# #                 # Remove the space when checking for the month
# #                 if month_padded.strip() in finance['expense'][current_year]:
# #                     print(f"Expenses found for year {current_year} and month {month_padded}")
# #                     expenses_for_current_month = finance['expense'][current_year][month_padded.strip()]
                    
# #                     for date_with_time, expenses_data in expenses_for_current_month.items():
# #                         print("Date with Time:", date_with_time)
# #                         print("Expenses Data:", expenses_data)
# #                         print("Entering..")
# #                 else:
# #                     expenses_for_current_month = {}  # Initialize as an empty dictionary
# #                     print("No expenses found for the current year and month:", month_padded)
# #             else:
# #                 expenses_for_current_month = {}  # Initialize as an empty dictionary
# #                 print("No expenses found for the current year:", current_year)
# #   # Process expenses here

# #                 # Iterate through the expenses for the current date
# #         for expense_data in expenses_for_current_month:
# #             purchasedfor = expense_data['purchasedFor']

# #             amount = expense_data['amount']

# #             # Check if purchasedfor matches one of the specific categories
# #             if purchasedfor == 'salary':
# #                 total_salary_expense += amount
# #             elif purchasedfor == 'Equipment':
# #                 total_equipment_expense += amount
# #             elif purchasedfor == 'visit_expense':
# #                 total_visit_expense += amount
# #             elif purchasedfor == 'ebbills':
# #                 total_ebbills_expense += amount

#                     # Now, you have the total expenses for each specific category
      


#         # Extract data for each mobile number
        

#         # Extract data for each mobile number
#         for mobile_number, data in pr_data.items():
#             # Initialize user data
#             user_data = {
#                 'mobile_number': mobile_number,
#                 'name': data.get('name', ''),
#                 'monthly_points': [],
#                 'total_achieved_points': 0,  # Total achieved points for the user
#                 'total_target_points': 0,
#                 'monthly_sales': 0,
#                 'monthly_visits': 0,  # Total target points for the user
#             }

#             # Extract monthly points if available
#             pr_points = data.get('prpoints', {})
      
            
#             for year, year_data in pr_points.items():
#                 achieved_points = 0
#                 target_points = 0
#                 total_sales = 0
#                 total_visits = 0
#                 user_calls = 0  # Initialize user-specific calls

#                 for year, year_data in pr_points.items():
#                     achieved_points = 0
#                     target_points = 0
#                     total_sales = 0
#                     total_visits = 0
#                     overall_total_calls = 0

#                     for week in current_week:
#                         if str(week) in year_data:
#                             for date in month_date:
#                                 # Check if the date exists in the week's data
#                                 if date in year_data[str(week)]:
#                                     week_achieved_point = year_data[str(week)][date]['achieved_points']
          
#                                     week_target_point = year_data[str(week)][date]['target_points']
#                                     week_sales = year_data[str(week)][date]['sales']
#                                     week_visit = year_data[str(week)][date]['visit']

#                                     year_data[str(week)]['weeklypoints']['achieved_points'] += week_achieved_point
#                                     year_data[str(week)]['weeklypoints']['target_points'] += week_target_point
#                                     year_data[str(week)]['weeklypoints']['total_sales'] += week_sales
#                                     year_data[str(week)]['weeklypoints']['total_visit'] += week_visit

#                                     achieved_point = year_data[str(week)]['weeklypoints']['achieved_points']
#                                     target_point = year_data[str(week)]['weeklypoints']['target_points']
#                                     total_sale = year_data[str(week)]['weeklypoints']['total_sales']
#                                     total_visit = year_data[str(week)]['weeklypoints']['total_visit']

#                                     # Add the week's achieved points to the 'weeklypoints' dictionary

  

                            

#                                     # Check if the current date exists in the week's data
#                                     formatted_date = datetime.datetime.strptime(date, "%d-%m-%Y")
#                                     formatted_date = formatted_date.date()  # Convert to date object
#                                     if formatted_date in year_data[str(week)]:
#                                         user_calls = year_data[str(week)][formatted_date]['calls']
#                                         overall_total_calls += user_calls

#                                     achieved_points += achieved_point
#                                     target_points += target_point
#                                     total_sales += total_sale
#                                     total_visits += total_visit

#                     month_entry = {
#                         'year': year,
#                         'achieved_points': achieved_points,
#                         'target_points': target_points,
#                         'total_sales': total_sales,
#                         'total_visits': total_visits
#                     }

#                     # Update user's total achieved and target points
#                     user_data['total_achieved_points'] += achieved_points
#                     user_data['total_target_points'] += target_points
#                     user_data['monthly_sales'] += total_sales
#                     user_data['monthly_visits'] += total_visits

#                     user_data['monthly_points'].append(month_entry)

#                 # Store user data in the dictionary
#                 user_data_dict[mobile_number] = user_data

#                 # Convert user data dictionary into a list
#                 user_data_list = list(user_data_dict.values())

#     except Exception as e:
#         print(e)
#         # Handle exceptions here and return an empty list if an error occurs
#         # return render(request, 'home.html', {'user_data_list': user_data_list})
#     context = {
#         'user_data_list': user_data_list,  # Replace with your actual user data
#         'current_month': calendar.month_name[current_month],  # Pass the month name
#         'overall_total_calls': overall_total_calls, 
#         'alphaamount':alphaamount,
#         'betaamount':betaamount,
#         'deltaamount':deltaamount,
#         'total_salary_expense':total_salary_expense,
#         'total_visit_expense':total_visit_expense,
#         'total_equipment_expense':total_equipment_expense,
#         'total_ebbills_expense':total_ebbills_expense,
#         #'prcharttotal':prcharttotal,  # Pass the overall total calls
#     }


#         # Pass the extracted data to the template
#     return render(request, 'home.html', context)
    

       
