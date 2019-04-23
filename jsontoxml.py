import json
from datetime import datetime
import xml.etree.ElementTree as ET

with open('Hangouts.json', encoding="utf8") as f:
	datastore = f.read()
    
data=json.loads(datastore)
	
count=0
phone=''
name=''
type=''
text=''
ts=''
datesent=''
date=''

root = ET.Element("smses", count=str(count), backup_set="145bea68-a1f4-4068-a631-06757067e675", backup_date="1555940780184")
    
for thread in data['conversations']:
    #Group message check
    if len(thread['conversation']['conversation']['participant_data']) > 2:
        continue
        
    if 'phone_number' in thread['conversation']['conversation']['participant_data'][0].keys():
        #number
        phone=thread['conversation']['conversation']['participant_data'][0]['phone_number']['e164']
        #name
        name=thread['conversation']['conversation']['participant_data'][0]['fallback_name']
    #if this fails and it's not a Group message, then it's a hangouts message
    elif 'phone_number' in thread['conversation']['conversation']['participant_data'][1].keys():
        phone=thread['conversation']['conversation']['participant_data'][1]['phone_number']['e164']
        name=thread['conversation']['conversation']['participant_data'][1]['fallback_name']
    else:
        continue
      
    for msg in thread['events']:
        count+=1
        #Inbound/Outbound
        # if print(data['conversations'][238]['events'][1]['sender_id']['gaia_id']) ==
        #print(data['conversations'][238]['events'][1]['self_event_state']['user_id']['gaia_id']) then 2
        #else 1
        sender_id=msg['sender_id']['gaia_id']
        user_id=msg['self_event_state']['user_id']['gaia_id']
        if sender_id == user_id:
            type=2
        else:
            type=1
            
        #This is where the message is located
        #print(data['conversations'][28]['events'][0]['chat_message']['message_content']['segment'][0]['text'])
        #check for pictures
        if 'attachment' in msg['chat_message']['message_content']:
            if 'text' in msg['chat_message']['message_content']:
                text=msg['chat_message']['message_content']['segment'][0]['text']
            else:
                continue
        else:
            text=msg['chat_message']['message_content']['segment'][0]['text']

        #timestamp
        #print(data['conversations'][28]['events'][0]['timestamp'])
        ts=int(int(msg['timestamp']) / 1000)
        
        if type == 2:
            datesent=0
        else:
            datesent=ts

        #date
        #ts=data['conversations'][28]['events'][0]['timestamp']
        #print(datetime.fromtimestamp(int(int(ts) / 1000000)).strftime('%b %d, %Y %I:%M:%S %p'))
        date=datetime.fromtimestamp(int(int(ts) / 1000)).strftime('%b %d, %Y %I:%M:%S %p').replace(' 0', ' ')
        
        ET.SubElement(root, "sms", protocol="0", address=str(phone), date=str(ts), type=str(type), subject="null", body=str(text), toa="null", sc_toa="null", service_center="null", read="1", status="-1", locked="0", date_sent=str(datesent), sub_id="-1", readable_date=str(date), contact_name=str(name))
    
root.set("count", str(count))
tree = ET.ElementTree(root)
tree.write("test.xml")
