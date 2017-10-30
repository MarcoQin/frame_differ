#!/usr/bin/env python
# encoding: utf-8

import json

with open("converted.json") as f:
    data = json.loads(f.read())


ss = "return {%s}"

rt = []

for frame in data:
    s = "{%s}"
    s = s % ",".join([str(x) for x in frame])
    rt.append(s)
ss = ss % ",".join(rt)

with open("frames1.lua", "w") as f:
    f.write(ss)
