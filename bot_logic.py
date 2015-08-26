from twython import Twython
import json
import os
import random


def auth():
    os.chdir('/home/fritz/Development/me/dontcarebot/')
    with open("access.json", 'r') as f:
        db = json.load(f)
    return Twython(db["API_Key"], db["API_Secret"], db["Access_Token"],
                   db["Access_Token_Secret"])


def load():
    with open("queue.json", 'r') as f:
        queue = json.load(f)
    with open("info.json", 'r') as fi:
        info = json.load(fi)
    return queue, info


def dump(queue, info):
    with open("queue.json", 'w') as f:
        json.dump(queue, f)
    with open("info.json", 'w') as fi:
        json.dump(info, fi)


def respond(twitter, top_tweet, reply=False):
    name = top_tweet["user"]["screen_name"]
    # twitter.create_friendship(screen_name=name)
    message_file = "messages.json" 
    if reply:
        message_file = "friendly_replies.json"
    with open(message_file, 'r') as f:
        messages = json.load(f)
    message = messages[random.randint(0, len(messages) - 1)]['message']
    twitter.update_status(status="@%s %s" % (name, message),
                          in_reply_to_status_id=top_tweet["id"])


def main():
    twitter = auth()
    queue, info = load()
    mentions = twitter.get_mentions_timeline()

    for mention in mentions:
        if not mention['favorited']:
            twitter.create_favorite(id=mention['id'])
            respond(twitter, mention, reply=True)

    tweets = twitter.search(q="tired sad", result_type="recent",
                            since_id=info["sinceid"], count='100')
    info["sinceid"] = tweets["search_metadata"]["max_id"]
    triggers = ("tired", "sad")
    to_add = [tweet for tweet in tweets["statuses"]
              if not tweet["retweeted"]
              and "retweeted_status" not in tweet]
    to_add = [tweet for tweet in to_add
              if triggers[0] in tweet["text"]
              or triggers[1] in tweet["text"]]
    queue = queue + to_add
    mx = max(len(to_add), 20)
    if len(queue) > mx:
        queue = queue[-mx:]
    if len(queue) > 0:
        respond(twitter, queue.pop())
    dump(queue, info)


# run on cron every minute
if __name__ == "__main__":
    main()
