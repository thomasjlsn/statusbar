all: root install

# ==========================================================================
# User level rules:
#
#     clean      uninstall pybar, delete all associated files
#     install    install pybar
#     uninstall  uninstall pybar
#
# ==========================================================================

clean:
	rm -fv pybar.service ||:
	#
	# Restored to clean state.
	#

install: root pip-install enable-service reload
	#
	# Installed pybar.
	#

uninstall: root disable-service
	#
	# Uninstalled pybar.
	#

arch-install: enable-pacman-hook install

arch-uninstall: disable-pacman-hook uninstall

# ==========================================================================
# Dev level rules:
#
#     Stuff that needs to happen, but does not directly concern the user.
#
# ==========================================================================

config:
	#
	# Configuring pybar for your OS.
	#
	bash configure.sh

disable-pacman-hook:
	#
	# Disabling pacman post-transaction hook.
	#
	@rm -fv /etc/pacman.d/hooks/pybar.hook ||:

enable-pacman-hook:
	#
	# Setting up pacman post-transaction hook.
	#
	@cp -fv pybar_pacman.hook /etc/pacman.d/hooks/pybar.hook

disable-service:
	#
	# Disabling systemd service.
	#
	@systemctl stop pybar.service ||:
	@systemctl disable pybar.service ||:
	@rm -fv /etc/systemd/system/pybar.service ||:

enable-service: config
	#
	# Setting up systemd service.
	#
	@cp -fv pybar.service /etc/systemd/system/pybar.service
	@systemctl start pybar.service
	@systemctl enable pybar.service

reload:
	#
	# Reloading daemon, possible warning above is safe to ignore.
	#
	@systemctl daemon-reload
	@systemctl restart pybar.service

pip-install: pip-requirements
	#
	# Installing pybar package
	#
	@pip install .

pip-uninstall:
	#
	# Uninstalling pybar package
	#
	@pip uninstall pybar --yes

pip-requirements:
	#
	# Installing python dependencies.
	#
	@pip3 install -r requirements.txt

root:
	# Operation requires root.
	test `whoami` = 'root'
