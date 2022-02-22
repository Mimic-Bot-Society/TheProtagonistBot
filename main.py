import os
import time
from random import randrange

import praw

reply_rate_limit_sleep = 5

general_rate_limit_sleep = 0.5


def read_file_contents(_file_name):
    file = open(_file_name, "r")
    file_contents = file.read()
    file.close()
    return file_contents


def get_quotes_list():
    return read_file_contents("quotes_list").split("\n")


def get_quote_dict():
    contents = read_file_contents("quotes_dict")
    lines = contents.split("\n")
    _quotes_dict = {}
    for line in lines:
        if line != "":
            key, value = line.split(":")
            _quotes_dict[key] = value
    return _quotes_dict


def get_random_quote():
    return quotes_list[randrange(0, len(quotes_list))]


def get_matched_quote(_comment_body):
    return next((tag for tag in quotes_dict.keys() if tag in _comment_body), None)


def handle_comment(_comment):
    replies = _comment.replies
    handle_single_comment(_comment)
    if len(replies) > 0:
        for comment_replay in replies:
            time.sleep(general_rate_limit_sleep)
            handle_comment(comment_replay)


def is_replying():
    return os.getenv("is_replying", False) == "True"


def get_allowed_subs():
    return os.getenv("allowed_subs", "")


def handle_single_comment(_single_comment):
    comment_body = _single_comment.body.lower()
    if "protagonist" in comment_body and _single_comment.author.name != "TheProtagonistBot":
        try:
            reply_body = get_reply_body(comment_body)
            print(f"Comment:\n####\n{comment_body}\n####\nReply draft:\n####\n{reply_body}")
            if is_replying() and _single_comment.subreddit.display_name in get_allowed_subs().split("+"):
                print(f"Replying to comment: {_single_comment.id}, Wait...")
                time.sleep(reply_rate_limit_sleep)
                _single_comment.reply(reply_body)
            else:
                print(f"Reply is forbidden in this subreddit: {_single_comment.subreddit.display_name}")
                print(f", Or replying is generally forbidden: {str(is_replying())}")
        except Exception as e:
            print(f"Failed to reply to comment: {str(e)}")
    else:
        print(f"Invalid comment: {_single_comment.id}")


def get_reply_body(comment_body):
    match = get_matched_quote(comment_body)
    if match is not None:
        reply_body = quotes_dict[match]
    else:
        reply_body = get_random_quote()
    return reply_body


quotes_list = get_quotes_list()
quotes_dict = get_quote_dict()

reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

tenet = reddit.subreddit(get_allowed_subs())

for comment in tenet.stream.comments():
    time.sleep(general_rate_limit_sleep)
    handle_comment(comment)
