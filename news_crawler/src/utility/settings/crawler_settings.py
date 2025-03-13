import os
from typing import Dict, Optional

from omegaconf import DictConfig
from omegaconf import OmegaConf as OmegaConfig

from news_crawler.src.utility.error import (ConfigFormatterMisMatchError,
                                            ConfigIsEmptyError,
                                            ConfigNameNotExistError,
                                            ConfigNotFoundError)


class ConfigHandler:
    """
        Xử lý cấu hình của các file config
    Attributes:
        base_dir (str): Folder chứa file config _ './src/config'
        config_name (str): Tên file config phải kết thúc bằng .yaml hoặc yaml _ 'firecrawler.yaml'
        config (dict): Dữ liệu config đã được load
        
    Methods:
        get_config: Lấy cấu hình của bộ config.
        update_config: Cập nhật cấu hình với giá trị mới.
        merge_cfg: Cập nhật thêm các cấu hình liên quan tới cấu hình hiện tại.
        save_config: Lưu cấu hình hiện tại vào file .yaml hoặc.yml
        
    """
    def __init__(
        self,
        base_dir: Optional[str| None] = None,
        config_name: Optional[str | None] = None,
        config_dict: Optional[Dict | None] = None,
    ):
        super(ConfigHandler, self).__init__()
        self.base_dir = base_dir
        self.config_name = config_name
        self.config_dict = config_dict
        
        # Xử lý lỗi khi config_name bị None
        if self.config_name is None or not (
            self.config_name.endswith('.yaml') or self.config_name.endswith('.yml')
        ):
            raise ConfigNameNotExistError(error_root = self.config_name)
        
        config_path = os.path.join(self.base_dir, self.config_name) if self.base_dir is not None else None
        
        if config_path and not os.path.exists(config_path):    
            print(ConfigNotFoundError(error_root = self.config_name))
            if self.config_dict is not None:
                self.config = OmegaConfig.create(self.config_dict)
            else:
                print(ConfigIsEmptyError(error_root = self.config_name))
                self.config = OmegaConfig.create({})
                
        elif config_path is not None and os.path.exists(config_path):
            
            load_conf = OmegaConfig.load(config_path)  # noqa
            if isinstance(load_conf, DictConfig):
                self.config = load_conf
            else:
                raise ConfigFormatterMisMatchError(error_root=config_path)
    
    def get_cfg(self, key: str, default = None):
        return OmegaConfig.select(self.config, key=key, default = default)
    
    def update_cfg(self, key: str, value):  # noqa: C901
        """
        Example usage:
            với cfg = self.config
            cfg.update_cfg("firecrawl.log_info", "infos")
        Update trực tiếp vào key: firecrawl 
        """
        return OmegaConfig.update(self.config, key, value, merge=True)

    def merge_cfg(self, new_config: dict):
        """
        New_config sẽ có cấu trúc của 1 dictionary
        """
        return OmegaConfig.merge(self, new_config)

    def to_dict(self):
        
        return OmegaConfig.to_container(self.config, resolve=True)

    def to_yaml(self):
        return OmegaConfig.to_yaml(self)

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.to_yaml())


# Testcase

# from news_crawler.src.utility.settings import ConfigHandler
# ConfigHandler(base_dir = './src/config', config_name = 'firecrawler.yaml').get_cfg('firecrawl')
