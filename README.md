indigo-pushover
===============

[Indigo](http://www.indigodomo.com/) plugin  - send push notifications to mobile devices via [Pushover](http://www.pushover.net).

### Requirements

1. [Indigo 6](http://www.indigodomo.com/) or later (pro version only)
2. Valid Pushover [API key](https://pushover.net/apps/clone/indigo_domotics)
3. Valid Pushover [user key](https://pushover.net/faq#overview-what)

### Installation Instructions

1. Download latest release [here](https://github.com/IndigoDomotics/indigo-pushover/releases)
2. Follow [standard plugin installation process](http://bit.ly/1e1Vc7b)

### Actions Supported
* Send Pushover Notification
	* customize title, message (supports variables)
	* limit to just one specific device (optional)
	* override notification sound
	* set message priority
	* configure supplemental link and title
	* attach images (jpeg only, must be less than 2.5mb, supports variables)

* Cancel Pushover Emergency-Priority Notification
	* tag (included in previous emergency notifications - will cancel all retries with that tag)
