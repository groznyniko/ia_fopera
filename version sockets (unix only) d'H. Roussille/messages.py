import json

class JsonSerializable(object):

    def toJson(self):
        return json.dumps(self.__dict__).encode('ascii')

    def __repr__(self):
        return self.toJson()

class Message(JsonSerializable):

    def __init__(self, type, content):
        self.type = type
        self.content = str(content)

class Information(Message):
    
    def __init__(self, content):
        super(Information, self).__init__("Information", content)

class Question(Message):
        
    def __init__(self, content):
        super(Question, self).__init__("Question", content)

class Response(Message):
    
    def __init__(self, content):
        super(Response, self).__init__("Response", content)

def deserialize(string):
    j = json.loads(string.decode('ascii'))

    if j["type"] == "Information":
        return Information(j["content"])

    elif j["type"] == "Question":
        return Question(j["content"])

    elif j["type"] == "Response":
        return Response(j["content"])

    return None


