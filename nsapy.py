from requests import post
from requests import Response
import requests
import json
from time import sleep

NUCONDRIA_URL = "https://nucondria.com/api/"
NSAOS_URL = NUCONDRIA_URL + "nsaos"

RESULT_ALIASES = {
    "Whitelist rule disallowed!":"The recipient has their whitelist enabled, and hasn't whitelisted you!"
}

def ping():
    try:
        response = post(NUCONDRIA_URL + "ping")
        return response.ok
    except:
        return False

def ratesafe_post(url,headers={},json={}):
    responded = False
    while not responded:
        response = post(url,headers=headers,json=json)
        if not response.status_code == 503:
            responded = True
        else:
            sleep(1)
    return response


class NSAOSClient():
    username = ""
    token = ""

    def create_account(self,username):
        response = ratesafe_post(NSAOS_URL,headers={
            "command":"Create-Auth",
            "username":username
        })
        if response.ok:
            userdetails = {"user":username,"token":response.text}
            self.username = userdetails["user"]
            self.token = userdetails["token"]
            return userdetails
        else:
            response.raise_for_status()

    def read_mail(self):
        return parse_mail_string(
            return_text_if_valid(
                ratesafe_post(NSAOS_URL,headers={
                    "command":"Read-Mail",
                    "username":self.username,
                    "auth-token":self.token
                }
            )
        ))

    def send_mail(self,title,content,recipient,finalize=True):
        response = ratesafe_post(NSAOS_URL,headers={
            "command":"Send-Mail",
            "username":self.username,
            "auth-token":self.token,
            "recipient":recipient
        },json={"content":content,"title":title,"finalize":finalize})
        return response

    def delete_mail(self,id):
        response = ratesafe_post(NSAOS_URL,headers={
            "command":"Delete-Mail",
            "username":self.username,
            "auth-token":self.token,
            "mail-uid":str(id)
        },json={"id":id})
        return response

    def get_politics(self):
        response = ratesafe_post(NSAOS_URL,headers={
            "command":"Get-Politics",
            "username":self.username,
            "auth-token":self.token
        })
        sections = response.text.split("")
        #put all sections into temporary variables for parsing
        tmpcandidates = sections[0].split("")
        elects = sections[1].split("")
        tmpglobals = sections[2].split("")
        tmpcouncil = sections[3].split("")
        tmpsuggestions = sections[4].split("")
        

        politics = {"elects":elects,"candidates":[],"globals":tmpglobals,"council":tmpcouncil,"suggestions":[]}
        for i in range(0,len(tmpcandidates)-1,2):
            candidate = Candidate()
            candidate.name = tmpcandidates[i]
            candidate.description = tmpcandidates[i+1].strip()
            politics["candidates"].append(candidate)
        for i in range(0,len(tmpsuggestions)):
            pass
        
        return politics

def return_text_if_valid(response:Response):
    response.raise_for_status()
    if response.text:
        return response.text
    else:
        return ""

class Suggestion():
    id = 0
    title = ""
    description = ""
    creator = ""
    infavor = [] #Users who are in favor of the change
    against = [] #Users who are against the change

class Candidate():
    name = ""
    description = ""

class Mail():
    author = ""
    title = ""
    content = ""
    id = 0
    finalized = True

def parse_mail_string(mailstring:str):
    splitstring = mailstring.split("")
    parsed = []
    for i in range(0,len(splitstring)-3,3):
        mail = Mail()
        mail.author = splitstring[i]

        mailjson = json.loads(splitstring[i+1])
        mail.content = mailjson.get("content","No content")
        mail.title = mailjson.get("title","Untitled")
        mail.finalized = mailjson.get("finalized",True)

        mail.id = int(splitstring[i+2])
        parsed.append(mail)
    
    return parsed