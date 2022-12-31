import json
import os

class MasterData():
    '''
    Class to help read the Master data
    Place in same file as Master (for now, TODO read from github or something)
    '''
    def __init__(self) -> None:
        self.textdata = self.get_textdata()
        # I have no idea if it's worth saving opened json data
        # vs opening them every time but once open it loads in data
        self.data = {} 
        # maybe make a data dictionary class
        
    def open_MB(self, dataMB: str):
        path = os.path.dirname(os.path.realpath(__file__))  # dir of script
        path = path + f'\\Master\\{dataMB}'
        if not path.endswith('.json'):
            path = path + '.json'
        with open(path, encoding='utf-8') as f:
            return json.load(f)             

    def get_textdata(self):
        return self.open_MB('TextResourceMB')

    def add_data(self, dataMB: str):
        self.data[dataMB] = self.open_MB(dataMB)

    def search_string_key(self, text_key: str, language: str = 'enUS')->str:
        '''
        Returns the text string for selected region

        language:
            English - enUS
            Japanese - jaJP
            Korean - koKR
            Taiwanese - zhTW
        '''

        obj = filter(lambda x:x["StringKey"]==text_key, self.textdata)
        try:
            return next(obj)[language]
        except StopIteration:
            return None

    def search_id(self, id: int, data: dict):
        obj = filter(lambda x:x["Id"]==id, data)
        try:
            return next(obj)
        except StopIteration:
            return None   

    def search_chars(self, *, \
        id: int=None, type: int=None, rarity: int=None, job: int=None):
        '''
        Returns a iterator of characters matching search conditions
        '''
        if 'CharacterMB' not in self.data:
            self.add_data('CharacterMB')
        if id:  # unique
            char = filter(lambda x:x["Id"]==id, self.data['CharacterMB'])
            return char

        if type:
            char = filter(lambda x:x["ElementType"]==type, self.data['CharacterMB'])
        if rarity:
            char = filter(lambda x:x["RarityFlags"]==rarity, char)
        if job:
            char = filter(lambda x:x["JobFlags"]==job, char)
        return char


    def search_item(self, id: int, type: str):
        if 'ItemMB' not in self.data:
            self.add_data('ItemMB')
        obj = filter(lambda x:x["ItemId"]==id and x['ItemType']==type,\
            self.data['ItemMB'])
        try:
            return next(obj)
        except StopIteration:
            return None

    def find_item(self, id: int, type: str) -> dict:
        if type == 14:
            if 'SphereMB' not in self.data:
                self.add_data('SphereMB')
            item = self.search_id(id, self.data['SphereMB'])
        elif type == 17:
            if 'TreasureChestMB' not in self.data:
                self.add_data('TreasureChestMB')
            item = self.search_id(id, self.data['TreasureChestMB'])
        else:
            item = self.search_item(id, type)

        if item is None:
            print('Item not found')
        return item

    def print_reward(self, reward: dict):
        '''
        Input Reward obj
        Reward{
            ItemCount
            ItemId
            ItemType
        }
        '''
        item = self.find_item(reward['ItemId'], reward['ItemType'])
        if item is None:
            return
        item_name = self.search_string_key(item['NameKey'])

        if reward['ItemType'] == 14:  # runes
            lv = str(item["Lv"])
            item_name = item_name + ' Lv.' + lv
        
        print(f'{item_name} | {reward["ItemCount"]}')

    def print_mission(self, mission: dict):
        print(self.search_string_key(mission['NameKey']))
        for item in mission['RewardList']:
            self.print_reward(item['Item'])
