# SMSGroup
# a demo of OpenShift and Twilio and MongoDB

import sys
import os
import bottle
import pymongo
import datetime
import time
import threading

# why cant i just import twilio?
from twilio.rest import TwilioRestClient
from twilio import twiml

# suck in the Twilio account creds
execfile(os.environ['OPENSHIFT_REPO_DIR'] + "twilio_creds",
         globals(), locals())
# todo, cleanly handle failure
sys.stderr.write("twilio creds %s %s %s\n" % (twilio_account, twilio_token, twilio_fromnum))

twilio_client = TwilioRestClient(twilio_account, twilio_token)

# connect to the OpenShift MongoDB
mongo_con = pymongo.Connection(
  os.environ['OPENSHIFT_NOSQL_DB_HOST'],
  int(os.environ['OPENSHIFT_NOSQL_DB_PORT']))
mongo_db = mongo_con[os.environ['OPENSHIFT_APP_NAME']]
mongo_db.authenticate(os.environ['OPENSHIFT_NOSQL_DB_USERNAME'],
                      os.environ['OPENSHIFT_NOSQL_DB_PASSWORD'])
# todo, cleanly handle failure


def worker():
    while True:
        # todo, wait on a trigger condition, not poll
        time.sleep(1)
        while True:
            msg = mongo_db.sendq.find_and_modify(remove=True)
            if (msg == None): break
            sys.stderr.write("send %s %s\n" % (msg['To'], msg['Body']))
            message = twilio_client.sms.messages.create(to=msg['To'],
                                                        from_=twilio_fromnum,
                                                        body=msg['Body'])

thr_work = threading.Thread(target=worker)
thr_work.daemon = True
thr_work.start()

bottle.debug(True)
app = bottle.Bottle()

@app.route('/', method='GET')
def route_get_index():
    return ""

@app.route('/twilio/sms', method='GET')
def route_get_twilio_sms():

    # HTTP URL query parameters from Twilio are:
    #  SmsSid  a unique identifier for the message
    #  AccountSid  a unique identifier of the Twilio Account
    #  From  the phone number that sent this message, in E.164 format
    #  To  the phone number of the recipient, in E.164 format
    #  Body  The text body of the SMS message
    #  FromCity FromState FromZip FromCountry  computed from From, if possible
    #  ToCity ToState ToZip ToCountry  computed from To, if possible

    # Bottle data of interest is:
    #  bottle.request.query
    #  bottle.request.cookies
    #  bottle.request.headers

    # log Twilio stuff to MongoDB
    sms_data = { }
    sms_data['_id'] = bottle.request.query.get('SmsSid', '').strip()
    sms_data['_date'] = datetime.datetime.utcnow()
    for k,v in bottle.request.query.iteritems():
        sms_data[k] = v
    mongo_db.twiliolog.insert(sms_data)

    sys.stderr.write("receive %s %s\n" % (sms_data['From'], sms_data['Body']))

    if (sms_data['Body'] == '.join'):
        # add an entry to mongo_db.member
        sys.stderr.write("join %s\n" % sms_data['From'])
        mongo_db.member.insert({"_id": sms_data['From']})
    elif (sms_data['Body'] == '.leave'):
        # remove an entry from mongo_db.member
        sys.stderr.write("leave %s\n" % sms_data['From'])
        mongo_db.member.remove({"_id": sms_data['From']})
    else:
        # send the message
        for m in mongo_db.member.find():
            sys.stderr.write("sendq %s %s\n" % (m['_id'], sms_data['Body']))
            mongo_db.sendq.insert({"To": m['_id'], "Body": sms_data['Body']})

    bottle.response.content_type = 'text/xml; charset=UTF8'
    r = twiml.Response()
    r.sms(".ok")
    return str(r)

@app.route('/twilio/voice', method='GET')
def route_get_twilio_voice():

    # HTTP URL query parameters from Twilio are:
    #  CallSid  a unique identifier for the call
    #  AccountSid  a unique identifier of the Twilio Account
    #  From  the phone number that sent this message,
    #   in E.164 format or client URI
    #  To  the phone number of the recipient, in E.164 format or client URI
    #  CallStatus  queued, ringing, in-progress, completed, busy, failed
    #   or no-answer  
    #  ApiVersion
    #  Direction  inbound or outbound-dial
    #  ForwardedFrom  in E.164 format, if set by PSTN carrier
    #  CallerName  result of optional CNAM lookup
    #  FromCity FromState FromZip FromCountry  computed from From, if possible
    #  ToCity ToState ToZip ToCountry  computed from To, if possible

    bottle.response.content_type = 'text/xml; charset=UTF8'
    r = twiml.Response()
    r.say("Hello")
    return str(r)

if __name__ == '__main__':
    bottle.run(app=app, host='localhost', port=8051, reloader=True)
else:
    application = app
