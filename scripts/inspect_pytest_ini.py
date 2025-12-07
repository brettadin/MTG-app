import configparser
config = configparser.ConfigParser()
config.read('pytest.ini')
print('Sections:', config.sections())
print('Has pytest section:', 'pytest' in config.sections())