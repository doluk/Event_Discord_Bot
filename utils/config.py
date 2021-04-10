import json
import os


class ClassIterator:
    '''makes arbitrary classes iterable by iterating over their __dict__
    Parameters
    ----------
        class_instance
            an instance of any class
    '''

    def __init__(self, class_instance):
        self.iter = class_instance.__dict__.__iter__()

    def __next__(self):
        return self.iter.__next__()


CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

class ConfigObj:
    '''class to hold one layer of the bot configuration. It's elements may be other ConfigObj's
    Methods
    -------
        get
            alias function to mask ConfigObj.element as ConfigObj.get('element')
        to_dict
            recursively transform this class and all sub-classes to a dictionary
    '''

    def __init__(self, **kwargs):
        self.__dict__.update({k: ConfigObj(**v) if isinstance(v, dict) else v
                              for k, v in kwargs.items()})

    def __iter__(self):
        ''' Returns the Iterator object '''
        return ClassIterator(self)


    def __getitem__(self, key: str):
        '''allows accessing attributes via ConfigObj[attribute]
        '''

        return self.__dict__[key]


    def get(self, key: str, default=None):
        '''alias function to mask ConfigObj.element as ConfigObj.get('element')
        '''

        return self.__dict__.get(key, default)


    def to_dict(self) -> dict:
        '''recursively transform this class and all sub-classes to a dictionary
        Returns
        -------
            dict
        '''

        return {k: v.to_dict() if isinstance(v, ConfigObj) else v
                for k, v in self.__dict__.items()}


class Config:
    '''class to represent the bot configuration
    Methods
    -------
        from_json
            read a json file and recursively represent it's entries as class attributes
        to_json
            write the current config state to a json file, overwriting the path
    '''

    def __init__(self):
        pass

    def load(self, path: str = CONFIG_PATH) -> None:
        """read a json file and recursively represent it's entries as class attributes
        Parameters
        ----------
            path: string
                the path to the json file
        """

        # read the json file
        with open(path) as fp:
            d = json.load(fp)

        # convert json to class attributes
        d = {k: ConfigObj(**v) if isinstance(v, dict) else v for k, v in d.items()}

        # clear all existing config and update with the new data. This allows for mid-run updates
        # by re-running the .load-method
        self.__dict__.clear()
        self.__dict__.update(d)

    def from_json(self, path: str) -> None:
        '''read a json file and recursively represent it's entries as class attributes
        Parameters
        ----------
            path: string
                the path to the json file
        '''

        # read the json file
        with open(path) as fp:
            d = json.load(fp)

        # convert json to class attributes
        d = {k: ConfigObj(**v) if isinstance(v, dict) else v for k, v in d.items()}

        # clear all existing config and update with the new data. This allows for mid-run updates
        # by re-running the .from_json-method
        self.__dict__.clear()
        self.__dict__.update(d)


    def to_json(self, path: str) -> None:
        '''write the current config state to a json file, overwriting the path
        Parameters
        ----------
            path: string
                the path to the json file
        '''

        # convert the class to a dictionary
        d = {k: v.to_dict() if isinstance(v, ConfigObj) else v
             for k, v in self.__dict__.items()}

        # write to a json file
        with open(path, 'w+') as outfile:
            json.dump(d, outfile, indent=2)

config = Config()
config.load(CONFIG_PATH)