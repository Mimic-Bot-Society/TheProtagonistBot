import os
import random
import threading
import time
import re
from random import randrange

import praw
from colorama import init, Fore, Style
from praw.exceptions import RedditAPIException

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
    handle_single_comment(_comment, 0)
    if len(replies) > 0:
        for comment_replay in replies:
            time.sleep(general_rate_limit_sleep)
            handle_comment(comment_replay)


def is_replying():
    return os.getenv("is_replying", False) == "True"


def get_allowed_subs():
    return os.getenv("allowed_subs", "test")


def get_trigger_word():
    return os.getenv("trigger_word", "protagonist")


def get_bot_username():
    return os.getenv("username", "TheProtagonistBot")


def handle_rate_limit_exception(_message, _comment):
    if "Take a break" in _message:
        p_seconds = re.compile(r"\d+ seconds", re.IGNORECASE)
        p_minutes = re.compile(r"\d+ minutes", re.IGNORECASE)

        seconds_match = p_seconds.findall(_message)
        minutes_match = p_minutes.findall(_message)

        if len(seconds_match) > 0:
            seconds = int(seconds_match[0].replace("seconds", "").strip())
        elif len(minutes_match) > 0:
            seconds = int(minutes_match[0].replace("minutes", "").strip()) * 60
        else:
            seconds = 600
        seconds += random.randint(10, 30)

        print(f"Rate limit exception, sleeping for {seconds} seconds then retrying!")
        thread = threading.Thread(target=handle_single_comment, args=(_comment, seconds,))
        thread.start()


def handle_single_comment(_single_comment, _sleep):
    if _sleep != 0:
        time.sleep(_sleep)

    comment_body = _single_comment.body.lower()
    if get_trigger_word() in comment_body and _single_comment.author.name != get_bot_username():
        try:
            reply_body = get_reply_body(comment_body)
            sub_name = _single_comment.subreddit.display_name
            print(f"{Fore.GREEN}Comment:")
            print(f"{Fore.YELLOW}###")
            print(f"{Fore.BLUE}{comment_body}")
            print(f"{Fore.YELLOW}###")
            print(f"{Fore.GREEN}Reply:")
            print(f"{Fore.BLUE}{reply_body}")
            if is_replying() and sub_name in get_allowed_subs().split("+"):
                print(f"Replying to comment: {_single_comment.id}, Wait...{Style.RESET_ALL}")
                time.sleep(random.randint(1, reply_rate_limit_sleep))
                _single_comment.reply(reply_body)
                print(f"{Fore.GREEN}Replied to comment.")
            else:
                print(f"{Fore.RED}Reply is forbidden in this subreddit: {Fore.CYAN}{sub_name}{Style.RESET_ALL}")
                print(f"{Fore.RED}, Or replying is generally forbidden:{Style.RESET_ALL}", end='')
                print(f"{Fore.CYAN} {is_replying()}{Style.RESET_ALL}")
        except RedditAPIException as reddit_api_exception:
            message = reddit_api_exception.args[0].message
            print(f"{Fore.RED}Reddit API Exception: {Fore.CYAN}{message}{Style.RESET_ALL}")
            handle_rate_limit_exception(message, _single_comment)
        except Exception as e:
            print(f"{Fore.RED}Failed to reply to comment: {Fore.CYAN}{str(e)}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Invalid comment: {Fore.CYAN}{_single_comment.id}{Style.RESET_ALL}")


def get_reply_body(comment_body):
    match = get_matched_quote(comment_body)
    if match is not None:
        reply_body = quotes_dict[match]
    else:
        reply_body = get_random_quote()
    return reply_body


init()

print(f"{Fore.YELLOW}Starting bot...")
print(f"Trigger word: {Fore.GREEN}{get_trigger_word()}")

print(f"{Fore.YELLOW}Getting quotes...")
quotes_list = get_quotes_list()
quotes_dict = get_quote_dict()

print(f"{Fore.YELLOW}Getting reddit instance... for user: {Fore.GREEN}{get_bot_username()}")
reddit = praw.Reddit(
    client_id=os.getenv("client_id"),
    client_secret=os.getenv("client_secret"),
    user_agent=os.getenv("user_agent"),
    username=os.getenv("username"),
    password=os.getenv("password")
)

print(f"{Fore.YELLOW}Getting subreddits...")
subs = reddit.subreddit(get_allowed_subs())

print(f"{Fore.YELLOW}Getting comments...{Style.RESET_ALL}")
for comment in subs.stream.comments():
    time.sleep(general_rate_limit_sleep)
    handle_comment(comment)
