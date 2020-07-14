import scrapy


class BaseSpider(scrapy.Spider):

    name:str
    source:str

    category_mapping:dict = {}

    def get_category_tree(self, bc_category):
        for category in self.category_mapping:
            for bc_category_name in self.category_mapping[category]:
                if bc_category == bc_category_name:
                    return (category, self.category_mapping[category][bc_category_name],)

        return ('Misceláneas', 'Otros',)

    def clean_phone(self, phone):
        return phone.lower().split('y')[0].split('o')[0].split('ó')[0].split(',')[0].strip()