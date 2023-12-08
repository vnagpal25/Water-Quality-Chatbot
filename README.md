# CSCE580-Fall2023-vansh_nagpal-Repo

## To use the chatbot for yourself, follow these instructions:
### Rasa Chatbot
#### How to Use
1) Launch two shells (can be windows CMD, Ubuntu, etc.)

2) Create a new virtual environment using conda(works with pip)

```
conda create --name water_chatbot_venv python=3.7
```

3) Ensure that the virtual environment is activated

```
conda activate water_chatbot_venv
```

4) In the terminal run the following command to install the required packages:

```
pip install -r requirements.txt
```

5) Navigate to ./code and run the following command to train the rasa chatbot

```
rasa train
```

6) In the same terminal navigate to ./code/actions and run the following command to start the actions server

```
rasa run actions
```

7) In the other terminal, start the chatbot

```
rasa shell
```

8) Start interacting with the Chatbot. Ask it questions regarding the safety of water data sites. 
  a. See ./data/json/good_data_sites.json for example site names. 
  b. Ask it questions like "fetch me the water data for {site_name}" or "is the water from {site name} safe to drink?". 
  c. Other variations work as well due to the robustness of rasa.

#### Water Quality Project for CSCE 580: Artificial Intelligence

#### See docs for a detailed report on the project and instructions to reproduce results

#### See ./code for implementation of chatbot and decision maker in Python
#####  - robust chatbot based on RASA with learning-based decision maker 
#####  - see [rasa docs](https://rasa.com/docs/rasa/) for more information

#### See ./data for all necessary data to run instance of chatbot
#####  - ./data/csv: labeled dataset from Kaggle
#####  - ./data/json: contains all parameter codes and site codes for USGS API
#####  - ./data/model: contains saved SVC model that trained on Kaggle dataset
#####  - ./data/npy: contains BERT vectorized embeddings for site names
#####  - ./data/user_sessions: contains saved conversations from user

#### See test for some example tests of the system working.