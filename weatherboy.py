#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
# Example: python weatherboy.py -l 22664159 -u c -d 30 -a

import gtk
import gobject
import time
import webbrowser
from urllib2 import urlopen, URLError
from argparse import ArgumentParser
from xml.dom import minidom

parser = ArgumentParser(description='Simple weather applet', epilog='Written by Roman Komkov and updated at 06.06.2012.\nPlease, report bugs to <r.komkov@gmail.com>')
parser.add_argument('-l', '--location', required=True, metavar='WOEID', help='location WOEID (more on http://developer.yahoo.com/weather/)')
parser.add_argument('-u', '--units', choices=['c','f'], default='c', metavar='c|f', help='units to display')
parser.add_argument('-d', '--delta', default='10', type=int, metavar='N', help='timeout in minutes between next weather data query')
parser.add_argument('-a', '--advanced', action = 'store_true', default=False, help='Advanced tooltip')

class Api:
    def __init__(self, location, units):
        self.params = (location,units)
        self.url = 'http://xml.weather.yahoo.com/forecastrss?w=%s&u=%s'
        self.namespace = 'http://xml.weather.yahoo.com/ns/rss/1.0'
        self.website = 'http://weather.yahoo.com/'

        self.codes = { #code:icon name
            '0':'weather-severe-alert',
            '1':'weather-severe-alert',
            '2':'weather-severe-alert',
            '3':'weather-severe-alert',
            '4':'weather-storm',
            '5':'weather-snow-rain',
            '6':'weather-snow-rain',
            '7':'weather-snow',
            '8':'weather-freezing-rain',
            '9':'weather-fog',
            '10':'weather-freezing-rain',
            '11':'weather-showers',
            '12':'weather-showers',
            '13':'weather-snow',
            '14':'weather-snow',
            '15':'weather-snow',
            '16':'weather-snow',
            '17':'weather-snow',
            '18':'weather-snow',
            '19':'weather-fog',
            '20':'weather-fog',
            '21':'weather-fog',
            '22':'weather-fog',
            '23':'weather-few-clouds',
            '24':'weather-few-clouds',
            '25':'weather-few-clouds',
            '26':'weather-overcast',
            '27':'weather-clouds-night',
            '28':'weather-clouds',
            '29':'weather-few-clouds-night',
            '30':'weather-few-clouds',
            '31':'weather-clear-night',
            '32':'weather-clear',
            '33':'weather-clear-night',
            '34':'weather-clear',
            '35':'weather-snow-rain',
            '36':'weather-clear',
            '37':'weather-storm',
            '38':'weather-storm',
            '39':'weather-storm',
            '40':'weather-showers-scattered',
            '41':'weather-snow',
            '42':'weather-snow',
            '43':'weather-snow',
            '44':'weather-few-clouds',
            '45':'weather-storm',
            '46':'weather-snow',
            '47':'weather-storm',
            '3200':'stock-unknown'
        }

    def conv_direction(self, value):
        value = Decimal(value)
        if value >= 0 and value < 22.5:
            return u'\u2193 (N)'
        elif value >= 22.5 and value < 67.5:
            return u'\u2199 (NE)'
        elif value >= 67.5 and value < 112.5:
            return u'\u2190 (E)'
        elif value >= 112.5 and value < 157.5:
            return u'\u2196 (SE)'
        elif value >= 157.5 and value < 202.5:
            return u'\u2191 (S)'
        elif value >= 202.5 and value < 247.5:
            return u'\u2197 (SW)'
        elif value >= 247.5 and value < 292.5:
            return u'\u2192 (W)'
        elif value >= 292.5 and value < 337.5:
            return u'\u2198 (NW)'
        else:
            return u'\u2193 (N)'

    def get_data(self):
        try:
            url = self.url % self.params
            dom = minidom.parse(urlopen(url))
            units_node = dom.getElementsByTagNameNS(self.namespace, 'units')[0]
            units = {'temperature': units_node.getAttribute('temperature'),
                    'distance': units_node.getAttribute('distance'),
                    'pressure': units_node.getAttribute('pressure'),
                    'speed': units_node.getAttribute('speed')}
            forecasts = []
            for node in dom.getElementsByTagNameNS(self.namespace, 'forecast'):
                forecasts.append({
                    'date': node.getAttribute('date'),
                    'low': node.getAttribute('low')+u'\u00B0 '+units['temperature'],
                    'high': node.getAttribute('high')+u'\u00B0 '+units['temperature'],
                    'condition': node.getAttribute('text'),
                    'icon': self.codes.get(node.getAttribute('code'))
                })
            condition = dom.getElementsByTagNameNS(self.namespace, 'condition')[0]
            location = dom.getElementsByTagNameNS(self.namespace, 'location')[0]
            wind = dom.getElementsByTagNameNS(self.namespace, 'wind')[0]
            atmosphere = dom.getElementsByTagNameNS(self.namespace, 'atmosphere')[0]
            return {
                'current_condition': condition.getAttribute('text'),
                'current_icon': self.codes.get(condition.getAttribute('code')),
                'current_temp': condition.getAttribute('temp')+u'\u00B0 '+units['temperature'],
                'extra':{
                'wind': {'direction':self.conv_direction(wind.getAttribute('direction')),
                            'speed':wind.getAttribute('speed')+' '+units['speed']},
                'atmosphere': {'humidity':atmosphere.getAttribute('humidity')+'%',
                                'visibility':atmosphere.getAttribute('visibility')+' '+units['distance'],
                                'pressure':atmosphere.getAttribute('pressure')+' '+units['pressure']}},
                'forecasts': forecasts,
                'location' : {'city' : location.getAttribute('city'),'country' : location.getAttribute('country')}
            }
        except URLError, ex:
            return None

