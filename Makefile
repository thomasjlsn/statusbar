config:
	#
	# Configuring statusd for your OS.
	#
	bash configure.sh

enable-service:
	#
	# Setting up systemd service.
	#
	@cp -fv statusd.service /etc/systemd/system/statusd.service
	@systemctl start statusd.service
	@systemctl enable statusd.service
	@make reload

disable-service:
	#
	# Disabling systemd service.
	#
	@systemctl stop statusd.service
	@systemctl disable statusd.service
	@rm -fv /etc/systemd/system/statusd.service

install:
	#
	# Installing statusd.
	#
	@pip install .
	@make config
	@make enable-service

uninstall:
	#
	# Uninstalling statusd.
	#
	@pip uninstall statusd
	@make disable-service

reload:
	#
	# Reloading daemon, possible warning above is safe to ignore.
	#
	@systemctl daemon-reload
	@systemctl restart statusd.service
