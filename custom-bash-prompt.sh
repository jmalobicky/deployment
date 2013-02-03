#!/bin/sh
PS1="[\u@\H \W]"

case `id -u` in
0) PS1="${PS1}# ";;
*) PS1="${PS1}$ ";;
esac

export PS1
