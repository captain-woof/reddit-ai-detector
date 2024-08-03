import time

def logWithTimestamp(text: str):
    timeCurr = time.strftime("%Y-%m-%d | %I:%M:%S %p")
    print("{0} > {1}".format(timeCurr, text))