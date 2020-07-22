# statusbar
a simple statusbar for dwm, tmux, etc.


## The problem

I wrote a script that populates my tmux statusbar. Now, if I have 10 tmux
sessions in the background, I have 10 statusbar scripts running too.


## The solution

A statusbar "server". A single process running in the background from which a
statusbar can request data.

You can have many instances of the statusbar with (basically) no
additional overhead.


## Usage

Once statusd is installed, you can use the `statusbar` command to add a fancy
statusbar anywhere that accepts **stdin**.


### Examples

dwm:
```
while true; do
    xsetroot -name "$(statusbar)"
    sleep 1
done&
```

tmux:
```
set -g status-interval 1
set -g status-right "#(statusbar)"
```


## Install

statusd / statusbar uses `make` as a build system. Use:

```
sudo make install
```

Installation requires root.


## Uninstall

```
sudo make uninstall
```
