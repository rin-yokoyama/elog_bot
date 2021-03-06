# elog_bot
A slack bot to submit messages to elog

## Requirements
- pipenv
- firefox + geckodriver
- convert command from the Imagemagick pacakge to resize image

Operation confiremed on CentOS 7

## Installation
- Create .env file under the top directory of the repository and set following environments.
```
SLACK_BOT_TOKEN=your_slack_bot_token
APP_LEVEL_TOKEN=your_app_token
ELOG_URL=url_to_your_elog
ELOG_UNAME=elog_user_name
ELOG_UPASSWORD=elog_user_password
```
- pipenv install

## Slack app
- Create a new slack bot in your workspace.
- Generate a new app level token with the connections:write scope.
- Add following OAuth scopes to the "Bot Token Scopes".
  - app_mentions:read
  - channels:history
  - channels:read
  - chat:write
  - files:read
  - groups:history
  - im:history
  - reactions:read
  - user::read
- Install the app to your workspace
- Enable Socket Mode
- Enable Event Subscription and subscribe to the following events
  - message.channels
  - message.groups
  - message.im
  - reaction_added

## channel2category.json
The file contains the dict of slack channel names to elog category name.
If the channel name or the category name does not exist in the dict or in the elog, respectively,
the category named "Slack" will be selected.
If there was no category named "Slack" existed, the first category will be selected to prevent the elog error.
```
{
  "slack_ch_name1": "elog_category_name",
  "slack_ch_name2": "elog_category_name",
  "slack_ch_name3": "elog_category_name"
}
```

## Usage
- pipenv shell
- python app.py
- Add your slack bot to the channels you want to use.
- Add :notebook: (notebook) emoji as a reaction to the message you want to submit to the elog
