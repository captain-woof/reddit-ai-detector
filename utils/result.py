"""
Scoring scheme
0% -> Not LLM
0-25% -> Few LLM
25-50% -> Some LLM
50-75% -> A lot LLM
75% -> 100% -> Mostly LLM
100% -> Fully LLM
"""

message1 = """
# AI-generated text detection result

**This post does not contain AI-generated texts.**

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts.

*If you think this result is a mistake, or have suggestions, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""

message2 = """
# AI-generated text detection result

**This post contains a few AI-generated texts (between 1% - 25%).** The AI-generated texts are:
{0}

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts.

*If you think this result is a mistake, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""

message3 = """
# AI-generated text detection result

**This post contains some AI-generated texts (between 26% - 50%).** The AI-generated texts are:
{0}

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts.

*If you think this result is a mistake, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""

message4 = """
# AI-generated text detection result

**This post contains a lot of AI-generated texts (between 51% - 75%).** The AI-generated texts are:
{0}

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts. In addition, I downvote posts like these, with a high percentage of fake texts, on behalf of my creator.

*If you think this result is a mistake, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""

message5 = """
# AI-generated text detection result

**This post contains mostly AI-generated texts (between 76% - 99%).** The AI-generated texts are:
{0}

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts. In addition, I downvote posts like these, with a high percentage of fake texts, on behalf of my creator.

*If you think this result is a mistake, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""

message6 = """
# AI-generated text detection result

**This post is entirely AI-generated.** The AI-generated texts are:
{0}

LLMs like ChatGPT can generate texts in mass quantities, which can be very elaborate and convincing - almost human-like. This is often used by scammers nowadays to fool people into believing that they are interacting with a real person. This escalates into all sorts of scams, including financial, identity, and much more.

I was created to check some vulnerable subreddits for such posts, and alert other redditors if I see LLM-generated posts. In addition, I downvote posts like these, with a high percentage of fake texts, on behalf of my creator.

*If you think this result is a mistake, please DM me.*

Bot author: [@realCaptainWoof](https://x.com/realCaptainWoof) | Powered by [ZeroGPT](https://www.zerogpt.com/)
"""


def getResultText(detectionResult):
    message = ""
    messageFormatted = ""
    # Get message template from AI percentage
    aiPercentage = detectionResult["aiPercentage"]
    if aiPercentage == 0:
        message = message1
    elif aiPercentage > 0 and aiPercentage <= 25:
        message = message2
    elif aiPercentage > 25 and aiPercentage <= 50:
        message = message3
    elif aiPercentage > 50 and aiPercentage <= 75:
        message = message4
    elif aiPercentage > 75 and aiPercentage < 100:
        message = message5
    elif aiPercentage == 100:
        message = message6

    # Insert list of detected AI texts in message
    aiSentences = detectionResult["aiSentences"]
    aiSentencesMessage = "\n".join(["- {0}".format(aiSentence) for aiSentence in aiSentences])
    messageFormatted = message.format(aiSentencesMessage)

    # Return message
    return messageFormatted