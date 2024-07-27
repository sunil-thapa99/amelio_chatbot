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

def get_policy_from_db(hr_policy_type):
    # Returns list of policy
    return []

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

            print('--------------------', hr_policy_type)
    
            if hr_policy_type:
                message = f"You selected: {hr_policy_type} policy."
                policy_templates = get_policy_from_db(hr_policy_type)
                buttons = []
                if policy_templates:
                    message += "\nHere are some templates for you:"
                    for p_template in policy_templates:
                        # Suggest as button
                        buttons.append({
                            "payload": f'/policy_type{"policy_name": {p_template.name},}',
                            "title": p_template.title
                        })
                buttons.append(
                    {"payload": '/policy_type{"policy_name": None}', "title": "Create you own"}
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
            
            selected_policy = tracker.get_slot('policy_name')
            if selected_policy.lower() == 'flexible work':
                dispatcher.utter_message(response="utter_ask_flexible_work_option")
            else:
                dispatcher.utter_message(text="No policy type selected")
            return []
        
class ActionSelectFlexibleWorkOption(Action):

    def name(self) -> Text:
        return "action_select_flexible_work_option"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_option = tracker.get_slot('flexible_work_option')

        # Define the predefined options
        options = {
            'a': 'Flexible hours: Employees can choose their start and end times, with a mandatory core period (e.g., from 10 AM to 3 PM).',
            'b': "Remote work: Employees can work remotely up to 2 days per week, with their manager's approval.",
            'c': 'Compressed workweek: Employees can work their weekly hours in fewer days (e.g., four days instead of five).',
            'd': 'Part-time work: Employees can choose to work part-time for a determined or undetermined period, with their manager\'s approval.',
            'e': 'Unpaid leave: Employees can take unpaid leave in addition to their paid leave, subject to approval.',
            'f': 'Irregular schedule: Employees can follow a personalized schedule where their working hours are not fixed from day to day, but their total working hours and pay remain the same.',
            'g': 'Job sharing: Two employees can share the responsibilities of a single full-time position, with reduced working hours and shared responsibilities.'
        }

        selected_descriptions = options[selected_option]

        dispatcher.utter_message(text=f"You selected the following option for the Flexible Work Policy:\n{selected_descriptions}")

        return [SlotSet('selected_flexible_work_options', selected_descriptions)]