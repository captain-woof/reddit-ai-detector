import praw
from requests import Session
import os
import json
from praw.models import Subreddit, ListingGenerator
from utils.logger import logWithTimestamp
import threading
from classes.listForThreads import ListForThreads
from utils.zerogpt import detectText
from utils.result import getResultText
from classes.countForThreads import CountForThreads
import time

class RedditBot:
    reddit: praw.Reddit
    subredditsToMonitor: list
    numPostsToCheckPerCycle: int
    userAgent: str
    postsToCheck: list
    maxThreads: int
    maxCharsPerPost: int
    postsCheckedCount: CountForThreads
    postsDetectedCount: CountForThreads
    interval: int

    def __init__(self) -> None:
        # Number of posts checked
        self.postsCheckedCount = CountForThreads()

        # Number of AI generated posts found
        self.postsDetectedCount = CountForThreads()

        # List of posts to check
        self.postsToCheck = []

        # Load config
        with open("config.json", "r") as configFile:
            config = json.loads(configFile.read())

            # Subreddits to monitor
            self.subredditsToMonitor = config["subredditsToMonitor"]

            # Number of posts to check per cycle
            self.numPostsToCheckPerCycle = config["numPostsToCheckPerCycle"]

            # User-Agent to send in HTTP(s) requests
            self.userAgent = config["userAgent"]

            # Maximum threads
            self.maxThreads = config["maxThreads"]

            # Maximum characters per post
            self.maxCharsPerPost = config["maxCharsPerPost"]

            # Sleep interval between checks
            self.interval = config["interval"]

        # Setup PRAW
        session = Session()
        self.reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            password=os.environ["REDDIT_PASSWORD"],
            requestor_kwargs={"session": session},
            user_agent=self.userAgent,
            username=os.environ["REDDIT_USERNAME"],
        )

    # Sends a post to a subreddit
    def __postToSubreddit(self, subredditName, postTitle, postBodyText):
        subreddit = self.reddit.subreddit(subredditName)
        subreddit.submit(title=postTitle, selftext=postBodyText)

    # Get posts from a subreddit
    def __getPostsFromSubreddit(self, subredditName, limit, type):
        subreddit: Subreddit = self.reddit.subreddit(subredditName)
        
        posts: ListingGenerator = None
        if type == "top":
            posts = subreddit.top(limit=limit)
        elif type == "hot":
            posts = subreddit.hot(limit=limit)
        else:
            posts = subreddit.new(limit=limit)
        return posts
    
    # Comments on a post
    def __commentOnPost(self, post, replyText):
        post.reply(replyText)

    # Checks if bot has already processed post
    def __isPostCheckedAlready(self, post):
        for comment in post.comments:
            if comment.author == os.environ["REDDIT_USERNAME"]:
                return True
        return False
    
    # Filters a list of posts for posts that need to be checked
    def __filterPostsThread(self, posts, postsFiltered):
        for post in posts:
                # If post has text, and is not already commented on
                if (len(post.selftext) > 0) and (not self.__isPostCheckedAlready(post)):
                    postsFiltered.append(post)
    
    # Gets all posts from all configured subreddits to check
    def __preparePostsFromSubredditsToCheck(self, type):
        # Clear master list of posts to check
        self.postsToCheck.clear()

        # Get and merge posts by each subreddit
        for subredditName in self.subredditsToMonitor:
            logWithTimestamp("Checking r/{0}".format(subredditName))

            # Collect all posts
            postsToCheckInSubreddit = self.__getPostsFromSubreddit(subredditName=subredditName,limit=self.numPostsToCheckPerCycle,type=type)

            # Split posts for each thread 
            postsForEachThread = [[] for _ in range(0,self.maxThreads)]
            for i,post in enumerate(postsToCheckInSubreddit):
                (postsForEachThread[i % self.maxThreads]).append(post)

            # Filter posts using threads
            postsToCheckInSubredditFiltered = ListForThreads()

            threads = [threading.Thread(
                target=self.__filterPostsThread,
                kwargs={"posts": postsForEachThread[threadIndex], "postsFiltered": postsToCheckInSubredditFiltered}
            ) for threadIndex in range(0,self.maxThreads)]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # Add posts to master list of posts to check
            self.postsToCheck.extend(list(postsToCheckInSubredditFiltered))

            # Log stats
            logWithTimestamp("Total {0} posts to check in r/{1}".format(len(postsToCheckInSubredditFiltered), subredditName))

        # Log stats
        logWithTimestamp("Total {0} posts to check in all {1} configured subreddits".format(len(self.postsToCheck), len(self.subredditsToMonitor)))
    
    # Check all gathered posts for thread
    def __checkPostsThread(self, posts):
        for post in posts:
            postText = post.selftext

            # If post has text body, then detect
            if len(postText) > 0:
                detectionResult = detectText(text = post.selftext[0:self.maxCharsPerPost], userAgent = self.userAgent)

                # If detection is successful, post result in comment
                if detectionResult["success"]:
                    # Downvote post if necessary
                    if detectionResult["aiPercentage"] > 50:
                        post.downvote()

                    # Post result in comment if possible and AI generated text was found
                    if (detectionResult["aiPercentage"] > 0) and (not post.locked):
                        commentToPost = getResultText(detectionResult)
                        self.__commentOnPost(post, commentToPost)
                        self.postsDetectedCount.inc()
                    # Increment posts checked stat
                    self.postsCheckedCount.inc()
                else:
                    logWithTimestamp("Detection failed for \"{0}\"".format(post.url))
                    print(detectionResult)
    
    # Check all gathered posts
    def __checkPosts(self):
        if len(self.postsToCheck) != 0:
            # Split posts for each thread
            postsForEachThread = [[] for _ in range(0,self.maxThreads)]
            for i,post in enumerate(self.postsToCheck):
                (postsForEachThread[i % self.maxThreads]).append(post)

            # Create and start threads
            threads = [threading.Thread(
                target=self.__checkPostsThread,
                kwargs={"posts": postsForEachThread[threadIndex]}
            ) for threadIndex in range(0,self.maxThreads)]

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # Print stats
            logWithTimestamp("Total {0} posts checked in all {1} configured subreddits; {2} AI-generated posts detected".format(self.postsCheckedCount.getCount(), len(self.subredditsToMonitor), self.postsDetectedCount.getCount()))

    # Performs checking once
    def performCheckOnce(self):
        self.postsCheckedCount.reset()
        self.postsDetectedCount.reset()
        self.__preparePostsFromSubredditsToCheck(type="new")
        self.__checkPosts()

    # Sleep
    def sleep(self):
        logWithTimestamp("Sleeping for {0} seconds".format(self.interval))
        time.sleep(self.interval) 

    # Performs checks in loop
    def startCheckLoop(self):
        while True:
            try:
                self.performCheckOnce()
            except Exception as e:
                print(e)
            finally:
                self.sleep()