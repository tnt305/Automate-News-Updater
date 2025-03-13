from abc import ABC, abstractmethod


class BaseScraper(ABC):
    
    @staticmethod
    @abstractmethod
    def get_html(url):
        """Lấy HTML từ trang web - có thể gọi từ class mà không cần instance"""
        pass
    
    @staticmethod
    @abstractmethod
    def save_dict(data):
        """Lưu dữ liệu dưới dạng dictionary - không phụ thuộc vào instance"""
        pass

    @classmethod
    @abstractmethod
    def save_db(cls, data):
        """Lưu dữ liệu vào database - cần instance vì có thể thay đổi theo từng scraper"""
        pass
    
    @abstractmethod
    def extract(self):
        """Trích xuất thông tin - mỗi scraper có cách trích xuất riêng"""
        pass

