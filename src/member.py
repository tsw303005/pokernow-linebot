from linebot import LineBotApi
from dotenv import load_dotenv
import os

class Member(object):
    def __init__(self) -> None:
        load_dotenv()

        # make sure that download folder exists, ledger and record folder
        self.__fileFolder = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(self.__fileFolder):
            os.makedirs(self.__fileFolder)
            
        self.__memberFile = os.path.join(self.__fileFolder, 'members.txt')
        if not os.path.exists(self.__memberFile):
            f = open(self.__memberFile, 'w')
            f.close()

        # line_bot_api
        self.__line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))

    @staticmethod
    def GET_ALL_NICKNAME() -> list:
        filePath = os.path.join(os.path.join(os.getcwd(), 'files'), 'members.txt')
        if not os.path.exists(filePath):
            return list()
        
        result = list()
        with open(filePath, 'r') as f:
            for line in f.readlines():
                nickName = line.rstrip('\n').split(' ')[1]
                result.append(nickName)

        return result
            
    def __checkID(self, id) -> bool:
        with open(self.__memberFile, 'r') as f:
            for line in f.readlines():
                s = line.rstrip('\n')
                spl = s.split(' ')
                if (spl[0] == id):
                    return True
        
        return False
    
    def __checkNameValidation(self, name) -> bool:
        with open(self.__memberFile, 'r') as f:
            for line in f.readlines():
                line = line.rstrip('\n')
                spl = line.split(' ')
                name = name.lower()
                if name in spl[1].lower() or spl[1].lower() in name:
                    return True
            
        return False
    
    def getMembers(self) -> str:
        result = str()

        with open(self.__memberFile, 'r') as f:
            for line in f.readlines():
                nickName = line.rstrip('\n').split(' ')[1]
                userName = line.rstrip('\n').split(' ')[2]
                result += f'{nickName}: {userName}\n'

        return result

    def checkMemberExist(self, name) -> str:
        with open(self.__memberFile, 'r') as f:
            for line in f.readlines():
                nickName = line.rstrip('\n').split(' ')[1]
                userName = line.rstrip('\n').split(' ')[2]
                if name.lower() in nickName.lower() or nickName.lower() in name.lower():
                    return 'Exist'
        
        return 'Not Exist'
         
    def addMember(self, nickName, userID, roomID) -> str:
        if (self.__checkNameValidation(nickName) == True):
            raise Exception('the name is invalid')
        # elif (self.__checkID(userID) == True and False):
        #     # temp remove for testing
        #     raise Exception('the user id has already existed')
       
        # create member file if not exist
        self.__memberFile = os.path.join(self.__fileFolder, 'members.txt')
        if not os.path.exists(self.__memberFile):
            f = open(self.__memberFile, 'w')
            f.close()
        
        profile = self.__line_bot_api.get_group_member_profile(roomID, userID)
        with open(self.__memberFile, 'a') as f:
            f.write(f'{userID} {nickName} {profile.display_name}\n')
        
        return f'add member "{profile.display_name}" "{nickName}": SUCCESS'

if __name__ == '__main__':
    m = Member()
