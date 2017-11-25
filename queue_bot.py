from slackclient import SlackClient
import os, time, re, random


# Todo: use an actual queue data structure, built on a linked list
_QUEUE = []

QUEUE_EMPTY_MESSAGES = {
    "QUEUE = []",
    "QUEUE =  [ ]",
    "QUEUE=[]",
    "QUEUE=[ ]",
    "QUEUE = [ ]",
    "queue = []",
    "queue= []",
    "queue =[]",
    "queue =  []",
    "queue=[ ]",
    "queue = [ ]",
    "queue =[ ]",
    "queue= [ ]",
    "QUEUE.open()",
    "QUEUE.open( )",
    "queue.open()",
    "queue.open( )",
}

EMOJIS = [
    ":unicorn_face:",
    ":robot_face:",
    ":stuck_out_tongue_closed_eyes:",
    ":whale:",
    ":octopus:",
    ":earth_americas:",
    ":open_book:",
    ":deciduous_tree:",
    ":sign_of_the_horns:",
    ":blowfish:",
    ":frog:",
    ":hatched_chick:",
    ":floppy_disk:",
    ":truck:",
    ":balloon:",
    ":birthday:",
    ":dancers:",
    ":bento:",
    ":guitar:",
    ":airplane_departure:",
    ":grey_question:",
    ":world_map:",
    ":lion_face:",
    ":dog:",
    ":sunflower:",
    ":elephant:",
    ":poodle:",
    ":spider_web:",
    ":white_circle:",
    ":paw_prints:",
    ":fire:",
    ":two_women_holding_hands:",
    ":lion_face:",
]


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

            # Make sure we're in the help channel.
            if (latest.get("channel") == channel_id and
                latest.get("type") == "message"):

                # Was the latest update posted by a user, and was it in fact
                # a message?
                if latest.get("user"):
                    text = latest["text"]
                    print "Latest:", latest

                    respond_to_message(sc, text, channel_id)

                time.sleep(.5)


def respond_to_message(sc, text, channel_id):
    """Given a Slack client and text, decide how to respond to the message."""

    # If someone indicated the queue should be empty, then empty it.
    if text in QUEUE_EMPTY_MESSAGES:
        _QUEUE = []
        sc.rtm_send_message(channel_id, generate_queue_display())

    # Add a new student to the queue. Staff should still have to do
    # this manually.
    elif "queue.enqueue" in text.lower():

        # Use regex to find all user handles in the message, using Slack's
        # standard format for referring to users: <@the-user's-id> (the id
        # is *not* the user's handle).
        users_to_enqueue = re.findall(r"<@\w+>", text)

        _QUEUE.extend(users_to_enqueue)

        sc.rtm_send_message(
            channel_id,
            generate_queue_display()
        )

    # A staff member should still say "on my way" before
    # dequeuing, but they can dequeue instead of manually re-typing
    # the whole queue.

    elif "queue.dequeue" in text.lower():
        _QUEUE.pop(0)

        sc.rtm_send_message(
            channel_id,
            generate_queue_display()
        )

    # A user could be allowed to remove themselves.
    elif "queue.remove" in text.lower():
        user_to_remove = re.search(r"<@\w+>", text).group()
        _QUEUE.remove(user_to_remove)

        sc.rtm_send_message(
            channel_id,
            generate_queue_display()
        )

# FIXME: Subclass a queue class for _QUEUE and make this its __repr__ or __str__.
def generate_queue_display():
    """Decide what to show for the queue."""

    queue_template = "QUEUE = [{}]"

    # Check whether we should display students or silliness in QUEUE
    if _QUEUE != []:
        queue_display = queue_template.format(" ".join(_QUEUE))

    else:
        queue_display = queue_template.format(random.choice(EMOJIS))

    return queue_display


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
