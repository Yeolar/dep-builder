#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 Yeolar
#

import multiprocessing
import os
import sys

BUILD = False
REFRESH_SH = True

SHELL_TPL = """#!/bin/sh

if [ ! -f %(file)s ]; then
    wget %(url)s
fi
rm -rf %(key)s
%(extract)s
cd %(key)s
%(cmds)s
"""

class Dependency(object):

    EXTRACT = dict((
        ('', ''),
        ('.zip', 'unzip %(file)s'),
        ('.tar.gz', 'tar xzf %(file)s'),
    ))

    def __init__(self, first_line):
        self.key, _, url = first_line.partition(':')
        self.url = url.strip()
        self.file = self.url.split('/')[-1]
        base, ext = os.path.splitext(self.file)
        self.sh = base + '.sh'
        self.extract = self.EXTRACT[ext]
        self.dest = os.path.join(os.getcwd(), 'usr', 'local')
        self._cmds = []

    def __str__(self):
        return self.key + ': ' + self.url

    def add_command(self, cmd):
        cmd = cmd.strip()
        if cmd.startswith('cmake'):
            self._cmds.append('mkdir _build && cd _build')
            self._cmds.append('cmake -DCMAKE_PREFIX_PATH=%(dest)s' + cmd[5:])
        else:
            self._cmds.append(cmd)

    def generate(self):
        self._cmds.append('make -j%d' % multiprocessing.cpu_count())
        self._cmds.append('make DESTDIR=%(dest)s install')
        self.cmds = '\n'.join(self._cmds)
        return SHELL_TPL % self.__dict__ % self.__dict__

deps = []

with open(sys.argv[1]) as fp:
    lines = [line.rstrip() for line in fp.readlines()]

for line in lines:
    if line.startswith('#'):
        continue
    if len(line) > 0:
        if line[0] != ' ':
            deps.append(Dependency(line))
        else:
            deps[-1].add_command(line)

for dep in deps:
    if not os.path.exists(dep.sh) or REFRESH_SH:
        with open(dep.sh, 'w') as fp:
            fp.write(dep.generate())
if BUILD:
    for dep in deps:
        os.system('sh ' + dep.sh)
