import praw
from requests import Session
import os
import json
from praw.models import Subreddit, ListingGenerator, MoreComments
from utils.logger import logWithTimestamp
import threading
from classes.listForThreads import ListForThreads
from utils.zerogpt import detectText
from utils.result import getResultText
from classes.countForThreads import CountForThreads
import time
import random
from classes.setForThreads import SetForThreads

class RedditBot:
    reddit: praw.Reddit
    subredditsToMonitor: list
    numPostsToCheckPerSubreddit: int
    userAgent: str
    postsToCheck: list
    postsDetected: ListForThreads
    maxThreads: int
    maxCharsPerPost: int
    postsCheckedCount: CountForThreads
    interval: int
    postIdsChecked: SetForThreads
    aiThresholdForDetection: int

    def __init__(self) -> None:
        # Post IDs checked
        self.postIdsChecked = SetForThreads()

        # Number of posts checked
        self.postsCheckedCount = CountForThreads()

        # List of posts to check and detect
        self.postsToCheck = []
        self.postsDetected = ListForThreads()

        # Load config
        with open("config.json", "r") as configFile:
            config = json.loads(configFile.read())

            # Minimum percentage of AI-generated text to be considered for reporting
            self.aiThresholdForDetection = config["aiThresholdForDetection"]

            # Subreddits to monitor
            self.subredditsToMonitor = config["subredditsToMonitor"]

            # Number of posts to check per cycle
            self.numPostsToCheckPerSubreddit = config["numPostsToCheckPerSubreddit"]

            # User-Agent to send in HTTP(s) requests
            self.userAgentReddit = config["userAgentReddit"]
            self.userAgentZerogpt = config["userAgentZerogpt"]

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
            user_agent=self.userAgentReddit,
            username=os.environ["REDDIT_USERNAME"],
        )

    # Sends a post to a subreddit
    def __postToSubreddit(self, subredditName, postTitle, postBodyText):
        subreddit = self.reddit.subreddit(subredditName)
        subreddit.submit(title=postTitle, selftext=postBodyText)

    # Get posts from a subreddit
    def __getPostsFromSubreddit(self, subredditName, limit):
        subreddit: Subreddit = self.reddit.subreddit(subredditName)
        
        posts: ListingGenerator = subreddit.new(limit=limit)
        return posts
    
    # Comments on a post
    def __commentOnPost(self, post, replyText):
        post.reply(replyText)

    # Checks if bot has already processed post
    def __isPostCommentedOnAlready(self, post):
        for comment in post.comments:
            if isinstance(comment, MoreComments) or comment.author == os.environ["REDDIT_USERNAME"]:
                return True
        return False
    
    # Filters a list of posts for posts that need to be checked
    def __filterPostsThread(self, posts, postsFiltered):
        for post in posts:
            # If post is already processed (present in local set), skip
            if self.postIdsChecked.isValExists(post.id):
                continue
            # If post has text, and is not already commented on
            if (len(post.selftext) > 0) and (not self.__isPostCommentedOnAlready(post)):
                postsFiltered.append(post)
    
    # Gets all posts from all configured subreddits to check
    def __preparePostsFromSubredditsToCheck(self):        
        # Get and merge posts by each subreddit
        for subredditName in self.subredditsToMonitor:
            logWithTimestamp("Checking r/{0}".format(subredditName))

            # Collect all posts
            postsToCheckInSubreddit = self.__getPostsFromSubreddit(subredditName=subredditName,limit=self.numPostsToCheckPerSubreddit)

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
            # Add post ID to checked set
            self.postIdsChecked.add(post.id)

            # Get body text of post
            postText = post.selftext

            # If post has text body, then detect
            if len(postText) > 0:
                # Perform detection
                detectionResult = detectText(text = postText[0:self.maxCharsPerPost], userAgent = self.userAgentZerogpt)

                # If detection is successful, post result in comment
                if detectionResult["success"]:
                    # If AI-generated text is found
                    if (detectionResult["aiPercentage"] >= self.aiThresholdForDetection):
                        # Send result to results commenting thread
                        self.postsDetected.append({
                            "post": post,
                            "detectionResult": detectionResult
                        })
                    # Increment posts checked stat
                    self.postsCheckedCount.inc()
                else:
                    logWithTimestamp("Detection failed for \"{0}\"".format(post.url))
                    print(detectionResult)
    
    # Check all gathered posts
    def __checkPosts(self):
        logWithTimestamp("Checking {0} posts in all {1} configured subreddits".format(len(self.postsToCheck), len(self.subredditsToMonitor)))

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
            logWithTimestamp("Total {0} posts checked in all {1} configured subreddits; {2} AI-generated posts detected".format(self.postsCheckedCount.getCount(), len(self.subredditsToMonitor), len(self.postsDetected)))

    # Function for commenting detection results
    def __startCommentingOnDetectedPostsThread(self):
        while True:
            try:
                # Read result from list if available
                result = self.postsDetected.pop()
                post = result["post"]
                detectionResult = result["detectionResult"]

                # Post result in comment if possible and AI generated text was found
                if not post.locked:
                    commentToPost = getResultText(detectionResult)
                    self.__commentOnPost(post, commentToPost)
                    logWithTimestamp("AI-generated post reported: {0}".format(post.url))

                # Downvote post if necessary
                if detectionResult["aiPercentage"] >= 75:
                    post.downvote()
            except IndexError:
                pass
            except Exception as e:
                logWithTimestamp(e)
            finally:
                # Sleep before going over the loop again
                time.sleep(random.randint(50,70))

    # Function to start commenting detection results
    def __startCommentingOnDetectedPosts(self):
        thread = threading.Thread(
            target=self.__startCommentingOnDetectedPostsThread
        )
        thread.start()

    # Cleanup for new cycle
    def __doCleanup(self):
        self.postsToCheck.clear()
        self.postsCheckedCount.reset()
        self.postsDetected.clear()

    # Performs checking once
    def __performCheckOnce(self):
        self.__doCleanup()
        self.__preparePostsFromSubredditsToCheck()
        self.__checkPosts()
        self.__startCommentingOnDetectedPosts()

    # Performs checks in loop
    def startCheckLoop(self):
        while True:
            try:
                self.__performCheckOnce()
            except Exception as e:
                print(e)
            finally:
                logWithTimestamp("Will sleep for {0} seconds".format(self.interval))
                time.sleep(self.interval)