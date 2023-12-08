import json
import os

class DataSaver:
  def save_conversation(self, user_queries, bot_responses):
    user_interactions = dict(zip(user_queries, bot_responses))

    # data path and files in data path
    data_path = os.path.abspath('../data/user_sessions')
    data_files = os.listdir(data_path)
    
    # get file number to save from previously saved user interaction files
    data_files = [data_file for data_file in data_files if data_file.startswith('user_session')]
    dot_indices = [data_file.find('.') for data_file in data_files]
    file_numbers = [int(data_file[12:dot_index]) for dot_index, data_file in zip(dot_indices, data_files)]
    file_number_to_save = 1 if len(file_numbers) == 0 else max(file_numbers) + 1

    # saves file
    file_name_to_save = os.path.join(data_path, 'user_session' + str(file_number_to_save) + '.json')
    save_file = open(file_name_to_save, 'w')
    json.dump(user_interactions, save_file)
    save_file.close()

