import json
import joblib
import numpy as np

class DataLoader:
  def __init__(self):
    self.model_path = "../../data/model"
    self.json_path = "../../data/json"
    self.np_path = "../../data/npy"

  def get_models(self):
    """
    Get SVM classifier, Gaussian Parameters and Default Values
    """
    svc = joblib.load(f'{self.model_path}/svc_classifier.joblib')

    default_values = open(f'{self.json_path}/default_values.json')
    default_values = json.load(default_values)

    gaussian_weights = open(f'{self.json_path}/gaussian_parameters.json')
    gaussian_weights = json.load(gaussian_weights)

    return svc, default_values, gaussian_weights, 


  def get_usgs_site_data(self):  
    """
    USGS Site and Paramter Codes Information 
    """
    site_codes = open(f'{self.json_path}/good_data_sites.json')
    site_codes = json.load(site_codes)  
    
    site_names = list(site_codes.keys())
    
    site_name_embeddings = np.load(f'{self.np_path}/good_data_site_code_embeddings.npy')
    
    param_codes = open(f'{self.json_path}/parameter_codes.json')
    param_codes = json.load(param_codes)

    return site_codes, site_names, site_name_embeddings, param_codes
