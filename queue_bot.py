from slackclient import SlackClient
import os, time
from slackqueue import SlackQueue


# Todo: use an actual queue data structure, built on a linked list
# SERIOUSLY DO THIS. Don't use a dictionary forever; that's gross. The
# list is also inefficient.

_QUEUE = SlackQueue()

def run_bot_update_queue(sc, channel_name):
    """Check latest messages constantly and update queue."""

    # Set the channel to send messages to, based on name passed
    channel_info = sc.server.channels.find(channel_name)
    channel_id = channel_info.id

    # TODO: Add whitelist of users who are allowed to interact with queue bot
    # to make sure staff are the only ones who can manage the queue.

    # Read messages forever!
    while True:

        latest = sc.rtm_read()

        # Are there any new messages, and are they not the stock bot connection
        # message?
        if (latest != [] and
            latest != [{'text': u'hello'}]):

            latest = latest[0]

            # Make sure we're in the desired channel and the latest update
            # was actually a message, not a typing notification.
            if (latest.get("channel") == channel_id and
                latest.get("type") == "message"):

                text = latest["text"]
                print "Latest:", latest

                if "queue.open()" in text.lower():
                    _QUEUE.is_open = True
                    sc.rtm_send_message(
                        channel_id,
                        _QUEUE.generate_display()
                    )
                    continue

                elif "queue.close()" in text.lower():
                    _QUEUE.is_open = False
                    while not _QUEUE.is_empty():
                        _QUEUE.dequeue()

                    sc.rtm_send_message(
                        channel_id,
                        "The queue is closed. Please hop in later if you need to!"
                    )
                    continue

                if _QUEUE.is_open:
                    _QUEUE.update(text)

                    if _QUEUE.has_changed:
                        sc.rtm_send_message(
                            channel_id,
                            _QUEUE.generate_display()
                        )

                time.sleep(.5)


if __name__ == "__main__":

    # Get API token and instantiate a client for all our Slack
    # interactions.
    slack_token = os.environ.get("BOT_API_TOKEN")
    sc = SlackClient(slack_token)

    # Try to connect to the real time messaging service
    if sc.rtm_connect():
        run_bot_update_queue(sc, "help")
    else:
        print "Connection Failed"
