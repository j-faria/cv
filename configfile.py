# file configfile.py
# create a custom INI file reader and read a file
import configparser

class iniReader(configparser.ConfigParser):

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

cfg = iniReader()

filename = 'info.ini'
cfg.read(filename)
# options is a dictionary -> access variables like options[section][parameter]
options = cfg.as_dict()
