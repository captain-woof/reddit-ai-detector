from classes.reddit import RedditBot
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load env vars
    load_dotenv()

    # Start reddit bot
    redditBot = RedditBot()
    redditBot.performCheckOnce()