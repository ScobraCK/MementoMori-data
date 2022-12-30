from master_data import MasterData

def print_common(event: dict, master_data: MasterData):
    print(master_data.search_string_key(event['TitleTextKey']), '\n')
    #print(master_data.search_string_key(event['SpecialRewardAppealTextKey']), '\n')

    print(f'Start time: {event["StartTime"]}')
    print(f'End time: {event["EndTime"]}', '\n')


def missions(master_data: MasterData):
    mission_data = master_data.open_MB('MissionMB')
    event_data = master_data.open_MB('LimitedMissionMB')

    for event in event_data:
        print_common(event, master_data)

        for missionid in event['TargetMissionIdList']:
            mission = master_data.search_id(missionid, mission_data)
            master_data.print_mission(mission)
            print()


def logins(master_data: MasterData):
    login_data = master_data.open_MB('LimitedLoginBonusMB')
    reward_data = master_data.open_MB('LimitedLoginBonusRewardListMB')
    
    for event in login_data:
        print_common(event, master_data)

        reward_id = event['RewardListId']
        reward = master_data.search_id(reward_id, reward_data)

        print('Daily Rewards')
        for item in reward['DailyRewardList']:
            print(f'Date: {item["Date"]}')
            master_data.print_reward(item['DailyRewardItem'])
            print()

        if reward['ExistEveryDayReward']:
            print('TODO: Code for every day reward')

        if reward['ExistSpecialReward']:
            print('Special Rewards')
            item = reward['SpecialRewardItem']
            print(f'Date: {item["Date"]}')
            master_data.print_reward(item['SpecialRewardItem'])
            print()

if __name__ == '__main__':
    master_data = MasterData()
    #logins(master_data)
    missions(master_data)
    input('Press any key to exit')