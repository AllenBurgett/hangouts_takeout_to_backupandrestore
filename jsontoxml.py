import json
from datetime import datetime
import xml.etree.ElementTree as ET

def singlePath(root, thread):

    if 'phone_number' in thread['conversation']['conversation']['participant_data'][0].keys():
        #number
        phone=thread['conversation']['conversation']['participant_data'][0]['phone_number']['e164']
        #name
        name=thread['conversation']['conversation']['participant_data'][0]['fallback_name']
    #Unknown case where object 0 has no phone number and is the only object in array. Submitted by reddit user.
    elif len(thread['conversation']['conversation']['participant_data'][1]) < 2:
        return 0
    #if this fails and it's not a Group message, then it's a hangouts message
    elif 'phone_number' in thread['conversation']['conversation']['participant_data'][1].keys():
        phone=thread['conversation']['conversation']['participant_data'][1]['phone_number']['e164']
        name=thread['conversation']['conversation']['participant_data'][1]['fallback_name']
    else:
        return 0
    
    count = 0
    
    for msg in thread['events']:
        count+=1
        #Inbound/Outbound
        type = getType(msg)
            
        #This is where the message is located
        text = getMessage(msg)
        
        #has attachment
        if text == None:
            continue

        #timestamp
        ts = getTimestamp(msg)        
        
        if type == 2:
            datesent=0
        else:
            datesent=ts

        #date
        date = getReadableDate(ts)
        
        ET.SubElement(root, "sms", protocol="0", address=str(phone), date=str(ts), type=str(type), subject="null", body=str(text), toa="null", sc_toa="null", service_center="null", read="1", status="-1", locked="0", date_sent=str(datesent), sub_id="-1", readable_date=str(date), contact_name=str(name))
    
    return count

#returns the count of messages
def groupPath(root, thread):
    user_ids = groupIDs(thread)
    
    if user_ids is None:
        return 0
        
    count = buildGroupConvo(root, thread)
    
    return count
        
    

def groupIDs(thread):
    user_ids = {}
    
    #if no phone numbers in all participant_data, then this is a hangouts chat_message
    if not 'phone_number' in thread['conversation']['conversation']['participant_data']:
        return None
    
    for participant_data in thread['conversation']['conversation']['participant_data']:
        if 'phone_number' in participant_data:
            userID = participant_data['id']['chat_id']
            phoneNumber = participant_data['phone_number']['e164']
            userName = participant_data['fallback_name']
            user_ids[userID] = (userName, phoneNumber)
            
        else:
            userID = participant_data['id']['chat_id']
            user_ids[userID] = ('Owner')
            
    return user_ids
    
def buildGroupConvo(root, thread):
    count = 0
    
    for msg in thread['events']:
        count+=1
        
        type = getType(msg)
        
        text = getMessage(msg)
        
        #has attachment
        if text == None:
            continue
        
        ts = getTimestamp(msg)
        
        if type == 2:
            datesent = 0
        else:
            datesent = ts
            
        date = getReadableDate(ts)
        
    #build XML here
    
    return count
        
        
def getType(msg):
    # if print(data['conversations'][238]['events'][1]['sender_id']['gaia_id']) ==
    #print(data['conversations'][238]['events'][1]['self_event_state']['user_id']['gaia_id']) then 2
    #else 1
    senderID = msg['sender_id']['gaia_id']
    userID = msg['self_event_state']['user_id']['gaia_id']
    if senderID == userID:
        return 2
    else:
        return 1
        
def getMessage(msg):

    #print(data['conversations'][28]['events'][0]['chat_message']['message_content']['segment'][0]['text'])
    #check for pictures
    if 'attachment' in msg['chat_message']['message_content']:
        if 'text' in msg['chat_message']['message_content']:
            text = msg['chat_message']['message_content']['segment'][0]['text']
        else:
            return None
    else:
        text = msg['chat_message']['message_content']['segment'][0]['text']
        
    return text
    
def getTimestamp(msg):

    #print(data['conversations'][28]['events'][0]['timestamp'])
    ts=int(int(msg['timestamp']) / 1000)
    
    return ts
    
def getReadableDate(ts):

    #ts=data['conversations'][28]['events'][0]['timestamp']
    #print(datetime.fromtimestamp(int(int(ts) / 1000000)).strftime('%b %d, %Y %I:%M:%S %p'))
    date = datetime.fromtimestamp(int(int(ts) / 1000)).strftime('%b %d, %Y %I:%M:%S %p').replace(' 0', ' ')
    
    return date
    

def main():

    with open('Hangouts.json', encoding="utf8") as f:
        datastore = f.read()
        
    data = json.loads(datastore)

    root = ET.Element("smses", count=str(0), backup_set="145bea68-a1f4-4068-a631-06757067e675", backup_date="1555940780184")
        
    count = 0
    for thread in data['conversations']:
        #Group message check
        if len(thread['conversation']['conversation']['participant_data']) > 2:
            continue
            count += groupPath(root, thread)
        else:
            count += singlePath(root, thread)
            
    root.set("count", str(count))
    tree = ET.ElementTree(root)
    tree.write("test.xml")
    
main()
