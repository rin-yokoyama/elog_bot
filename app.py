import os
import re
import subprocess
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
            chan_id = result["channel"]["id"]
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

            # link to the message
            permalink = "link not available"
            result = client.chat_getPermalink(token=BOT_TOKEN, channel=chan_id, message_ts=message['ts'])
            if result["ok"] == True:
                permalink = result["permalink"]

            print(chan)
            print(user)
            print(euser)
            print(content)
            print(ts)
            print(permalink)
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
                        if re.match('.*\\.(png|jpg)+$', filename, re.IGNORECASE):
                            cmd = 'convert -resize \"1080x1080>\" ' + filename + ' ' + filename
                            proc = subprocess.call(cmd,shell=True)
                    else:
                        say(f"<@{event['user']}>Error: Failed to download file {filename}")

            print(attfiles)
            elog_url = elog.post_entry(chan, user, euser, content, ts, permalink, attfiles)
            if elog_url == None:
                msg = f"<@{event['user']}>Error in post_elog_entry(). The message was not submitted correctly. Check drafts in the elog"
                if __debug__:
                    print(msg)
                else:
                    say(msg)
            else:
                msg = f"<@{event['user']}> The message has been submitted to the elog: {elog_url}"
                if __debug__:
                    print(msg)
                else:
                    say(msg)

        except SlackApiError as e:
            msg = f"<@{event['user']}>Error: {e}"
            if __debug__:
                print(msg)
            else:
                say(msg)

# launching the app
if __name__ == "__main__":
    SocketModeHandler(app, APP_TOKEN).start()
