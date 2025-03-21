# nsaos client
A python client for the [Functional Paper and Mail System](https://steamcommunity.com/sharedfiles/filedetails/?id=3444382722) (known internally as nsaos for some reason) for garry's mod, there are lots of missing features, but it's coming along nicely

⚠️ Whitelist support is not implemented yet, so accounts created using this tool will not be able to recieve mail until the whitelist is disabled or someone is added to it from Garry's Mod

| Feature | nsapy | Original |
|--------|--------|-----|
| Inbox     | ✅ | ✅ |
| Send mail | ✅ | ✅ |
| Mail fonts and colors | ❌ | ✅ |
| Bulk send mail | ✅ | ❌ |
| Delete mail | ✅ | ✅ |
| Delete all mail | ✅ | ❌ |
| Folders | ❌ | ✅ |
| Bulk sorting | ❔* | ❌ |
| Modify whitelist | ❌ | ✅ |
| Keep a list of all known players | ✅ | ❌ |
| Multi-account support | ✅ | ❌ |
| Mail forwarding | ✅ | ❌ |
| Keep a list of all known players | ✅ | ❌ |
| View candidates | ✅ | ✅ |
| Vote for candidates | ❌ | ✅ |
| View council | ❌ | ✅ |
| View suggestions | ❌ | ✅ |
| Vote on suggestions | ❌ | ✅ |

* Bulk sorting sorts folders in the original mod, and doesn't change anything in the client

## How to use

### Importing an account from GMOD
To import an account from Garry's Mod, you need to find your user.txt file, first right-click on Garry's mod in steam, and click browse local files, then go to garrysmod/data/nsaos/user.txt, copy that file, and then go to the folder where nsaosclient is. Create a folder called "users" if it doesn't already exist, then paste the file into the folder you created and rename it to your username

### Sorting mail
To sort your mail, you need to tell the client where your mailassoc.txt file is, it should be in the same folder as your user.txt (see above), make sure that your mailbox is closed before sorting your mail, or the changes will not take effect, once you have chosen your mailassoc.txt you will have 3 options for sorting
| Sorting method | Effect |
|----------------|--------|
|Put mail in author folders|Sorts mail into folders which will be the name of the person who sent them, so mail from buzzsaw08 would go into a folder called buzzsaw08|
|Put mail in today's folder|Sorts mail into *TODAY*'s folder, not when the mail was sent because i don't have access to that info, for example a folder called March 21 2025 useful if you're sorting every day but not for much else|
|Put mail in custom folder|Sorts mail into a folder with a name you choose|

After selecting your sorting method, you can choose if you want to overwrite folders of mail that already has one, if no, mail that isn't in the inbox folder will be ignored

### Known players
To use the send to all known players feature, you will need to first find some players, this can be done by checking your inbox (gets the usernames of all players who have messaged you) and by checking politics (gets the usernames of all candidates)

### Exporting an account to GMOD
You might need to export an account for use in Garry's Mod to view mail with special fonts or colors, disable whitelist, or add someone to the whitelist, to do this simply copy the file from the users folder into the garrysmod/data/nsaos/ folder and rename it to user.txt
