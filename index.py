#!/usr/bin/python
# coding=utf-8

import bottle
import os.path
import glob
from bottle import route, view, request, template, static_file, response, abort, redirect
import rrdtool
import socket

basename="/temperature/"

@route('/')
@view('mainpage')
def main():
	names = glob.glob("./rrd/*.rrd")
	new_names = []
	for i in names:
	    new_names.append(i.replace('./rrd/','').replace('.rrd',''))
	return dict(names=new_names,basename=basename)

@route('/graph/<name>')
def graph(name):
	test = rrdtool.graphv("-", "--start", "-1m", "-w 800", "--title=Температуры %s" % name, 
	                      "DEF:cpu_temp=rrd/%s.rrd:ds0:MAX" % name,
	                      "DEF:hdd_temp=rrd/%s.rrd:ds1:MAX" % name,
			      "LINE1:cpu_temp#0000FF:Процессор",
			      "LINE2:hdd_temp#00FFFF:Диск\j",
			      "GPRINT:cpu_temp:MAX:Максимум\: процессор\: %3.0lf °C",
			      "GPRINT:hdd_temp:MAX:жёсткий диск\: %3.0lf °C\j",
			      "GPRINT:cpu_temp:MAX:Текущий\: процессор\: %3.0lf °C",
			      "GPRINT:hdd_temp:MAX:жёсткий диск\: %3.0lf °C\j"
			     )
	return str(test['image'])

@route('/post',method='POST')
def accept_temperature():
        ip = request.environ.get("REMOTE_ADDR")
        hostname = request.environ.get("REMOTE_HOST")
        if hostname == None:
                hostname = socket.gethostbyaddr(ip)[0]
	rrdname = "./rrd/%s.rrd" % hostname
	try:
		os.stat(rrdname)
	except:
		rrdtool.create(rrdname,'--start', 'now', 
			       '--step', '420', 
			       'RRA:AVERAGE:0.5:1:1200', 
			       'DS:ds0:GAUGE:600:-273:5000',
			       'DS:ds1:GAUGE:600:-273:5000'
			       )
        hdd_temps = request.json['hdd']
	if hdd_temps:
		max_hdd = int(hdd_temps[0])
		for i in hdd_temps:
			i = int(i)
			if i > max_hdd:
				max_hdd = i
		rrdtool.update(rrdname, '-tds1', 'N:%s' % max_hdd)
        cpu_temps = request.json['cpu']
	if cpu_temps:
		max_cpu = int(cpu_temps[0])
		for i in cpu_temps:
			i = int(i)
			if i > max_cpu:
				max_cpu = i
		rrdtool.update(rrdname, '-tds0', 'N:%s' % max_cpu)
	return dict()


bottle.run(server=bottle.CGIServer)

