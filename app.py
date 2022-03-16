import os
import requests
import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from post_elog_entry import ElogWriter

# Initialization of the app with tokens
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
APP_TOKEN = os.environ.get("APP_LEVEL_TOKEN")
app = App(token=BOT_TOKEN)
client = WebClient(token=BOT_TOKEN)
elog = ElogWriter()

@app.event("reaction_added")
def reaction_handler(event, say):
    if event['reaction'] == 'notebook':
        item = event['item']
        euser_id = event['user']
        # ID of channel that the message exists in
        conversation_id = item['channel']

        try:
            # Call the conversations.history method using the WebClient
            # The client passes the token you included in initialization    
            result = client.conversations_history(
                channel=conversation_id,
                inclusive=True,
                oldest=item['ts'],
                limit=1
            )
            message = result["messages"][0]
            # content of the slack post
            content = message["text"]
            ts = str(datetime.datetime.fromtimestamp(float(message["ts"])))

            result = client.conversations_info(
                channel=conversation_id
            )
            # channel name
            chan = result["channel"]["name"]
            # user name of the slack post
            user_id = message["user"]
            result = client.users_info(
                user=user_id
            )
            user = result["user"]["real_name"]
            # name of the reacted user 
            result = client.users_info(
                user=euser_id
            )
            euser = result["user"]["real_name"]

            print(chan)
            print(user)
            print(euser)
            print(content)
            print(ts)
            attfiles = []
            file_path = os.getcwd() + "/files/"
            if 'files' in message:
                for file in message['files']:
                    if 'url_private_download' in file and 'name' in file:
                        url=file['url_private_download']
                        print(url)
                        filename=file_path + file['name']
                        urlData = requests.get(
                            url,
                            allow_redirects=True,
                            headers={'Authorization': 'Bearer %s' % BOT_TOKEN},
                            stream=True
                        ).content
                        with open(filename ,mode='wb') as f: # write in byte type
                            f.write(urlData)
                        attfiles.append(filename)
                    else:
                        say(f"<@{event['user']}>Error: Failed to download file {filename}")

            print(attfiles)
            elog.post_entry(chan, user, euser, content, ts, attfiles)

        except SlackApiError as e:
            say(f"<@{event['user']}>Error: {e}")

# launching the app
if __name__ == "__main__":
    SocketModeHandler(app, APP_TOKEN).start()
