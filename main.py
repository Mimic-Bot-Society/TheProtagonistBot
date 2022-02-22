import praw
import time
import os

from random import randrange

from praw.exceptions import RedditAPIException


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
            handle_comment(comment_replay)


def is_replying():
    return bool(os.getenv("is_replying", False))


def get_allowed_subs():
    return os.getenv("allowed_subs", "").split(",")


def handle_single_comment(_single_comment):
    comment_body = _single_comment.body.lower()
    if "protagonist" in comment_body and _single_comment.author.name != "TheProtagonistBot":
        try:
            match = get_matched_quote(comment_body)
            if match is not None:
                reply_body = quotes_dict[match]
            else:
                reply_body = get_random_quote()
            print("Comment:\n####\n" + comment_body + "\n####\nReply:\n####\n" + reply_body)
            if is_replying() and _single_comment.subreddit.name in get_allowed_subs():
                _single_comment.reply(reply_body)
        except Exception as e:
            print("Failed to reply to comment: " + str(e))
    else:
        print("Invalid comment: " + _single_comment.id)


quotes_list = get_quotes_list()
quotes_dict = get_quote_dict()

reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

tenet = reddit.subreddit("tenet+test")

for comment in tenet.stream.comments():
    time.sleep(0.1)
    handle_comment(comment)
