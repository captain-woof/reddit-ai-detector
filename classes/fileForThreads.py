import threading

class FileForThreads:
    def __init__(self, filePath) -> None:
        self.lock = threading.Lock()
        self.filePath = filePath
        self.actualFile = None

    def openFileForReading(self):
        try:
            self.lock.acquire()
            if self.actualFile and (not self.actualFile.closed):
                self.actualFile.close()
            self.actualFile = open(self.filePath, "r")
            self.lock.release()
        except FileNotFoundError:
            self.lock.release()
            raise FileNotFoundError

    def openFileForWriting(self):
        try:
            self.lock.acquire()
            if self.actualFile and (not self.actualFile.closed):
                self.actualFile.close()
            self.actualFile = open(self.filePath, "a")
            self.lock.release()
        except FileNotFoundError:
            self.lock.release()
            raise FileNotFoundError

    def closeFile(self):
        self.lock.acquire()
        self.actualFile.close()
        self.lock.release()

    def writeLine(self, line: str):
        self.lock.acquire()
        self.actualFile.write(line.rstrip("\n") + "\n")
        self.lock.release()

    def readline(self):
        self.lock.acquire()
        line = self.actualFile.readline()
        self.lock.release()
        return line
    
    def readlines(self):
        self.lock.acquire()
        lines = self.actualFile.readlines()
        self.lock.release()
        return lines
        