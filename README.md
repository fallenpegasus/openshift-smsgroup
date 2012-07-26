OpenShift SMSGroup QuickStart

This repository is a quickstart for the SMSGroup application.

It uses the OpenShift Python-2.6 language cartridge, the OpenShift MongoDB-2.0 database cartridge, and requires the API credentials of a Twilio account.


Quickstart
==========

1. Create an account at http://openshift.redhat.com/ and then install the rhc client tool.

2. Create a python application and attach mongodb to it.

    rhc app create -a smsgroup -t python-2.6
    rhc app cartridge add -a smsgroup -c mongodb-2.0

3. Add this upstream repo.

    cd smsgroup
    git remote add upstream -m master git://github.com/fallenpegasus/openshift-smsgroup.git
    git pull -s recursive -X theirs upstream master

4. Add your Twilio credentials and information.

Log in to your Twilio.com account

Browse to https://www.twilio.com/user/account to get the "Account SID" and the "Auth Token"

Browse to https://www.twilio.com/user/account/phone-numbers/incoming and click "Buy a Number". Go through the process.

Edit the twilio_creds file, and set the account, token, and fromnum.  

    # change these to your Twilio account credentials
    twilio_account = "ACyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    twilio_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    twilio_fromnum = "+12024561414"

And then commit those changes to Git

    git add twilio_creds
    git commit -m "set twilio creds"
    # after you have done this, you MUST not push this repo to a public Git server!

5. Then push the repo into OpenShift

    git push

6. Now attach this app to Twilio

Browse to https://www.twilio.com/user/account/apps

Click on "Create TwiML App"

Set the Friendly Name to openshift-smsgroup

Set the SMS Request URL to http://smsgroup-mynamespace.rhcloud.com/twilio/sms (Remember to change "mynamespace" to your own OpenShift namespace.)

Set the SMS Request URL Schem from "POST" to "GET"

Click on "Save Changes"

Browse to https://www.twilio.com/user/account/phone-numbers/incoming

Click on the number you just bought

Set the SMS Application to "openshift-smsgroup"

Click on "Save Changes"

7. That's it, you can use you SMS Group!



Using the SMS Group
===================

* To join the group, SMS the word ".join" to the phone number.  It will respond with ".ok"

* To leave the group, SMS the word ".leave" to the phone number.  It will respond with ".ok"

* To send a message to the group, just SMS the message to the phone number.  It will be broadcast to everyone who's joined.

* You do not have to be a member of the group to send a message to it.


Costs
=====

If you use a US NANP number, with no international messaging, Twilio will charge you USD1.00/month for the phone number, and USD0.01 per SMS sent and received.

For example, if you have ten people in the group, it will cost eleven cents every time someone sends it a message. One cent for the incoming.  And one cent for each of the ten outgoing messages. 
This is in addition to whatever your cellphone carriers are charging for texting.


MongoDB
=======

You can access the MonogDB instance by either installing the RockMongo 1.1 cartridge, or by ssh'ing into the application gear, and then running the "mongo" command on the command line.

    ssh 440a01df1a1b4766967198ed73e67c86@smsgroup-matwood.rhcloud.com
    [smsgroup-matwood.rhcloud.com ~]\> mongo
    MongoDB shell version: 2.0.2
    connecting to: 127.11.100.129:27017/admin
    > use smsgroup
    switched to db smsgroup
    > show collections

The "twiliolog" collection is a log of all the Twilio REST calls that have been issued to this application, with all the assocated parameters.

The "member" collection is all the current members of the group.  The _id of each record is the E.164 in +1XXXXXXXXX form of the member.

The "sendq" collection is queue all the messages that are about to be transmitted.  This will usually be empty, unless you are really fast on the draw.  The application does not try to sort this collection as it removes records from it, so if you have a large group with lots of traffic, messages may start being send out of order.


