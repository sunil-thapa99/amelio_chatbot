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
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import errorcode

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(
  api_key=OPENAI_KEY
)

config = {
    'host': '127.0.0.1',  # or your MySQL server host
    'user':'root', 
    'password':"",
    # Add 'user' and 'password' fields if your MySQL server requires them
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
cursor.execute("USE amelio")

PROMPT_TEMPLATE = """
You are an expert in drafting HR policies. I am currently working on creating an {job_type}. The policy will include the following condition: {flexible_work_option}.
Based on this specific clause, please provide a list of detailed questions to consider:
"""

with open('actions/predefined_questions.json', 'r') as file:
    predefined_questions = json.load(file)

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
                            "payload": '/policy_type{"policy_name": "'+p_template[0]+'"}',
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
                options = predefined_questions[selected_policy]
                buttons = []
                for key, option_val in options.items():
                    print(key, type(key), '========================================================', option_val, type(option_val))
                    buttons.append(
                        {
                            "label" : option_val,
                            "value": "/select_flexible_work_option{'flexible_work_option': '"+key+"'}"
                        }
                    )
                message={"payload":"dropDown","data":buttons}
                    # buttons.append({
                    #     "payload": '/select_flexible_work_option{"flexible_work_option": "'+key+'"}',
                    #     "title": value
                    # })
                # dispatcher.utter_message(text="Please select your flexible work option:", buttons=buttons)
                print('-------------', message, '=================')
                dispatcher.utter_message(text="Please select your flexible work option:", json_message=message)
            else:
                dispatcher.utter_message(text="No policy type selected")
            return []

def prompt_engineering(context, prompt):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
    )
    return response.choices[0].text

class ActionSelectFlexibleWorkOption(Action):

    def name(self) -> Text:
        return "action_select_flexible_work_option"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        flexible_work_option = tracker.get_slot('flexible_work_option')
        option = tracker.get_slot('option').split('_')
        option = ' '.join(option[1:])
        hr_policy_type = tracker.get_slot('hr_policy_type')
        job_type = f'{hr_policy_type} for {option} work'
        selected_policy = tracker.get_slot('policy_name')
        flexible_work_option = predefined_questions[selected_policy].get(flexible_work_option)
        prompt = PROMPT_TEMPLATE.format(job_type=job_type, flexible_work_option=flexible_work_option)
        questions = prompt_engineering(context=job_type, prompt=prompt)
        dispatcher.utter_message(text=questions)
        # dispatcher.utter_message(text=f"You have selected: {flexible_work_option}")
        return []
        # return [SlotSet('flexible_work_option', flexible_work_option)]