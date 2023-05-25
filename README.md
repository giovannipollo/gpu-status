# gpu-status

Telegram bot to manage the GPU status of a server.

# How to use

Create a `conf.json` organized as follows:
```json
{
    "api-key": "your_api_key",
    "group-id": "your_group_id"
}
```
Then create a `venv` by running the following command:
```bash
python3 -m venv venv
```
Activate the `venv` by running the following command:
```bash
source venv/bin/activate
```
Install the dependencies by running the following command:
```bash
pip install -r requirements.txt
```
Run the bot by running the following command:
```bash
python3 bot.py
```

# Logic

This bot aims at helping the users of a server to manage the GPU status. It has been designed to be added to a telegram group where all the users of the server are present. The main command of the bot, that is callable by the users in the group is `/gpustatus`. This command will show the status of the GPU of the server. At the moment it has only been tested on single GPU server. Feel free to open a pull request to extend the functionality to multi GPU servers. The bot will show the status of the GPU in the following format:
```
Total Memory: total_memory MB
Used Memory: used_memory MB
Free Memory: free_memory MB

Users:
User: username -> used_memory MB

WARNING: GPU is being used
```

In addition to that the bot pools the GPU status every 5 minutes and buffers the last 3 checks. If the last 2 checks differs from the current check, the bot will send a message to the group to warn the users that the GPU status has changed. This is very useful to notify the users both that the GPU has become free or that it has been taken by someone. 