from parser import LineType

map = {}

import join
map[LineType.Join] = join

import mode
map[LineType.Mode] = mode

import nick
map[LineType.Nickname] = nick

import part
map[LineType.Part] = part

import ping
map[LineType.Ping] = ping

import topic
map[LineType.Topic] = topic

import user
map[LineType.Username] = user

import who
map[LineType.Who] = who