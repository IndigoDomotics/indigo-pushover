#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2012, Chad Francis. All rights reserved.
# http://www.chadfrancis.com

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
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request(
			"POST",
			"/1/messages",
			urllib.urlencode({
				# retrieve application API token from plugin preferences dict
				"token": self.pluginPrefs["applicationapikey"],
				# retrieve user token from plugin preferences dict
				"user": self.pluginPrefs["userkey"],
				"title": pluginAction.props["txttitle"],
				"message": pluginAction.props["txtmessage"],
			}),
			{ "Content-type": "application/x-www-form-urlencoded" }
		)

