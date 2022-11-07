from configparser import ConfigParser

config = ConfigParser()
path = './config/config.ini'

class AppConfig:
    
    def __init__(self):        
        config.read(path)
        self.keywords_context_before = config['Keywords']['ContextBefore']
        self.keywords_context_after = config['Keywords']['ContextAfter']

    def save(self):
        config.read(path)
        config['Keywords']['ContextBefore'] = self.keywords_context_before
        config['Keywords']['ContextAfter'] = self.keywords_context_after
        with open(path, 'w') as configfile:
            config.write(configfile)


def main():
    config = AppConfig()

if __name__ == '__main__':
    main()
