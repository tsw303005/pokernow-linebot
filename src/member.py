import os

class Member(object):
    MEMBERS = list()

    def __init__(self) -> None:
        # make sure that download folder exists, ledger and record folder
        self.__fileFolder = os.path.join(os.getcwd(), 'files')
        if not os.path.exists(self.__fileFolder):
            os.makedirs(self.__fileFolder)
            
        self.__memberFile = os.path.join(self.__fileFolder, 'members.txt')
        if not os.path.exists(self.__memberFile):
            f = open(self.__memberFile, 'w')
            f.close()
            
        with open(self.__memberFile, 'r') as f:
            for line in f.readlines():
                name = line.rstrip('\n').split(' ')[1]
                self.MEMBERS.append(name)

            
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
         
    def addMember(self, name, id) -> str:
        if (self.__checkID(id) == True):
            raise Exception('the user id has already existed')
        elif (self.__checkNameValidation(name) == True):
            raise Exception('the name is invalid')
        
        with open(self.__memberFile, 'a') as f:
            f.write(f'{id} {name}\n')
            
        self.MEMBERS.append(name)
        
        return f'add member {name} success'

if __name__ == '__main__':
    m = Member()
