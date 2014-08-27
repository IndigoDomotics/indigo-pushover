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

	# helper functions
	def prepareTextValue(strInput):

		if strInput is None:
			return strInput
		else:
			strInput = strInput.strip()

			while "%%v:" in strInput:
				strInput = self.substituteVariable(strInput)

			#todo: encode special characters

			return strInput

	# actions go here
	def send(self, pluginAction):

		#fill params dictionary with required values
		params = {
			'token': self.pluginPrefs['apiToken'].strip(),
			'user': self.pluginPrefs['userkey'].strip(),
			'title': self.prepareTextValue(pluginAction.props['msgTitle']),
			'message': self.prepareTextValue(pluginAction.props['msgBody'])
		}

		#populate optional parameters
		if pluginAction.props['msgDevice'] is not None:
			params['device'] = pluginAction.props['msgDevice'].strip()

		if pluginAction.props['msgSound'] is not None:
			params['sound'] = pluginAction.props["msgSound"].strip()

		if pluginAction.props['msgSupLinkTitle'] is not None:
			params['url_title'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

		if pluginAction.props['msgSupLinkUrl'] is not None:
			params['url'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])

		if pluginAction.props['msgPriority'] is not None:
			params['priority'] = pluginAction.props['msgPriority']
		
		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request(
			"POST",
			"/1/messages",
			urllib.urlencode(msgParams),
			{ "Content-type": "application/x-www-form-urlencoded" }
		)
