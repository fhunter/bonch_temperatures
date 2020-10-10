#!/usr/bin/python
# coding=utf-8

" Temperature monitoring server side script "

import os.path
import glob
import socket
import bottle
from bottle import route, view, request, response, redirect
import rrdtool

BASENAME = "/temperature/"

@route('/')
def main():
    " Main page, redirects to proper parameters "
    redirect(BASENAME+'/i/w/')

@route('/<grouped:re:[g|i]>/<period:re:[d|w|m|y]>/')
@view('mainpage')
def main_grouped(grouped, period):
    " Main page, returns links to graphs generated from RRD databases "
    names = glob.glob("./rrd/*.rrd")
    names.sort()
    new_names = []
    for i in names:
        new_names.append(i.replace('./rrd/', '').replace('.rrd', ''))
    return dict(names=new_names, basename=BASENAME, grouped=grouped, period=period)


@route('/graph/<grouped:re:[g|i]>/<period:re:[d|w|m|y]>/<name>')
def graph(name,grouped,period):
    " Graph endpoint, returns generated graph "
    pd = "-1"+period
    if grouped == "i":
        test = rrdtool.graphv("-", "--start", pd, "-w 800", "--title=Температуры %s" % name,
                              "-u 60", "-l 15",  
                              "DEF:cpu_temp=rrd/%s.rrd:ds0:MAX" % name,
                              "DEF:hdd_temp=rrd/%s.rrd:ds1:MAX" % name,
                              "LINE1:cpu_temp#0000FF:Процессор",
                              "LINE2:hdd_temp#FF0000:Диск\\j",
                              "CDEF:unavailable=hdd_temp,UN,INF,0,IF",
                              "AREA:unavailable#f0f0f0",
                              "GPRINT:cpu_temp:MAX:Максимум\\: процессор\\: %3.0lf °C",
                              "GPRINT:hdd_temp:MAX:жёсткий диск\\: %3.0lf °C\\j",
                              "GPRINT:cpu_temp:MAX:Текущий\\: процессор\\: %3.0lf °C",
                              "GPRINT:hdd_temp:MAX:жёсткий диск\\: %3.0lf °C\\j"
                             )
    else:
        names = glob.glob("./rrd/%s*.rrd" % name)
        names.sort()
        new_names = []
        for i in names:
            new_names.append(i.replace('./rrd/', '').replace('.rrd', ''))
	arguments = ("-", "--start", pd, "-w 800", "--title=Температуры %s" % name, "-u 60", "-l 15")
	j=1
	for i in new_names:
	    new_arguments = ( "DEF:cpu_temp%d=rrd/%s.rrd:ds0:MAX" % (j,i),
                              "DEF:hdd_temp%d=rrd/%s.rrd:ds1:MAX" % (j,i),
                              "LINE%d:cpu_temp%d#0000FF:Процессор" % (j,j),
                              "LINE%d:hdd_temp%d#FF0000:Диск\\j" % (j*2+1,j),
                              "GPRINT:cpu_temp%d:MAX:Максимум\\: процессор\\: %%3.0lf °C" %(j),
                              "GPRINT:hdd_temp%d:MAX:жёсткий диск\\: %%3.0lf °C\\j" % (j),
                              "GPRINT:cpu_temp%d:MAX:Текущий\\: процессор\\: %%3.0lf °C" % (j),
                              "GPRINT:hdd_temp%d:MAX:жёсткий диск\\: %%3.0lf °C\\j" %(j))
            j=j+1
	    arguments = arguments + new_arguments
        test = rrdtool.graphv(*arguments)
    response.set_header('Content-type', 'image/png')
    return str(test['image'])

@route('/post', method='POST')
def accept_temperature():
    " Temperature receiving backend "
    ip_address = request.environ.get("REMOTE_ADDR")
    host_name = request.environ.get("REMOTE_HOST")
    if host_name is None:
        host_name = socket.gethostbyaddr(ip_address)[0]
    rrdname = "./rrd/%s.rrd" % host_name
    if not os.path.exists(rrdname):
        rrdtool.create(rrdname, '--start', 'now',
                       '--step', '600',
                       'DS:ds0:GAUGE:1200:-273:5000',
                       'RRA:AVERAGE:0.5:1:1200',
                       'RRA:MIN:0.5:1:1200',
                       'RRA:MAX:0.5:1:1200',
                       'DS:ds1:GAUGE:1200:-273:5000',
                       'RRA:AVERAGE:0.5:1:1200',
                       'RRA:MIN:0.5:1:1200',
                       'RRA:MAX:0.5:1:1200'
                      )
    hdd_temps = request.json['hdd']
    max_hdd = float('-inf')
    max_cpu = float('-inf')
    if hdd_temps:
        max_hdd = float(hdd_temps[0])
        for i in hdd_temps:
            i = float(i)
            if i > max_hdd:
                max_hdd = i
    cpu_temps = request.json['cpu']
    if cpu_temps:
        max_cpu = float(cpu_temps[0])
        for i in cpu_temps:
            i = float(i)
            if i > max_cpu:
                max_cpu = i
    rrdtool.update(rrdname, 'N:%s:%s' % (max_cpu, max_hdd))
    return dict()


bottle.run(server=bottle.CGIServer)
