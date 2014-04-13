#! /usr/bin/env python
# -*- coding: utf-8 -*-

import httplib, urllib, sys, os

class Plugin(indigo.PluginBase):

	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = True

	def __del__(self):
		indigo.PluginBase.__del__(self)


	def startup(self):
		self.debugLog(u"startup called")

	def shutdown(self):
		self.debugLog(u"shutdown called")

	# actions go here
	def send(self, pluginAction):
		pushtoken = self.pluginPrefs["applicationapikey"]

		if pluginAction.props["pushtoken"]:
			pushtoken = pluginAction.props["pushtoken"]

		pushtitle = pluginAction.props["txttitle"]

		while "%%v:" in pushtitle:
			pushtitle = self.substituteVariable(pushtitle)
		
		pushmessage = pluginAction.props["txtmessage"]

		while "%%v:" in pushmessage:
			pushmessage = self.substituteVariable(pushmessage)
		
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request(
			"POST",
			"/1/messages",
			urllib.urlencode({
				"token": pushtoken,
				"user": self.pluginPrefs["userkey"],
				"title": pushtitle,
				"message": pushmessage,
				"device": pluginAction.props["pushdevice"],
				"sound": pluginAction.props["pushsound"],
				"url": pluginAction.props["pushurl"],
				"url_title": pluginAction.props["pushurltitle"],
			}),
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
