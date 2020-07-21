all: root clean install

# ==========================================================================
# User level rules:
#
#     clean      uninstall statusd, delete all associated files
#     install    install statusd
#     uninstall  uninstall statusd
#
# ==========================================================================

clean: root uninstall
	rm -fv statusd.service ||:
	#
	# Restored to clean state.
	#

install: root pip-install enable-service reload
	#
	# Installed statusd.
	#

uninstall: root disable-service
	#
	# Uninstalled statusd.
	#

# ==========================================================================
# Dev level rules:
#
#     Stuff that needs to happen, but does not directly concern the user.
#
# ==========================================================================

config:
	#
	# Configuring statusd for your OS.
	#
	bash configure.sh

disable-service:
	#
	# Disabling systemd service.
	#
	@systemctl stop statusd.service ||:
	@systemctl disable statusd.service ||:
	@rm -fv /etc/systemd/system/statusd.service ||:

enable-service: config
	#
	# Setting up systemd service.
	#
	@cp -fv statusd.service /etc/systemd/system/statusd.service
	@systemctl start statusd.service
	@systemctl enable statusd.service

reload:
	#
	# Reloading daemon, possible warning above is safe to ignore.
	#
	@systemctl daemon-reload
	@systemctl restart statusd.service

pip-install: pip-requirements
	#
	# Installing statusd package
	#
	@pip install .

pip-uninstall:
	#
	# Uninstalling statusd package
	#
	@pip uninstall statusd --yes

pip-requirements:
	#
	# Installing python dependencies.
	#
	@pip3 install -r requirements.txt

root:
	# Operation requires root.
	test `whoami` = 'root'
