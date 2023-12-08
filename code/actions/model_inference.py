import numpy as np
from termcolor import colored
from data_loader import DataLoader

class WaterQualityDecision():
  def __init__(self):
    """
    Load Models
    """
    self.DataLoader = DataLoader()
    self.svc, self.default_values, self.gaussian_weights = self.DataLoader.get_models()


  def get_confidence_gaussian(self, measured_data):
    """Given measured data parameters, returns confidence of 
      potability using average of gaussian confidences"""
    assert type(self.gaussian_weights) == dict and type(measured_data) == dict

    decision_conf = 0
    num_vars = 0

    for var_name, var_value in measured_data.items():
      if var_name in self.gaussian_weights:
        center, width = float(self.gaussian_weights[var_name]['center']), float(self.gaussian_weights[var_name]['width'])
        conf = np.exp(-width *((var_value - center) ** 2))
        decision_conf += conf
        num_vars += 1
      
    if num_vars == 0:
      decision_conf = 0
    else:
      decision_conf /= num_vars

    return decision_conf, num_vars


  def get_confidence_svc(self, measured_data):
    # our input vector 'x' that will be fed to svm classifier
    x = []
    
    deciding_params = 0 # number of relevant parameters measured
    
    for param_name in self.default_values.keys():
      if param_name in measured_data:
        x.append(measured_data[param_name])
        deciding_params += 1
      else:
        x.append(self.default_values[param_name])
    
    # converting np array for input to svc
    # casting to float to convert strings
    # reshaping to 2D because that is expected input to svc
    x = np.array(x).astype(float).reshape(1, -1) 

    # first value is the probability that the water is unpotable
    # second value is the prob that the water is potable (what we are concerned with)
    (_, decision_conf) = self.svc.predict_proba(x)[0] # removing second dimension heres
    
    return decision_conf, deciding_params


  def get_decision_string(self, measured_data):
    gaussian_confidence, _ = self.get_confidence_gaussian(measured_data)
    svc_confidence, _ = self.get_confidence_svc(measured_data)
    
    num_vars = len(measured_data.keys())
    
    """
    Decision String Method:

      Aggregate the confidence of potability as the average of the gaussian smoothing method
      and the SVM classification method

      Conf less than 0.80: hard reject (red)
      Conf more than 0.80, non robust analysis: very cautionary accept (yellow)
      Conf more than 0.80, robust analysis: cautionary accept (green)
    """
    
    # aggregating results
    confidence = np.mean([gaussian_confidence, svc_confidence])

    if confidence >= 0.70:
      if num_vars >= 3:
        return colored(f"Based on my analysis, I assign this water safe to drink with a confidence of {'%.2f' % (round(confidence, 2) * 100)}%\n"
        'I would still recommend testing this water\'s quality using either an at-home water testing kit or by contacting your local water provider.',
        'green')
      else:
        return colored(f"Based on my analysis, I assign this water safe to drink with a confidence of {'%.2f' % (round(confidence, 2) * 100)}%\n"
        f'Keep in mind this analysis was performed with {num_vars} measured parameters, which is not enough to ensure robustness.\n'
        'I would still recommend testing this water\'s quality using either an at-home water testing kit or by contacting your local water provider.',
        'yellow')
    else:
      return colored(f"Based on my analysis, I assign this water safe to drink with a confidence of {'%.2f' % (round(confidence, 2) * 100)}.%\n"
      f'PLEASE DO NOT DRINK THIS WATER, measured {num_vars} parameters', 'red')
