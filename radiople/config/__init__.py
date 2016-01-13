import configparser
from os import listdir
from os import path


class ConfigItem(object):
    pass

parser = configparser.ConfigParser()

path = path.dirname(path.realpath(__file__))
filenames = [f for f in listdir(path) if f.endswith('.conf')]

config = ConfigItem()


def try_cast(value):
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    elif value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    elif value == 'None':
        return None
    elif '.' in value:
        return float(value)
    else:
        return int(value)

for filename in filenames:
    parser.read(path + '/' + filename)
    context = filename.rsplit('.', 1)[0]
    setattr(config, context, ConfigItem())

    for section in parser.sections():
        raw = getattr(config, context)
        setattr(raw, section, ConfigItem())

        for key, value in parser.items(section):
            value = try_cast(value)
            row = getattr(raw, section)
            setattr(row, key, value)
