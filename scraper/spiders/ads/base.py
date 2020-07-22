

class BaseParser:

    category_mapping: dict = {}

    source:str

    def __init__(self, source):
        self.source = source

    def get_category_tree(self, bc_category):
        for category in self.category_mapping:
            for bc_category_name in self.category_mapping[category]:
                if bc_category == bc_category_name:
                    return (category, self.category_mapping[category][bc_category_name],)

        return ('Misceláneas', 'Otros',)

    def clean_phone(self, phone):
        cleaned_phone = phone.lower().split('y')[0].split('o')[0].split('ó')[0].split(',')[0].split('/')[0].strip()
        if len(cleaned_phone) > 17:
            cleaned_phone = cleaned_phone.split('.')[0].strip()
        if len(cleaned_phone) > 17:
            cleaned_phone = cleaned_phone.split('-')[0].split('—')[0].strip()
        if len(cleaned_phone) > 17:
            cleaned_phone = cleaned_phone.split(' ')[0].strip()
        return cleaned_phone
