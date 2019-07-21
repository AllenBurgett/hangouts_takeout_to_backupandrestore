import json
from datetime import datetime
import xml.etree.ElementTree as ET
import re

import time


def current_milli_time(): return int(round(time.time() * 1000))


def singlePath(root, thread):
    participant_data = thread['conversation']['conversation']['participant_data']

    if 'phone_number' in participant_data[0].keys():
        # number
        phone = participant_data[0]['phone_number']['e164']
        is_valid = participant_data[0]['phone_number']['i18n_data']['is_valid']
        if not is_valid:
            # likely a short code, skip
            return 0
        # name
        name = participant_data[0]['fallback_name']
    # Unknown case where object 0 has no phone number and is the only object in array. Submitted by reddit user.
    elif len(thread['conversation']['conversation']['participant_data']) < 2:
        return 0
    # if this fails and it's not a Group message, then it's a hangouts message (or incoming message?)
    elif 'phone_number' in participant_data[1].keys():
        phone = participant_data[1]['phone_number']['e164']
        name = participant_data[1]['fallback_name']
        is_valid = participant_data[1]['phone_number']['i18n_data']['is_valid']
        if not is_valid:
            # likely a short code, skip
            return 0

    else:
        return 0

    count = 0

    for msg in thread['events']:
        try:
            count += 1
            # Inbound/Outbound
            type = getType(msg)

            # This is where the message is located
            text = getMessage(msg)

            # has attachment
            if text == None:
                continue

            # timestamp
            ts = getTimestamp(msg)

            if type == 2:
                datesent = 0
            else:
                datesent = ts

            # date
            date = getReadableDate(ts)

            ET.SubElement(root, "sms", protocol="0", address=str(phone), date=str(ts), type=str(type), subject="null", body=str(text), toa="null", sc_toa="null",
                          service_center="null", read="1", status="-1", locked="0", date_sent=str(datesent), sub_id="-1", readable_date=str(date), contact_name=str(name))
        except Exception:
            print(msg)
            raise

    return count

# returns the count of messages


def groupPath(root, thread):
    user_ids = groupIDs(thread)

    if user_ids is None:
        return 0

    count = buildGroupConvo(root, thread, user_ids)

    return count


def groupIDs(thread):
    user_ids = {}

    phone_found = False
    for participant_data in thread['conversation']['conversation']['participant_data']:
        try:
            userID = participant_data['id']['chat_id']
            if participant_data.get('phone_number'):
                phone_found = True
                phoneNumber = participant_data['phone_number']['e164']
                userName = participant_data['fallback_name']
                user_ids[userID] = (userName, phoneNumber)
            else:
                # if this is an mms thread, the owner's phone # will be in "fallback_name" for some reason
                # so, if we find other numbers, and only one is missing, it should be your own number
                fallback = participant_data.get("fallback_name")
                if fallback:
                    user_ids[userID] = (fallback, fallback)
        except Exception:
            print(participant_data)
            raise

    if phone_found:
        return user_ids
    else:
        # this is a Hangouts thread
        return None


def buildGroupConvo(root, thread, user_ids):
    count = 0

    for msg in thread['events']:
        try:
            count += 1

            sender_id = msg['sender_id']['chat_id']

            type = getType(msg)

            text = getMessage(msg)

            # has attachment
            if text == None:
                continue

            ts = getTimestamp(msg)

            if type == 2:
                datesent = 0
            else:
                datesent = ts

            date = getReadableDate(ts)

            xml_address = '~'.join([user[1] for user in user_ids.values()])
            xml_name = ', '.join([user[0] for user in user_ids.values()])

            mms_root = ET.SubElement(root,
                                     "mms",
                                     address=str(xml_address),
                                     date=str(ts), read="1",
                                     date_sent=str(datesent),
                                     sub_id="-1",
                                     readable_date=str(date),
                                     contact_name=str(xml_name),
                                     rr="129",
                                     ct_t="application/vnd.wap.multipart.related",
                                     seen="1",
                                     text_only="1",
                                     msg_box=str(type),  # Conveniently, this matches sms values - 2 is outbox, 1 is inbox
                                     )

            if type == 2:
                # PduHeaders.RESPONSE_STATUS_OK
                mms_root.set("resp_st", "128")
                mms_root.set("m_type", "128")  # sent, maybe?
            else:
                mms_root.set("m_type", "132")  # hopefully "received"

            parts = ET.SubElement(mms_root, "parts")
            ET.SubElement(parts, "part", seq="0", ct="text/plain", text=text)

            addrs = ET.SubElement(mms_root, "addrs")
            for key, (name, phone) in user_ids.items():
                # types get weird for mms - they're PDUHeaders values
                # 151 - PduHeaders.TO
                # 137 - PduHeaders.FROM
                if key == sender_id:
                    type = "137"
                else:
                    type = "151"
                ET.SubElement(addrs, "addr", address=phone,
                              type=type, charset="106")

        except Exception:
            print(msg)
            raise

    return count


