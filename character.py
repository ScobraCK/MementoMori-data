from master_data import MasterData
import file_data

def get_character_info(id: int, masterdata: MasterData) -> dict:
    char_data = next(masterdata.search_chars(id=id))
    char = {}

    char['Id'] = char_data['Id']
    char['Title'] = masterdata.search_string_key(char_data['Name2Key'])
    char['Name'] = masterdata.search_string_key(char_data['NameKey'])
    char['Element'] = file_data.soul_map[char_data['ElementType']]
    char['Base Rarity'] = file_data.rarity_map[char_data['RarityFlags']]
    char['Class'] = file_data.job_map[char_data['JobFlags']]
    char['Base Speed'] = char_data['InitialBattleParameter']['Speed']

    return char

# testing
if __name__ == "__main__":
    master = MasterData()
    char = get_character_info(1, master)
    print(char)