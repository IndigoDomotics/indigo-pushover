#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import logging
import json
from collections import OrderedDict

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        try:
            self.logLevel = int(self.pluginPrefs[u"logLevel"])
        except:
            self.logLevel = logging.INFO
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u"logLevel = {}".format(self.logLevel))


    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        self.logger.debug(u"startup called")

        savedList = self.pluginPrefs.get(u"appTokens", None)
        if savedList:
            self.appTokenList = json.loads(savedList)
        else:
            self.appTokenList = {}        

        try:
            appToken = self.pluginPrefs['apiToken']
            r = requests.get("https://api.pushover.net/1/sounds.json?token={}".format(appToken))
            customdecoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
            rdict = customdecoder.decode(r.text)
            self.sounds = rdict['sounds']
            self.logger.debug(u"Sounds = {}".format(self.sounds))
        except Exception as err:
            self.logger.warning(u"Error getting alert sounds list: {}".format(err))
        
        
    def shutdown(self):
        self.logger.debug(u"shutdown called")

    def get_sound_list(self, filter="", valuesDict=None, typeId="", targetId=0):
        returnList = list()
        for name in self.sounds:
            returnList.append((name, self.sounds[name]))
        self.logger.debug(u"get_sound_list = {}".format(returnList))
        return returnList

    def validateActionConfigUi(self, valuesDict, typeId, deviceId):
        errorDict = indigo.Dict()

        if typeId == "send":
            if not self.present(valuesDict.get("msgBody")):
                errorDict["msgBody"] = "Cannot be blank"
                return (False, valuesDict, errorDict)
        elif typeId == "cancel":
            if not self.present(valuesDict.get("cancelTag")):
                errorDict["cancelTag"] = "Cannot be blank"
                return (False, valuesDict, errorDict)

        return (True, valuesDict, errorDict)

    def present(self, prop):
        return (prop and prop.strip() != "")

    # helper functions
    def prepareTextValue(self, strInput):

        if not strInput:
            return strInput            
        return self.substitute(strInput.strip())


    # actions go here
    def send(self, pluginAction):
        self.logger.debug(u"send pluginAction.props = {}".format(pluginAction.props))
    
        appToken = pluginAction.props.get('appToken', None)
        if not appToken:
            appToken = self.pluginPrefs['apiToken']
        self.logger.debug(u"appToken = {}".format(appToken))

        msgBody = self.prepareTextValue(pluginAction.props['msgBody'])

        #fill params dictionary with required values
        params = {
            'token': appToken.strip(),
            'user': self.pluginPrefs['userKey'].strip(),
            'message': msgBody
        }

        attachment = {}

        #populate optional parameters
        if self.present(pluginAction.props.get('msgTitle')):
            msgTitle = self.prepareTextValue(pluginAction.props['msgTitle']).strip()
            params['title'] = msgTitle
        else:
            msgTitle = u''
        

        if self.present(pluginAction.props.get('msgDevice')):
            params['device'] = pluginAction.props['msgDevice'].strip()

        if self.present(pluginAction.props.get('msgUser')):
            params['user'] = pluginAction.props['msgUser'].strip()

        if self.present(pluginAction.props.get('msgSound')):
            params['sound'] = pluginAction.props["msgSound"].strip()

        if self.present(pluginAction.props.get('msgSupLinkTitle')):
            params['url_title'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

        if self.present(pluginAction.props.get('msgSupLinkUrl')):
            params['url'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])

        if self.present(pluginAction.props.get('msgAttachment')):
            attachFile = self.prepareTextValue(pluginAction.props['msgAttachment'])
            extension = os.path.splitext(attachFile.lower())[1]

            if os.path.isfile(attachFile) and (extension in ['.jpg', '.jpeg', '.gif']):
                if os.path.getsize(attachFile) <= 2621440:
                    attachment = {
                        "attachment": (attachFile, open(attachFile, "rb"), "image/jpeg")
                    }
                else:
                    self.logger.warn(u"Warning: attached file size was too large, attachment was skipped")
            else:
                self.logger.warn(u"Warning: file does not exist, or is not an image file, attachment was skipped")

        if self.present(pluginAction.props.get('msgPriority')):
            params['priority'] = pluginAction.props['msgPriority']
            if params['priority'] == 2 or params['priority'] == "2":
                # Require Confirmation priority requires 2 additional params:
                params['retry'] = "600"     # show every 10 minutes until confirmted (could expose UI for this...)
                params['expire'] = "86400"  # set expire to maximum (24 hours)

                if self.present(pluginAction.props.get('msgTags')):
                    params['tags'] = self.prepareTextValue(pluginAction.props['msgTags'])

        r = requests.post("https://api.pushover.net/1/messages.json", data = params, files = attachment)

        if r.status_code == 200:
            self.logger.debug(u"Result: {}".format(r.text))
            self.logger.info(u"Pushover notification was sent sucessfully, title: {}, body: {}".format(msgTitle, msgBody))
        else:
            self.logger.error(u"Post Error - Result: {}".format(r.text))


    def cancel(self, pluginAction):
    
        params = {'token': self.pluginPrefs['apiToken'].strip() }
        URL = "https://api.pushover.net/1/receipts/cancel_by_tag/" + pluginAction.props['cancelTag'] + ".json"
        r = requests.post(URL, data = params)
        self.logger.debug(u"Result: %s" % r.text)

    ########################################
    # This is the method that's called by the Add Token button in the menu dialog.
    ########################################

    def addToken(self, valuesDict, typeId=None, devId=None):

        appName = valuesDict["appName"]
        appToken = valuesDict["appToken"]

        tokenItem = {"name" : appName, "token" : appToken}
        self.logger.debug(u"Adding Token {}: {}".format(appName, appToken))
        self.appTokenList[appName] = appToken
        self.listTokens()
        
        indigo.activePlugin.pluginPrefs[u"appTokens"] = json.dumps(self.appTokenList)

        return valuesDict

    ########################################
    # This is the method that's called by the Delete Token button
    ########################################
    def deleteTokens(self, valuesDict, typeId=None, devId=None):
        
        for item in valuesDict["appTokenList"]:
            self.logger.info(u"Deleting Token {}".format(item))
            del self.appTokenList[item]

        self.listTokens()
        indigo.activePlugin.pluginPrefs[u"appTokens"] = json.dumps(self.appTokenList)

        
    def get_app_tokens(self, filter="", valuesDict=None, typeId="", targetId=0):
        returnList = list()
        for name in self.appTokenList:
            returnList.append((self.appTokenList[name], name))
        self.logger.debug(u"get_app_tokens = {}".format(returnList))
        return sorted(returnList, key= lambda item: item[1])


    ########################################
    
    def listTokens(self):
        if len(self.appTokenList) == 0:
            self.logger.info(u"No App Tokens Devices")
            return
            
        fstring = u"{:20} {:^50}"
        self.logger.info(fstring.format("App Name", "App Token"))
        for name, token in self.appTokenList.iteritems():
             self.logger.info(fstring.format(name, token))

    ########################################
    # ConfigUI methods
    ########################################

    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        if not userCancelled:
            try:
                self.logLevel = int(valuesDict[u"logLevel"])
            except:
                self.logLevel = logging.INFO
            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(u"logLevel = {}".format(self.logLevel))
 
    # doesn't do anything, just needed to force other menus to dynamically refresh

    def menuChanged(self, valuesDict, typeId, devId):
        return valuesDict


