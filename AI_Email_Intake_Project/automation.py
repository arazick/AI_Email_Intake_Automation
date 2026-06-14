from openai import OpenAI
from sk import my_sk
import json
from datetime import datetime
from tabulate import tabulate

OPENAI_API_KEY = my_sk #API secret key
inbox = [] #list of all emails from text file
with open ("emails.txt", "r") as emails: #read from text file and add each non-blank line to the 'inbox' array
        for line in emails:
            email = line.strip()
            if(not email):
                   continue
            else:
                inbox.append(email)
######################################################################################################################################################
        #CREATE RACE SCHEDULES
races = {
      "5K":{
      "Winter 5K":{"date" : "01/01/2026","time" : "8:00 AM","registrant_names" : [] },
      "Spring 5K":{"date" : "05/13/2026","time" : "7:45 AM", "registrant_names" : [] },
      "Summer 5K": {"date" : "07/18/2026","time" : "8:00 AM", "registrant_names" : [] },
      "Fall 5K": {"date" : "10/07/2026","time" : "9:00 AM", "registrant_names" : [] }
      },
      "10K" : {
        "Thanksgiving 10K" : {"date" : "11/26/2026", "time" : "8:00 AM", "registrant_names" : []},
        "New Year's Day 10K" : {"date" : "01/01/2026", "time" : "8:30 AM", "registrant_names" : []},
        "Mother's Day 10K" : {"date" : "05/10/2026", "time" : "9:00 AM", "registrant_names" : []},
        "Father's Day 10K" : {"date" : "06/21/2026", "time" : "8:00 AM", "registrant_names" : []}
      },
      "Half Marathon" : {
        "Life Time Chicago Half Marathon" : {"date" : "01/01/2026", "time" : "7:00 AM", "registrant_names" : []},
        "Rock 'n' Roll Las Vegas Half Marathon": {"date" : "02/21/2026", "time" : "9:00 AM", "registrant_names" : []},
        "Anchorage Mayor's Half Marathon" : {"date" : "06/18/2026", "time" : "8:30 AM", "registrant_names" : []},
        "RunSedona" : {"date" : "02/06/2026", "time" : "8:00 AM", "registrant_names" : []}
      },
      "Marathon": {
            "Boston Marathon" : {"date" : "04/19/2026", "time": "8:45 AM", "registrant_names": []},
            "London Marathon": {"date": "04/25/2026", "time": "8:00 AM", "registrant_names": []},
            "New York City Marathon": {"date": "11/01/2026", "time": "9:40 AM", "registrant_names": []},
            "Chicago Marathon": {"date": "10/11/2026", "time": "7:00 AM", "registrant_names" : []}

      }
}

######################################################################################################################################################
        #START CLIENT - READ EMAILS AND EXTRACT DETAILS
client = OpenAI(api_key=OPENAI_API_KEY) #create client
registration_requests = []
for mail in inbox:
    response = client.responses.create(
    model = "gpt-4",
    instructions=
    "You are reading a race registration email. Extract the following information:" \
    "1. full_name" \
    "2. race_distance" \
    "3. race_date in mm/dd/yyyy" \
    "Rules: " \
    "1. If any of those 3 fields are MISSING, set them to 'null'" \
    "2. race_distance must be explicitly one of the following: 5K, 10K, Half Marathon, Marathon, or null if none match or no race_distance is provided. Extract only the first race provided in the request" \
    "3. Assume that the year is 2026 if no year is given" \
    "4. Return ONLY a valid JSON in the following format: "\
    '{"full_name": ..., "race_distance": ..., "race_date": ...}'\
    "5. Do not include explanations or extra text" \
    "6. full_name does NOT include any periods, commas, or other punctuation" \
    "7. An incorrectly spelled month is an invalid date" \
    "8. If a date is invalid, you should still extract the data without altering it.",
    input=mail,
    temperature = 0
    )
    registration= json.loads(response.output_text)
    registration_requests.append(registration)
client.close()

######################################################################################################################################################
        #REGISTRATION VALIDATION/LOGIC
email = ""
for registration in registration_requests:
        valid_name = True
        valid_race_distance = True
        valid_race_date = True
