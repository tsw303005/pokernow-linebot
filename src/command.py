from src.pokernow import Pokernow

class Command(object):

    def __init__(self) -> None:
        self.__pokernow = Pokernow()
    
    def __parse(self, command) -> list:
        spl = command.split(' ')
        if (spl[0] != '!pokernow'):
            return []
        else:
            return spl[1:]
        
        
    def makeCommand(self, command):
        command = self.__parse(command)
