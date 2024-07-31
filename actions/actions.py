# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import mysql.connector
from mysql.connector import errorcode

config = {
    'host': '127.0.0.1',  # or your MySQL server host
    'user':'root', 
    'password':"",
    # Add 'user' and 'password' fields if your MySQL server requires them
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
cursor.execute("USE amelio")

def get_policy_from_db(table_name, attribute_name, value):
    value = value.lower()
    query = f"SELECT * FROM {table_name} WHERE {attribute_name}='{value}'"
    cursor.execute(query)
    result = cursor.fetchmany()
    # Returns list of policy
    return result

class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        messages = ["Hi there. 👋😃 It's such a pleasure to have you here. How may I help you?",
                    "Hello, 🤗 how can we assist you?"]
        
        buttons = [
            # {"payload": "/job_posting", "title": "Job Posting"},
            # {"payload": '/hr_policy', "title": "HR Policy"},
            {"payload": '/select_option{"option": "selected_hr_policy"}', "title": "HR Policy"}
        ]

        reply = random.choice(messages)
        dispatcher.utter_message(text=reply, buttons=buttons)

        return []



class ActionHrPolicy(Action):
    
        def name(self) -> Text:
            return "action_hr_policy"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            # buttons = [
            #     {"payload": "/hr_policy{'content_type': 'hr_policy'}", "title": "HR Policy"},
            #     {"payload": "/job_posting", "title": "Job Posting"}
            # ]
            print(tracker.get_intent_of_latest_message(), '=================')
            try:
                hr_policy_type = tracker.get_slot("hr_policy_type")
            except:
                hr_policy_type = None
    
            if hr_policy_type:
                message = f"You selected: {hr_policy_type} policy."
                # policies = get_policy_from_db('hr_policy', 'policy_name', hr_policy_type)
                # Fetch all of remote work policies
                # query = f"SELECT hr_policy_type.* \
                #             FROM hr_policy_type \
                #             JOIN hr_policy ON hr_policy_type.hr_policy_id = hr_policy.id \
                #             WHERE hr_policy.policy_name = '{hr_policy_type}'; \
                #         "
                # cursor.execute(query)
                # policies = cursor.fetchmany()
                policies = [
                    ('flexible', 'Flexible Work'),
                    ('remote', 'Remote Work'),
                    ('part_time', 'Part-time Work'),
                    ('unpaid_leave', 'Unpaid Leave'),
                    ('job_sharing', 'Job Sharing')
                ]
                buttons = []
                if policies:
                    message += "\nHere are some templates for you:"
                    for p_template in policies:
                        # Suggest as button
                        buttons.append({
                            "payload": '/policy_type{"policy_name": "'+p_template[1]+'"}',
                            "title": p_template[1].capitalize()
                        })
                buttons.append(
                    {"payload": '/policy_type{"policy_name": None}', "title": "Create your own"}
                )
                dispatcher.utter_message(text=message, buttons=buttons)
            else:
                message = "You have selected HR policy. \nWhat policy would you like to create?"
                dispatcher.utter_message(text=message,)
    
            return []

class ActionPolicyType(Action):
        
        def name(self) -> Text:
            return "action_policy_type"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            try:
                selected_policy = tracker.get_slot('policy_name')
            except:
                selected_policy = None
            print('-----------------', selected_policy)
            # query = f"SELECT * FROM hr_policy_type WHERE {attribute_name}='{value}'"
            # cursor.execute(query)
            # result = cursor.fetchmany()
            # selected_policy = get_policy_from_db('hr_policy_type', 'policy_name', selected_policy)
            selected_policy = 'flexible'
            if selected_policy.lower() == 'flexible':
                options = {
                    'a': 'Flexible hours: Employees can choose their start and end times, with a mandatory core period (e.g., from 10 AM to 3 PM).',
                    'b': "Remote work: Employees can work remotely up to 2 days per week, with their manager's approval.",
                    'c': 'Compressed workweek: Employees can work their weekly hours in fewer days (e.g., four days instead of five).',
                    'd': 'Part-time work: Employees can choose to work part-time for a determined or undetermined period, with their manager\'s approval.',
                    'e': 'Unpaid leave: Employees can take unpaid leave in addition to their paid leave, subject to approval.',
                    'f': 'Irregular schedule: Employees can follow a personalized schedule where their working hours are not fixed from day to day, but their total working hours and pay remain the same.',
                    'g': 'Job sharing: Two employees can share the responsibilities of a single full-time position, with reduced working hours and shared responsibilities.'
                }
                buttons = []
                for key, value in options.items():
                    buttons.append({
                        "payload": '/select_flexible_work_option{"flexible_work_option": "'+key+'"}',
                        "title": value
                    })
                dispatcher.utter_message(text="Please select your flexible work option:", buttons=buttons)
            else:
                dispatcher.utter_message(text="No policy type selected")
            return []
        
class ActionSelectFlexibleWorkOption(Action):

    def name(self) -> Text:
        return "action_select_flexible_work_option"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        flexible_work_option = tracker.get_slot('flexible_work_option')
        dispatcher.utter_message(text=f"You have selected: {flexible_work_option}")
        return []
        # return [SlotSet('flexible_work_option', flexible_work_option)]