######################################################################################################################################################
        #RACE NAME VALIDATION
        if(registration.get("full_name") == "null"): #no name provided - WORKS
              email = email + "Dear Registrant,\nWe were unable to register you because you have not provided your first and last name. Please provide a valid first and last name.\n"
              valid_name = False
        else:
            name = registration.get("full_name").split(" ")
            if(len(name) == 1): #missing either first or last name (one has not been provided) - WORKS
                    email = email + "Dear " + registration.get("full_name") + ", \nWe were unable to register you because you have not provided your full name. Please provide a valid first and last name.\n" 
                    valid_name = False
            elif((len(name[0]) ==1 or len(name[1]) ==1)): #first OR last name not long enough - WORKS
                    email = email + "Dear " + registration.get("full_name") + ", \nWe were unable to register you because you have not entered a valid first name and/or last name. Please enter your at least two characters for both the first and last name.\n" 
                    valid_name = False
            else:
                    email = email + "Dear " + registration.get("full_name") + ",\n"
######################################################################################################################################################
        #RACE DISTANCE VALIDATION           
        distance = registration.get("race_distance")
        if((distance != "5K" and distance != "10K" and distance!= "Half Marathon" and distance!= "Marathon")): #INVALID DISTANCE
              valid_race_distance = False
              email = email + "We were unable to register you because you have not selected a valid race distance. Please choose from the following: \n - 5K\n - 10K\n - Half Marathon\n - Marathon\n"
######################################################################################################################################################
        #RACE DATE VALIDATION           
        date = registration.get("race_date")
        if(date == "null"):
            valid_race_date = False
            email = email + "We were unable to register you because you have not provided a date. Please enter a valid date.\n"
        else:
                format = "%m/%d/%Y"
                try:
                    datetime.strptime(date, format)
                except ValueError:
                    valid_race_date = False
                    email = email + "We were unable to register you because you have provided an invalid date. Please enter a valid date."
                else:
                    races_on_date = []
                    for race_type, subraces in races.items():
                            for race_name, race_info in subraces.items():
                                if(race_info["date"] == date):
                                    option = race_name
                                    races_on_date.append(option)
                    if(len(races_on_date) == 0):
                        email = email + "We were unable to register you because there are no races on the date you have entered, please try a different date.\n"
        if (valid_race_distance and valid_race_date):
            match = False
            name_of_race = ""
            for race_name, race_info in races[distance].items():
                                if(race_info["date"] == date):
                                    match = True
                                    name_of_race = race_name
                                    break
            if (valid_name and match):
                    races[distance][name_of_race]["registrant_names"].append(registration.get("full_name"))
                    email = email + "You have successfully registered for the " + name_of_race + " on " + date + ". We look forward to seeing you there!\n"
            elif(len(races_on_date) >= 1 and not match):
                                email = email + "Sorry, there are no " + distance + " races on " + date + " Here are specific race(s) taking place on the date you entered: \n"
                                for choice in races_on_date:
                                    email = email + ("- " + choice + "\n")
                                email = email + "Let us know if you would be interested in registering for any of these races!\n"
        email = email + "Thank You,\nRace Registration"   
        email = email + "\n---------------------------------------------------\n"            
with open ("outbox.txt", "w") as output:
      output.write(email)
# print(email) #individualized confirmation/rejection message (uncomment if you would like to see output in terminal)

######################################################################################################################################################
        #PRINT TABLE FOR EACH CATEGORY DISTANCE RACE: 5K, 10K, HALF MARATHON, MARATHON
print()
print("RACE SCHEDULES FOR EACH DISTANCE\n")
for race_type, subraces in races.items():
    table = [['Race Name', 'Date', 'Time', 'Registrants']]
    for race_name, race_info in subraces.items():
        date = race_info['date']
        time = race_info['time']
        registrants = ""
        for person in race_info['registrant_names']:
             registrants = registrants + "- " + person + "\n"
        table.append([race_name, date, time, registrants])
    print(race_type + " Races")   
    print(tabulate(table, headers = 'firstrow', tablefmt = 'fancy_grid'))
    print()

              