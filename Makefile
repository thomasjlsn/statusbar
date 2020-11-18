all: root install

# ==========================================================================
# User level rules:
#
#     clean            delete files associated with pybar
#
#     install          install pybar
#     uninstall        uninstall pybar
#
#     arch-install     install pybar for arch linux
#     arch-uninstall   uninstall pybar for arch linux
#
# ==========================================================================

clean:
	rm -fv pybar.conf ||:
	rm -fv pybar.service ||:

install: root pip-install enable-service reload

uninstall: root disable-service

arch-install: enable-pacman-hook install

arch-uninstall: disable-pacman-hook uninstall

# ==========================================================================
# Dev level rules:
#
#     Stuff that needs to happen, but does not directly concern the user.
#
# ==========================================================================

config:
	bash gen_service_file.sh
	@cp -fv pybar_config.py /etc/pybar_config.py

disable-pacman-hook:
	@rm -fv /etc/pacman.d/hooks/pybar.hook ||:

enable-pacman-hook:
	@cp -fv pybar.hook /etc/pacman.d/hooks/pybar.hook

disable-service:
	@systemctl stop pybar.service ||:
	@systemctl disable pybar.service ||:
	@rm -fv /etc/systemd/system/pybar.service ||:

enable-service: config
	@cp -fv pybar.service /etc/systemd/system/pybar.service
	@systemctl start pybar.service
	@systemctl enable pybar.service

reload:
	@systemctl daemon-reload
	@systemctl restart pybar.service

pip-install: pip-requirements
	@pip install .

pip-uninstall:
	@pip uninstall pybar --yes

pip-requirements:
	@pip3 install -r requirements.txt

root:
	test `whoami` = 'root'
