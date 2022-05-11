indigo-pushover
===============

[Indigo](http://www.indigodomo.com/) plugin  - send push notifications via [Pushover](http://www.pushover.net).

| Requirement            |                     |   |
|------------------------|---------------------|---|
| Minimum Indigo Version | 2022.1              |   |
| Python Library (API)   | Official            |   |
| Requires Local Network | No                  |   |
| Requires Internet      | Yes                 |   |
| Hardware Interface     | None                |   |

### Requirements

2. Valid Pushover [API key](https://pushover.net/apps/clone/indigo_domotics)
3. Valid Pushover [user key](https://pushover.net/faq#overview-what)

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
