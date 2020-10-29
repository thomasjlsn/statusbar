# pybar
a simple statusbar for dwm, tmux, etc.


## The problem

I wrote a script that populates my tmux statusbar. Now, if I have 10 tmux
sessions in the background, I have 10 statusbar scripts running too.


## The solution

A statusbar "server". A single process running in the background from which a
statusbar can request data.

You can have many instances of a statusbar with (basically) no additional
overhead.


## Usage

Use the `pybar` command to add a fancy statusbar anywhere that accepts
**stdin**.


### Examples

dwm:
```
while true; do
    xsetroot -name "$(pybar)"
    sleep 1
done&
```

tmux:
```
set -g status-interval 1
set -g status-right "#(pybar)"
```


## Install

Pybar uses `make` as a build system.

For a basic install, use:

```
sudo make install
```

Additionally, if you are on Arch Linux, pybar has a pacman module, which shows
available updates. For it to work properly, a pacman post-transaction hook must
be installed also.

To install pybar with pacman support, use:

```
sudo make arch-install
```

## Uninstall

```
sudo make uninstall
```

If you are on Arch:

```
sudo make arch-uninstall
```