class MainApp:
    def __init__(self,args):
        self.args = args
        self.weather = None
        self.tooltip = None
        self.tray = gtk.StatusIcon()
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.connect('activate', self.on_left_click)
        self.tray.set_has_tooltip(True)
        if self.args.advanced:
            self.tray.connect('query-tooltip', self.on_tooltip_advanced)
        self.api = Api(self.args.location, self.args.units)
        self.update_tray()
        gobject.timeout_add_seconds(self.args.delta * 60, self.update_tray)

    def on_tooltip_advanced(self, widget, x, y, keyboard_mode, tooltip):
        #if self.tooltip:
            #tooltip.set_text(self.tooltip)
        if self.weather:
            weather = self.weather
            tooltip_text = '%s\n%s' % (self.weather['current_temp'],self.weather['current_condition'])
            vbox = gtk.VBox()
            header = gtk.Label()
            header.set_markup('<u><b>'+self.weather['location']['city']+', '+self.weather['location']['country']+'</b></u>')
            header.set_alignment(1.0, 0.5)
            separator_h = gtk.HSeparator()
            hbox = gtk.HBox()
            now_image = gtk.Image()
            now_image.set_padding(0,5)
            now_image.set_pixel_size(48)
            now_image.set_from_icon_name(weather['current_icon'],48)
            now_label = gtk.Label()
            now_label.set_markup('<b>'+tooltip_text+'</b>')
            now_label.set_padding(5,5)
            table = gtk.Table(columns=2, homogeneous=False)
            u = 0
            l = 1
            for k,v in self.weather['extra'].iteritems():
                h_label = gtk.Label()
                h_label.set_markup('<b>'+k+'</b>')
                h_label.set_alignment(0.0, 0.5)
                h_label.set_padding(5,0)
                table.attach(h_label,0,1,u,l)
                for i,j in v.iteritems():
                    u +=1
                    l +=1
                    k_label = gtk.Label(i)
                    k_label.set_alignment(0.0, 0.5)
                    v_label = gtk.Label(j)
                    v_label.set_alignment(0.0, 0.5)
                    table.attach(k_label,0,1,u,l)
                    table.attach(v_label,1,2,u,l)
                u +=1
                l +=1

            hbox.pack_start(now_image, False, False, 0)
            hbox.pack_start(now_label, False, False, 0)
            vbox.pack_start(header, True, False, 0)
            vbox.pack_start(separator_h, False, False, 0)
            vbox.pack_start(hbox, False, False, 0)
            vbox.pack_start(table, False, False, 0)
            vbox.show_all()
            tooltip.set_custom(vbox)
        else:
            tooltip.set_text('Connection error!')
        return True

    def on_refresh(self,widget):
        self.update_tray()

    def on_right_click(self, icon, event_button, event_time):
        menu = gtk.Menu()
        refresh = gtk.MenuItem('Refresh')
        refresh.show()
        refresh.connect('activate', self.on_refresh)
        quit = gtk.MenuItem('Quit')
        quit.show()
        quit.connect('activate', gtk.main_quit)
        menu.append(refresh)
        menu.append(quit)
        menu.popup(None, None, gtk.status_icon_position_menu,
                    event_button, event_time, self.tray)

    def on_left_click(self, widget):
        webbrowser.open(self.api.website)

    def update_tray(self):
        self.weather = self.api.get_data()
        if self.weather != None:
            self.tray.set_from_icon_name(self.weather['current_icon'])
            if not self.args.advanced:
                tooltip_text =  '%s / %s' % (self.weather['current_temp'],self.weather['current_condition'])
                self.tray.set_tooltip_markup(tooltip_text)
        else:
            if not self.args.advanced:
                self.tray.set_tooltip_text('Connection error!')
            self.tray.set_from_stock('gtk-dialog-error')
        return True

if __name__ == "__main__":
    try:
        args = parser.parse_args()
        MainApp(args)
        gtk.main()
    except KeyboardInterrupt:
        pass

