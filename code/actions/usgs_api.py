import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests as rq
from termcolor import colored
from sentence_transformers import SentenceTransformer # nlp library

from data_loader import DataLoader
class USGS_API:
  def __init__(self):
    self.DataLoader = DataLoader()
    self.site_codes, self.site_names, self.site_name_embeddings, self.param_codes = \
    self.DataLoader.get_usgs_site_data()

    self.bert_model = SentenceTransformer("bert-base-uncased") 

    self.request_url = "https://waterservices.usgs.gov/nwis/dv/?"


  def handle_site_request(self, site_name):
    """Given a user entered site name, compares given site name with cached site names using BERT
      Then closest actual site name to entered object"""
    # TODO, only return if the cosine similarity is above 0.5

    # use BERT to encode phrase embedding for request site
    site_embedding = self.bert_model.encode(site_name) 

    # insert embedding into existing array of embeddings
    phrase_embeddings = np.insert(self.site_name_embeddings, 0, site_embedding, axis=0)

    # compare first element with each subsequent element using cosine similarity
    similarity_vector = cosine_similarity(phrase_embeddings[0:1], phrase_embeddings[1:])

    # get index of max value, and return the site at that index
    max_index = np.argmax(similarity_vector)
    site_name = self.site_names[max_index]
    site_code = self.site_codes[site_name]
    return site_code, site_name


  def make_api_call(self, official_site_code):
    """Given the site code of the site, 
      makes an api call to USGS and decodes relevant time series data for processing"""
    
    # formats url request, making request and decoding json string as dict
    req_url_past_month =f'{self.request_url}site={official_site_code}&format=json&period=P30D&statCd=00003'
    data_past_month = rq.get(req_url_past_month)
    data_past_month = data_past_month.json()
    
    req_url_all = f'{self.request_url}site={official_site_code}&format=json&statCd=00003'
    data_all = rq.get(req_url_all)
    data_all = data_all.json()

    measured_values_strings ,measured_values_floats = \
      self.extract_usgs_json_data(data_all, time_series=False)
    
    measured_values_strings_ts, measured_values_floats_ts = \
      self.extract_usgs_json_data(data_past_month)

    # update the dictionaries with the acquired time series values
    measured_values_strings.update(measured_values_strings_ts)

    measured_values_floats.update(measured_values_floats_ts)

    # returns data
    return measured_values_strings, measured_values_floats


  def extract_usgs_json_data(self, data_json, time_series=True):
    """
    Parses through requested data from USGS API
    """
    # to return
    measured_values_strings = {}
    measured_values_floats = {}

    # getting time series data (all measurements collected at site) as dictionaries
    data_values = data_json['value']['timeSeries']

    # iterates over time series values
    for element in data_values:
        # getting variable name from variable code
        variable_code = element["variable"]["variableCode"][0]["value"]
        variable_name = self.param_codes[variable_code]
        
        # getting unit of measurement
        variable_unit = element['variable']['unit']['unitCode']

        # getting measured value
        measured_values = element['values'][0]['value']
        
        # sanity check for later
        data_exists = True

        # if multiple values required get average of all of them
        if time_series:
          mean_vals = []
          for val in measured_values:
            mean_vals.append(float(val['value']))

          if mean_vals:
            measured_value = np.mean(mean_vals)
          
          # if no values were found, we don't need to return them
          data_exists = data_exists and len(mean_vals) > 0

        # else get just a singular measured value
        else:
          measured_value = float(measured_values[0]['value'])

        # using sanity check
        if data_exists:
          # for user display
          measured_values_strings[variable_name] = \
            f'{measured_value} {variable_unit}'

          # prune the variable name
          pruned_var_name = self.prune(variable_name)

          # if desired parameter, then update the to return 
          if pruned_var_name:
            measured_values_floats[pruned_var_name] = measured_value
          
          # unit conversion from ug/L to mg/L = ppm
          if pruned_var_name == 'Trihalomethanes, water,':
            measured_values_floats[pruned_var_name] *= 1000

    # returns the measured data
    return measured_values_strings, measured_values_floats


  def prune(self, variable_name):
    """
    Checks if the variable name starts with any of the following prefixes,
    returns pruned name for ease of viewing
    """
    var_prefixes = ['pH', 'Dissolved oxygen', 'Turbidity', 'Specific conductance', 
                    'Temperature, water,','Hardness, water', 'Dissolved solids ', 'Chlorine', 
                    'Sulfate, water,', 'Organic carbon, water,', 'Trihalomethanes, water,']
    for var_prefix in var_prefixes:
      if variable_name.startswith(var_prefix):
        return var_prefix
    return ''
