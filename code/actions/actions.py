import sys
sys.path.append('/home/vnagpal/CSCE580/CSCE580-Fall2023-vansh_nagpal-Repo/code_v2/actions')
from typing import Any, Text, Dict, List


import rasa.core.tracker_store
from rasa.shared.core.trackers import DialogueStateTracker
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from usgs_api import USGS_API
from model_inference import WaterQualityDecision
from data_saver import DataSaver

DecisionBot = WaterQualityDecision()
USGS_ = USGS_API()
DataWriter = DataSaver()

class ActionMakeAPICall(Action):
    def name(self) -> Text:
        return "action_make_api_call"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # extract latest user message
        latest_msg = tracker.latest_message
        site_name_entities = latest_msg.get('entities', None)
        # pdb.set_trace()
        if site_name_entities is None:
            dispatcher.utter_message(text='No site name entered, please try again')
        else:
          ret_str = ""

          site_name = ""
          for site_name_entity in site_name_entities:
            site_name += (" " + site_name_entity['value'])

          # official closest site name
          site_code, site_name  = USGS_.handle_site_request(site_name)

          ret_str += f"Requested site: {site_name}. Site Code: {site_code}\n"

          measured_data, _ = USGS_.make_api_call(site_code)
          ret_str += "Most recently measured data:\n"
          for key in measured_data: ret_str = ret_str + str(key) + ': ' + str(measured_data[key]) +'\n'
          
          dispatcher.utter_message(text=ret_str)
        return []

class ActionGetWaterDecision(Action):
    def name(self) -> Text:
        return "action_get_water_decision"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # extract latest user message
        latest_msg = tracker.latest_message
        site_name_entities = latest_msg.get('entities', None)
        # pdb.set_trace()
        if site_name_entities is None:
            dispatcher.utter_message(text='No site name entered, please try again')
        else:
          ret_str = ""

          site_name = ""
          for site_name_entity in site_name_entities:
            site_name += (" " + site_name_entity['value'])

          # official closest site name
          site_code, site_name  = USGS_.handle_site_request(site_name)

          ret_str += f"Requested site: {site_name}. Site Code: {site_code}\n"

          _, measured_data = USGS_.make_api_call(site_code)

          # gets chatbot response based on potability conf and number of params(robustness)
          ret_str += DecisionBot.get_decision_string(measured_data)

          dispatcher.utter_message(text=ret_str)
        return []

class ActionSaveConversation(Action):
    def name(self) -> Text:
        return "action_save_conversation"




    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hist = tracker.events
        user_queries = []
        bot_responses = []        
        for el in hist:
          if el['event'] == 'user':
            user_queries.append(el['text'])
          elif el['event'] == 'bot':
            bot_responses.append(el['text'])
        DataWriter.save_conversation(user_queries, bot_responses)
        return []
