from src.pokernow import Pokernow
from src.member import Member
from linebot import LineBotApi
from dotenv import load_dotenv
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

class Command(object):

    def __init__(self) -> None:
        load_dotenv()

        self.__pokernow = Pokernow()
        self.__member = Member()

        # line_bot_api
        self.__line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
    
    def __parse(self, command) -> list:
        spl = command.split(' ')
        if (spl[0] != '!pokernow'):
            return []
        else:
            return spl[1:]
        
        
    def makeCommand(self, command, userID, groupID) -> str:
        command = self.__parse(command)
        
        # if command does not correspond the format
        # means that return nothing
        if not command:
            return ''

        if command[0] == 'addMember':
            resp = self.__member.addMember(command[1], userID, groupID)
        elif command[0] == 'checkExist':
            resp = self.__member.checkMemberExist(command[1])
        elif command[0] == 'endGame':
            resp = self.__pokernow.endGame(command[1])
        elif command[0] == 'getMembers':
            resp = self.__member.getMembers()
        elif command[0] == 'settleup':
            self.__line_bot_api.push_message(groupID, TextSendMessage(text='正在結算中，請稍等～'))
            resp = self.__pokernow.settleUp()
        else:
            raise Exception('wrong command format, please check help')
            
        return resp
        
