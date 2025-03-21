import nsapy
import os
import pathlib
from json import loads as parse_json
import json
from requests import Response
from tqdm import tqdm
from datetime import datetime
import platform
import tempfile
import subprocess
import requests

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
colorama_init()

RESULT_ALIASES = {
    "Rule exists already":f"{Fore.RED}You already have that user whitelisted!{Style.RESET_ALL}",
    "Whitelist rule disallowed!":f"{Fore.RED}You aren't whitelisted! {Style.DIM}(or the user doesn't exist){Style.RESET_ALL}",
    "User Already Exists":f"{Fore.RED}That username is taken, try another{Style.RESET_ALL}"
}

knownplayers = []

client = nsapy.NSAOSClient()

script_dir = pathlib.Path(__file__).parent

def print_list(options):
    for i in range(0,len(options)):
        print(f"{Style.DIM}{i+1}{Style.RESET_ALL} {options[i]}")

def sign_in(forcesignout=False):
    if forcesignout:
        os.remove(script_dir / "currentuser.txt")
    
    try:
        with open(script_dir / "currentuser.txt","r") as f:
            content = f.read()
        
        userdata = parse_json(content)
        client.username = userdata["user"]
        client.token = userdata["token"]
        return
    except:
        pass

    print("Welcome! Please sign in")
    print(f"{Style.DIM}NOTE: If you want to use your account from GMOD, view readme.md for info on how to import it{Style.RESET_ALL}")
    userfiles = os.listdir(script_dir / "users")
    users = []
    for user in userfiles:
        with open(script_dir / "users" / user,"r") as f:
            content = f.read()
        userdata = parse_json(content)
        users.append(userdata)
    
    choices = []
    for user in users:
        choices.append(user["user"])
    choices.append("Create new user")
    print_list(choices)

    selection = int(input("Select a user: "))
    if selection > len(users):
        try:
            userdetails = client.create_account(input("What username do you want?"))
            with open(script_dir / "users" / (userdetails["user"] + ".txt"), "w") as f:
                json.dump(userdetails, f)
            with open(script_dir / "currentuser.txt", "w") as f:
                json.dump(userdetails,f)
            print(f"{Fore.GREEN}Account created!{Style.RESET_ALL}")
        except requests.HTTPError as e:
            return_action_result(e.response)
    else:
        client.username = users[selection-1]["user"]
        client.token = users[selection-1]["token"]
        with open(script_dir / "currentuser.txt","w") as f:
            json.dump(users[selection-1],f)
        discover_player(client.username)

def main_menu():
    while True:
        print(f"-- nsaos python client -- {Fore.BLUE}{client.username}{Style.RESET_ALL} --")
        print_list(["Inbox","Send","Politics","Whitelist","Sort mail (Requires GMOD)","Other...","Sign out"])
        
        match input("Select an option: "):
            case "1":
                view_inbox()
            case "2":
                send_mail()
            case "3":
                politics_menu()
            case "5":
                sort_mail()
            case "6":
                other_menu()
            case "7":
                sign_in(True) # Force a signout, even if a cached user is available

def politics_menu():
    print("Getting politics...")
    politics = client.get_politics()
    print(f"{Fore.CYAN}Candidates{Style.RESET_ALL}")
    for candidate in politics["candidates"]:
        discover_player(candidate.name)
        print(candidate.name)
        print(f"{Style.DIM}{candidate.description}{Style.RESET_ALL}")


def other_menu():
    print_list(["Delete all mail","Whitelist all","Clear whitelist","View known players","Back"])
    match input("Select an option: "):
        case "1":
            if not input("Are you sure? ").startswith("y"):
                return
            
            print("Getting mail...")
            inbox = client.read_mail()
            if len(inbox) == 0:
                print("Your inbox is already empty!")
                return
            
            results = []
            for mail in tqdm(inbox):
                results.append(return_action_result(client.delete_mail(mail.id)))
            
            print_list(results)

        case "4":
            print_list(knownplayers)
            input("Press enter to continue")
        case "5":
            return

def sort_mail():
    print(f"Where is your mailassoc.txt file? {Style.DIM}(it should be in the same folder as your user.txt file){Style.RESET_ALL}")
    assocpath = input("File path: ")
    try:
        if os.path.isdir(assocpath):
            print(f"{Style.DIM}Provided path is a directory, searching for mailassoc.txt in this path{Style.RESET_ALL}")
            assocpath += "mailassoc.txt"
        with open(assocpath,"r") as f:
            mailassoc = json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}File not found, aborting{Style.RESET_ALL}")
        return
    except json.JSONDecodeError:
        print(f"{Fore.RED}Your mailassoc file is corrupted, aborting{Style.RESET_ALL}")
        return
    
    print("Which sorting method would you like to use? You can decide if mail that is already sorted gets its folder overwritten or not")
    print_list(["Put mail in author folders","Put mail in today's folder","Put mail in custom folder"])
    method = input("Sorting method:")
    sortingfunction = None
    match method:
        case "1":
            print("Sorting mail into folders based on the author")
            sortingfunction = lambda mail : mail.author
        case "2":
            print("Putting mail into a folder based on the *current* time, not the time the mail was sent")
            print("This is meant to be used every day so you can try and estimate the time the mail was sent")
            print(f"{Fore.RED}NOT RECOMMENDED WHEN OVERWRITING SORTED MAIL{Style.RESET_ALL}")
            date = datetime.now()
            currenttime = date.strftime("%B %d, %Y")
            sortingfunction = lambda mail : currenttime
        case "3":
            foldername = input("Folder name: ")
            sortingfunction = lambda mail : foldername
    
    overwrite = input("Overwrite folders of mail that already has one?").startswith("y")

    print("Fetching mail...")
    results = []
    untouched = 0
    for mail in tqdm(client.read_mail()):
        # third condition won't execute if mail.id isn't in mailassoc, so it wont fail
        if (not overwrite) and (mailassoc.get(str(mail.id),"inbox") != "inbox"):
            untouched += 1
            continue

        foldername = sortingfunction(mail)
        results.append(f"{mail.title} moved to {foldername} from {mailassoc.get(str(mail.id),'inbox')}")
        mailassoc[str(mail.id)] = foldername
    
    with open(assocpath,"w") as f:
        json.dump(mailassoc,f)

    print_list(results)
    if untouched > 0:
        print(f"{Style.DIM}{untouched} messages were not sorted{Style.RESET_ALL}")

