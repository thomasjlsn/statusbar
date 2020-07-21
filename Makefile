install:
	@pip install .
	@cp -fv service_files/statusd.service /etc/systemd/system/statusd.service
	@systemctl start statusd.service
	@systemctl enable statusd.service
	@make reload

uninstall:
	@pip uninstall statusd

reload:
	#
	# Reloading daemon, possible warning above is safe to ignore.
	#
	@systemctl daemon-reload
	@systemctl restart statusd.service
