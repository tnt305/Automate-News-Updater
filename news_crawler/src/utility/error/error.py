from news_crawler.src.utility.error import BaseError


class ConfigNotFoundError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='There is no config file in the base directory'):
        super().__init__(error_root, message)

class ConfigNameNotExistError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='Config file  should end with .yaml or yaml'):
        super().__init__(error_root, message)
        
class ConfigIsEmptyError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='Configurations has not been define. Define them yourself'):
        super().__init__(error_root, message)   

class ConfigFormatterMisMatchError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='Expected DictConfig format for OmegaConf for config file'):
        super().__init__(error_root, message)   

class RequestConnectionError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='Expected DictConfig format for OmegaConf for config file'):
        super().__init__(error_root, message)


class FrequencyMismatchError(BaseError):
    def __init__(self,
                 error_root='config_yaml',
                 message='Expected search date in list [daily, monthly, weekly]',
                 *args):
        super().__init__(error_root, message, *args)

# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass
# class ConfigError(BaseError):
#     pass