# hangouts_takeout_to_backupandrestore
Take the hangouts JSON output from Takeout and convert it to an XML that's readable by the App Backup and Restore

This will import your SMS 1:1 messages. Group messages support has been added.

Group messages seem to be much more complicated than 1:1 messages (who would have thought it?). Please feel free to use the code in place as a starting point. Otherwise, I might attempt to handle group messages in the future.

**Notes**
I made this for myself and thought I would share it with whomever wandered across it. I do not guarantee it will work for you, but it has worked for me. **If you are not familiar with coding, I urge you to have someone who is review this (and really anything you pull that's not from a legitimate organization) before you use it. I make no web calls, but you are exposing sensitive information when giving programs like this one access to your private conversations. So, error on the side of caution and have someone you trust review this to ensure your data is safe.**

**Instructions**
1. Go to takeout.google.com and have them prepare your Hangouts JSON (JSON is the default format option). Follow Google's instructions to retrieve.
2. Make sure you have Python 3 installed (I'm running 3.7, but I'm probably not running anything very specific to it. Python 2 blows up on the encoding).
3. Download jsontoxml.py
4. Put jsontoxml.py and Hangouts.json in the same folder 
5. Open a command window (terminal should work as well, but I've only tested on Windows) and navigate to the folder from step 4
6. Type "python3 jsontoxml.py" and hit enter.
**Note**: _This script requires python 3 to run. If your OS installs python 3 in a different location such as "python" that may work as well. In many cases the nonspecific use of "python" still defaults to python2 which is why python3 is deliberately used here but steps to invoke python3 on your OS may differ._
7. If you get no errors, then you should be able to go to back to your folder and see test.xml
8. Download SMS Backup & Restore https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore on the phone you're transferring the messages to.
9. Get test.xml to your phone (my method was Google Drive)
10. Move test.xml to the SMSBackupRestore folder (I used https://play.google.com/store/apps/details?id=com.asus.filemanage to do this)
11. Launch SMS Backup and Restore and navigate to Restore
12. Click "Select Another Backup" you should see test.xml. Choose it and continue.
13. Turn the Phone Calls switch off
14. Click Restore
