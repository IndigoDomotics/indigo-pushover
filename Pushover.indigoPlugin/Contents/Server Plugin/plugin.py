#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.debug = pluginPrefs.get("debug", False)

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        self.debugLog(u"startup called")

    def shutdown(self):
        self.debugLog(u"shutdown called")

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

        if strInput is None:
            return strInput
        else:
            strInput = strInput.strip()

            strInput = self.substitute(strInput)

            self.debugLog(strInput)

            #fix issue with special characters
            strInput = strInput.encode('utf8')

            return strInput

    # actions go here
    def send(self, pluginAction):

        msgBody = self.prepareTextValue(pluginAction.props['msgBody'])

        #fill params dictionary with required values
        params = {
            'token': self.pluginPrefs['apiToken'].strip(),
            'user': self.pluginPrefs['userKey'].strip(),
            'message': msgBody
        }

        attachment = {}

        #populate optional parameters
        if self.present(pluginAction.props.get('msgTitle')):
            msgTitle = self.prepareTextValue(pluginAction.props['msgTitle']).strip()
            params['title'] = msgTitle
        else:
            msgTitle = ''
        

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
            self.debugLog(u"Result: %s" % r.text)
            self.logger.info(u"Pushover notification was sent sucessfully, title: " + msgTitle + ", body: " + msgBody)
        else:
            self.logger.error(u"Post Error - Result: %s" % r.text)

    def cancel(self, pluginAction):
    
        params = {'token': self.pluginPrefs['apiToken'].strip() }
        URL = "https://api.pushover.net/1/receipts/cancel_by_tag/" + pluginAction.props['cancelTag'] + ".json"
        r = requests.post(URL, data = params)
        self.debugLog(u"Result: %s" % r.text)

