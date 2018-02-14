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

		#fill params dictionary with required values
		params = {
			'token': self.pluginPrefs['apiToken'].strip(),
			'user': self.pluginPrefs['userKey'].strip(),
			'title': self.prepareTextValue(pluginAction.props['msgTitle']),
			'message': self.prepareTextValue(pluginAction.props['msgBody'])
		}

		#populate optional parameters
		if self.present(pluginAction.props['msgDevice']):
			params['device'] = pluginAction.props['msgDevice'].strip()

		if self.present(pluginAction.props['msgUser']):
			params['user'] = pluginAction.props['msgUser'].strip()

		if self.present(pluginAction.props['msgSound']):
			params['sound'] = pluginAction.props["msgSound"].strip()

		if self.present(pluginAction.props['msgSupLinkTitle']):
			params['url_title'] = self.prepareTextValue(pluginAction.props['msgSupLinkTitle'])

		if self.present(pluginAction.props['msgSupLinkUrl']):
			params['url'] = self.prepareTextValue(pluginAction.props['msgSupLinkUrl'])

		if self.present(pluginAction.props['msgPriority']):
			params['priority'] = pluginAction.props['msgPriority']
			if params['priority'] == 2 or params['priority'] == "2":
				# Require Confirmation priority requires 2 additional params:
				params['retry'] = "600"		# show every 10 minutes until confirmted (could expose UI for this...)
				params['expire'] = "86400"	# set expire to maximum (24 hours)

		conn = httplib.HTTPSConnection("api.pushover.net:443")
		conn.request(
			"POST",
			"/1/messages.json",
			urllib.urlencode(params),
			{"Content-type": "application/x-www-form-urlencoded"}
		)
		self.debugLog(u"Result: %s" % conn.getresponse().read())
		conn.close()