def getType(msg):
    # if print(data['conversations'][238]['events'][1]['sender_id']['gaia_id']) ==
    # print(data['conversations'][238]['events'][1]['self_event_state']['user_id']['gaia_id']) then 2
    # else 1
    senderID = msg['sender_id']['gaia_id']
    userID = msg['self_event_state']['user_id']['gaia_id']
    if senderID == userID:
        return 2  # sent by "me"
    else:
        return 1


def getMessage(msg):

    # print(data['conversations'][28]['events'][0]['chat_message']['message_content']['segment'][0]['text'])
    # check that msg contains 'chat_message'
    if 'chat_message' not in msg:
        return None

    message_content = msg['chat_message']['message_content']
    # check for pictures
    text = ""
    if 'attachment' in message_content:
        for attachment in message_content['attachment']:
            types = attachment['embed_item']['type']
            for type in types:
                if type == "PLUS_PHOTO":
                    url = attachment["embed_item"]["plus_photo"]["url"]
                    # strip spaces that for some reason are in there
                    url = re.sub(r'\s+', '', url)
                    text += url + "\n"
                elif type == "PLUS_AUDIO_V2":
                    #These are voicemail transcriptions, and don't seem to be easily turned into a link
                    #default to info header instead
                    text += "Voicemail transcript:\n"
                elif type == "THING_V2":
                    url = attachment['embed_item']['thing_v2']['url']
                    # strip spaces that for some reason are in there
                    url = re.sub(r'\s+', '', url)

                    name = attachment['embed_item']['thing_v2']['name']
                    text += name + "\n" + url
                # thing doesn't seem to ever show up, and place_v2 is always matched by a thing_v2
                elif type in ('THING', 'PLACE_V2'):
                    continue
                else:
                    raise Exception(f"Unknown attachment type: {type}")

    if message_content.get('segment'):
        segments = message_content['segment']
        for segment in segments:
            type = segment['type']
            if type == "TEXT":
                text += segment['text']
            elif type == "LINE_BREAK":
                text += "\n"
            elif type == "LINK":
                url = segment['text']
                # strip spaces that for some reason are in there
                url = re.sub(r'\s+', '', url)
                text += url

    if not text:
        raise Exception(f"No text found for message {msg}")

    return text


def getTimestamp(msg):

    # print(data['conversations'][28]['events'][0]['timestamp'])
    ts = int(int(msg['timestamp']) / 1000)

    return ts


def getReadableDate(ts):

    # ts=data['conversations'][28]['events'][0]['timestamp']
    # print(datetime.fromtimestamp(int(int(ts) / 1000000)).strftime('%b %d, %Y %I:%M:%S %p'))
    date = datetime.fromtimestamp(
        int(int(ts) / 1000)).strftime('%b %d, %Y %I:%M:%S %p').replace(' 0', ' ')

    return date


def main():

    with open('Hangouts.json', encoding="utf8") as f:
        datastore = f.read()

    data = json.loads(datastore)

    root = ET.Element("smses", count=str(
        0), backup_set="145bea68-a1f4-4068-a631-06757067e675", backup_date=str(current_milli_time()))

    count = 0
    for thread in data['conversations']:
        # Group message check
        if len(thread['conversation']['conversation']['participant_data']) > 2:
            count += groupPath(root, thread)
        else:
            count += singlePath(root, thread)

    root.set("count", str(count))
    tree = ET.ElementTree(root)
    tree.write("test.xml")


main()
