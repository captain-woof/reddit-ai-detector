import requests
import json

"""
POST https://api.zerogpt.com/api/detect/detectText
{"input_text":"sample text"}

{"success":true,"code":200,"message":"detection result passed to proxy","data":{"sentences":[],"isHuman":100,"additional_feedback":"Please input more text for a more accurate result","h":[],"hi":[],"textWords":2,"aiWords":0,"fakePercentage":0.0,"specialIndexes":[],"specialSentences":[],"originalParagraph":"sample text","feedback":"Your Text is Human Written","input_text":"sample text","detected_language":"en"}}
"""

def __makePostRequest(url,dataJson,userAgent):
    return requests.post(
        allow_redirects=True,
        json=dataJson,
        url=url,
        headers={
            "User-Agent": userAgent,
            "Origin": "https://www.zerogpt.com",
            "Referer": "https://www.zerogpt.com"
        }
    )

def detectText(text, userAgent):
    resp = None
    try:
        resp = __makePostRequest(
            url="https://api.zerogpt.com/api/detect/detectText",
            dataJson={
                "input_text": text
            },
            userAgent=userAgent
        )

        if not resp.ok:
            raise Exception

        respProcessed = resp.json()
        return {
            "success": respProcessed["success"],
            "aiSentences": respProcessed["data"]["h"],
            "textWords": respProcessed["data"]["textWords"],
            "aiWords": respProcessed["data"]["aiWords"],
            "humanPercentage": respProcessed["data"]["isHuman"],
            "aiPercentage": respProcessed["data"]["fakePercentage"],
            "feedback": respProcessed["data"]["feedback"],
            "originalParagraph": respProcessed["data"]["originalParagraph"]
        }
    except json.JSONDecodeError:
        return {
            "success": False
        }
    except Exception as e:
        print("Detection failed for text: '{0}'".format(text))
        print(resp)
        return {
            "success": False
        }