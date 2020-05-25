PREFIX ?= /usr/local

install:
	@cp -fv statusd.py $(PREFIX)/bin/statusd
	@chmod -v 555 $(PREFIX)/bin/statusd
	@cp -fv statusbar.py $(PREFIX)/bin/statusbar
	@chmod -v 555 $(PREFIX)/bin/statusbar
	@cp -fv statusd.service /etc/systemd/system/statusd.service
	@systemctl start statusd.service
	@systemctl enable statusd.service
	@make reload

reload:
	#
	# Reloading daemon, possible warning above is safe to ignore.
	#
	@systemctl daemon-reload
	@systemctl restart statusd.service
