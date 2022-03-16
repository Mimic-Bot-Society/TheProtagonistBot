# tenet_bot

[![Reddit User Karma](https://img.shields.io/reddit/user-karma/combined/TheProtagonistBot?style=social)](https://reddit.com/user/TheProtagonistBot)

Simple replay bot for the Protagonist character of Tenet by Christopher Nolan.

Reddit's user for the bot is [u/TheProtagonistBot](https://www.reddit.com/user/TheProtagonistBot/).

Bot is mainly active in the [![Subreddit subscribers](https://img.shields.io/reddit/subreddit-subscribers/tenet?style=social)](https://www.reddit.com/r/tenet)
subreddit.

Currently, bot is powered using
python **3.9.1** and the **[praw](https://praw.readthedocs.io/en/latest/)** library which is running in a free tier
heroku dyno.

The bot use two types of quotes, [one](https://github.com/yamin8000/tenet_bot/blob/master/quotes_dict)
is called a dictionary where if certail trigger words are in the original comment then a relevant quote is replied
[other one](https://github.com/yamin8000/tenet_bot/blob/master/quotes_list)
is just a list of quotes that if trigger words are not found then a random comment is replied.
