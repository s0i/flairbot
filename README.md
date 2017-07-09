# What does the bot do?

This bot does a few things for your subreddit:

- Automatically removes posts with no flair that are older than X minutes (default is 10, can be adjusted in wiki, more details below)

- Leaves a comment explaining why the post was removed and allows mobile users to use a command to flair their posts
	- The commands and flair options are auto-generated from data about your subreddit. No setup required!

- Automatically approves posts after a flair is added to them (for up to 72 hours)! The bot also deletes its comment in the thread, and
commands used by mobile users.


**Note that moderators are exempt by default to avoid confusion. If you want to test the bot out, you will have to do so on an alt.**

# How do I set it up?

To set it up, all you have to do is run the code and invite the bot to your subreddit with the following permissions: wiki, posts, and flairs. The wiki permission is so that it can set up a page at http://www.reddit.com/r/yoursubreddithere/wiki/FlairTimeBot where you can adjust settings such as how long before posts are removed and how long users have to reflair posts that are removed.
After inviting the bot, it's important that you check modmail where it will reply with information about the setup and an error report if anything went wrong.

# Note to developers 

The code is configured to run on the now-deleted account /u/FlairTimeBot. If you want to run it yourself, you will have to go through the code and replace instances of the bot's name with your the name of your own bot. I am hoping to make the code more general soon, but it is not currently a priority.