def view_inbox():
    print(f"{Style.DIM}Reading inbox, please wait...{Style.RESET_ALL}")
    inbox = client.read_mail()
    print("\n\n\n")
    index = 0
    for mail in inbox:
        index += 1
        print(f"""#{index} {Fore.CYAN}{mail.title}{Style.RESET_ALL}
by {Fore.BLUE}{mail.author}{Style.RESET_ALL}
{Style.DIM}-- BEGIN MESSAGE ----------------------------------------------{Style.RESET_ALL}
{mail.content}
{Style.DIM}-- END MESSAGE ------------------------------------------------{Style.RESET_ALL}
""")
        discover_player(mail.author)
    
    print_list(["Delete","Forward","Back"])
    match input("Select an option: "):
        case "1":
            mailindex = int(input("Enter mail number: ")) - 1
            try:
                selectedmail = inbox[mailindex]
            except IndexError:
                print("Invalid mail, try again")
                return
            
            print(return_action_result(client.delete_mail(selectedmail.id)))
        case "2":
            mailindex = int(input("Enter mail number: ")) - 1
            try:
                selectedmail = inbox[mailindex]
                title = selectedmail.title
                content = selectedmail.content
                author = selectedmail.author

            except IndexError:
                print("Invalid mail, try again")
                return

            print_list(["Add all forwarding info","Add fwd: to title only","Don't change anything"])
            match input("Forwarding method: "):
                case "1":
                    title = f"FWD: {title}"
                    content = f"Forwarded message\nFrom: {author}\nTo: {client.username}\n---------------------------------\n{content}"
                case "2":
                    title = f"FWD: {title}"
            
            select_sending_method(title,content)
                    


def send_mail():
    title = input("Enter the title: ")
    content = get_long_input("Write your message here, then save and quit")
    select_sending_method(title,content)
    

def select_sending_method(title,content):
    print("How should you send this message?")
    print_list(["Regular send","Send to multiple recipients","Send to all known players","Spam to players","Abort"])

    while True:
        match input("What method should be used to send: "):
            case "1":
                recipient = input("Enter the recipient: ")
                print(return_action_result(client.send_mail(title,content,recipient)))
                return
            case "2":
                recipients = get_long_input("Enter list of recipients then save and quit").strip().split("\n")
                mass_send(title,content,recipients)
                return
                
            case "3":
                mass_send(title,content,knownplayers)
                return
            case "4":
                recipients = get_long_input("Enter list of recipient(s) then save and quit").strip().split("\n")
                for i in range(0,int(input("Spam count: "))):
                    mass_send(title,content,recipients)
                return
            case "5":
                print("Not sending message")
                return
            case _:
                print("Invalid selection")


def get_long_input(placeholder="Save and close this file once you're finished"):
    tempfilepath = ""
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmpfile:
        tmpfile.write(placeholder.encode())
        tempfilepath = tmpfile.name
    
    if platform.system() == "Windows":
        subprocess.run(["notepad", tempfilepath], check=True)
    else:
        subprocess.run(["nano", tempfilepath], check=True)
    
    with open(tempfilepath,"r") as tmpfile:
        return tmpfile.read()

def mass_send(title,content,recipients):
    print("Mass sending...")
    results = []
    recipients = tqdm(recipients)
    for recipient in recipients:
        recipients.set_description(f"Mailing {recipient}")
        results.append(recipient + ": " + return_action_result(client.send_mail(title,content,recipient)))
                
    print_list(results)

def return_action_result(response:Response):
    if response == None:
        return f"{Fore.RED}No response{Style.RESET_ALL}"

    if response.text in RESULT_ALIASES.keys():
        return RESULT_ALIASES[response.text]
    
    if response.ok:
        if response.text == "":
            return f"{Fore.GREEN}Success!{Style.RESET_ALL}"
        return f"{Fore.GREEN}{response.text}{Style.RESET_ALL}"
    else:
        if response.text == "":
            return f"{Fore.RED}Failure{Style.RESET_ALL}"
        return f"{Fore.RED}{response.text}{Style.RESET_ALL}"

def discover_player(username:str):
    if not username in knownplayers:
        knownplayers.append(username)
        with open(script_dir / "knownplayers.txt","w") as f:
            json.dump(knownplayers,f)

try:
    try:
        with open(script_dir / "knownplayers.txt","r") as f:
            knownplayers = json.load(f)
    except:
        pass

    sign_in()
    main_menu()
except KeyboardInterrupt:
    print("\nGoodbye!")