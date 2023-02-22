from src.pokernow import Pokernow
from src.member import Member

class Command(object):

    def __init__(self) -> None:
        self.__pokernow = Pokernow()
        self.__member = Member()
    
    def __parse(self, command) -> list:
        spl = command.split(' ')
        if (spl[0] != '!pokernow'):
            return []
        else:
            return spl[1:]
        
        
    def makeCommand(self, command, userId) -> str:
        command = self.__parse(command)
        if command[0] == 'addMember':
            resp = self.__member.addMember(command[1], userId)
        elif command[0] == 'endGame':
            resp = self.__pokernow.endGame(command[1])
        else:
            raise Exception('wrong command format, please check help')
            
        return resp
        
