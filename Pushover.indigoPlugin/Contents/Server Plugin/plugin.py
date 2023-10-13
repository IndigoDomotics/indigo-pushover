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
        self.logLevel = int(pluginPrefs.get("logLevel", logging.INFO))
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(f"logLevel = {self.logLevel}")
        self.apiToken = None
        self.sounds = None

        self.apiToken = pluginPrefs.get('apiToken', None)
        if not self.apiToken:
            self.logger.warning(f"API Token not configured")

    def startup(self):
        self.logger.debug(f"startup called")
        try:
            r = requests.get(f"https://api.pushover.net/1/sounds.json?token={self.apiToken}")
            custom_decoder = json.JSONDecoder(object_hook=OrderedDict)
            rdict = custom_decoder.decode(r.text)
            self.sounds = rdict['sounds']
        except Exception as err:
            self.logger.warning(f"Error getting alert sounds list: {err}")
            self.sounds = OrderedDict(
                [(u'pushover', u'Pushover (default)'), (u'bike', u'Bike'), (u'bugle', u'Bugle'), (u'cashregister', u'Cash Register'),
                 (u'classical', u'Classical'), (u'cosmic', u'Cosmic'), (u'falling', u'Falling'), (u'gamelan', u'Gamelan'), (u'incoming', u'Incoming'),
                 (u'intermission', u'Intermission'), (u'magic', u'Magic'), (u'mechanical', u'Mechanical'), (u'pianobar', u'Piano Bar'),
                 (u'siren', u'Siren'), (u'spacealarm', u'Space Alarm'), (u'tugboat', u'Tug Boat'), (u'alien', u'Alien Alarm (long)'),
                 (u'climb', u'Climb (long)'), (u'persistent', u'Persistent (long)'), (u'echo', u'Pushover Echo (long)'),
                 (u'updown', u'Up Down (long)'), (u'vibrate', u'Vibrate Only'), (u'none', u'None (silent)')])
        self.logger.debug(f"Sounds = {self.sounds}")

    def shutdown(self):
        self.logger.debug("shutdown called")

    def get_sound_list(self, filter="", valuesDict=None, typeId="", targetId=0):
        returnList = list()
        for name in self.sounds:
            returnList.append((name, self.sounds[name]))
        return returnList

    def validateActionConfigUi(self, valuesDict, typeId, deviceId):
        errorDict = indigo.Dict()

        if typeId == "send":
            if not self.present(valuesDict.get("msgBody")):
                errorDict["msgBody"] = "Cannot be blank"
        elif typeId == "cancel":
            if not self.present(valuesDict.get("cancelTag")):
                errorDict["cancelTag"] = "Cannot be blank"

        if len(errorDict):
            return False, valuesDict, errorDict
        else:
            return True, valuesDict, errorDict

    @staticmethod
    def present(prop):
        return prop and prop.strip() != ""

    # helper functions
    def prepareTextValue(self, strInput):

        if not strInput:
            return strInput
        return self.substitute(strInput.strip())

    # actions go here
    def send(self, pluginAction):
        self.logger.threaddebug(f"send pluginAction.props = {pluginAction.props}")

        msgBody = self.prepareTextValue(pluginAction.props['msgBody'])

        # fill params dictionary with required values
        params = {
            'token': self.apiToken,
            'user': self.pluginPrefs['userKey'].strip(),
            'message': msgBody
        }

        attachment = {}

        # populate optional parameters
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
                    self.logger.warn("Warning: attached file size was too large, attachment was skipped")
            else:
                self.logger.warn("Warning: file does not exist, or is not an image file, attachment was skipped")

        if self.present(pluginAction.props.get('msgPriority')):
            params['priority'] = pluginAction.props['msgPriority']
            if params['priority'] == 2 or params['priority'] == "2":
                # Require Confirmation priority requires 2 additional params:
                params['retry'] = "600"  # show every 10 minutes until confirmed (could expose UI for this...)
                params['expire'] = "86400"  # set expire to maximum (24 hours)

                if self.present(pluginAction.props.get('msgTags')):
                    params['tags'] = self.prepareTextValue(pluginAction.props['msgTags'])

        r = requests.post("https://api.pushover.net/1/messages.json", data=params, files=attachment)

        if r.status_code == 200:
            self.logger.debug(f"Result: {r.text}")
            self.logger.info(f"Pushover notification was sent successfully, title: {msgTitle}, body: {msgBody}")
        else:
            self.logger.error(f"Post Error - Result: {r.text}")

    def cancel(self, pluginAction):

        params = {'token': self.apiToken}
        URL = f"https://api.pushover.net/1/receipts/cancel_by_tag/{pluginAction.props['cancelTag']}.json"
        r = requests.post(URL, data=params)
        self.logger.debug(f"Result: {r.text}")

    ########################################
    # ConfigUI methods
    ########################################

    def validatePrefsConfigUi(self, valuesDict):
        self.logger.debug(u"validatePrefsConfigUi called")
        errorMsgDict = indigo.Dict()

        if valuesDict["apiToken"] == "":
            errorMsgDict['apiToken'] = "API Token is required"

        if len(errorMsgDict) > 0:
            return False, valuesDict, errorMsgDict
        return True, valuesDict

    def closedPrefsConfigUi(self, valuesDict, userCancelled):
        self.logger.debug(u"closedPrefsConfigUi called")
        if not userCancelled:
            self.logLevel = int(valuesDict.get("logLevel", logging.INFO))
            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(f"logLevel = {self.logLevel}")

            self.apiToken = valuesDict.get('apiToken', None)
            if not self.apiToken:
                self.logger.error(f"API Token not configured")

    # doesn't do anything, just needed to force other menus to dynamically refresh
    @staticmethod
    def menuChanged(valuesDict, typeId, devId):
        return valuesDict
