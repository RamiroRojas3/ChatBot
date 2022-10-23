
# Chatbot in Rasa

This repository is a chatbot developed in Rasa. It focuses on representing me as a student in Systems Engineering. Any person can talk with the chatbot about my career progress and also about my personal information.

## Installation
Use a virtual enviroment as [Anaconda](https://www.anaconda.com/products/distribution), download and install it.
Then you need [Python](https://www.python.org/), currently using version 3.9.12

Once you have both of them, get inside the terminal and create a virtual enviroment and excute, (without the ").
```bash
create --name "NameOfYourEnviroment" python="YourPythonVersion"
```
This command create the virtual enviroment, and everytime you want to get in the enviroment you must run the next command.
```bash
conda activate "NameOfYourEnviroment"
```
Once we are in the enviroment, we install the next dependencies, one at time.
```bash
conda install ujson
conda install tensorflow
pip install rasa
```
Now you are ready to pull the repository and in the terminal inside the virtual enviroment you can train it, and run it

## Usage

Once you clone or pull the repository to your local, the you have to train it, so inside your terminal and inside the conda enviroment with rasa you run the next command
```bash
rasa train
```
when the train is finished, run the next commands for test it
```bash
rasa shell
```
After this command finish, in the terminal should appear a "type:" or something as this where you can insert your intention and talk to the chatbot.

## Usage with Telegram

To use it in Telegram, then you shoul do some modifications after the installation of rasa.
Find where your virtual enviroment is installed, inside that directory go to "PathOfYourEnvirment"/RASA/Lib/site-packages/rasa/core/channels/channel.py in windows and "PathOfYourEnvirment"/lib/python3.8/site-packages/rasa/core/channels in linux. Then inside this python file search for the function "get_metadata()" and change the content to this
```python
def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
       metadata = request.json
       return metadata
``` 
