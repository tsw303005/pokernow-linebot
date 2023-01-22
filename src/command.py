from src.pokernow import Pokernow
from linebot.models import MessageEvent, TextMessage, TextSendMessage

class Command(object):
    
    def __init__(self):
        self.__pokernow = Pokernow()
        self.__gameNum = 0
        self.__url = ['https://www.pokernow.club/games/pgl1JHGsdNtTfXrFW0CzTn6HR']
    
    def __parse(self, command):
        return command.split(' ')
    
    def makeCommand(self, command):
        parsedCommand = self.__parse(command)
        
        if parsedCommand[0] != 'pokernow':
            return 'return'
        elif parsedCommand[1] == 'help':
            return \
            '''pokernow linebot 指令

- pokernow getscore <場次>: 回傳第幾場次的 scoreboard 結果
- pokernow creategame: 創建新局，並且回傳網址跟場次

每個指令都需要等待個幾秒鐘
'''
        elif parsedCommand[1] == 'getscore' and parsedCommand[2].isnumeric() and int(parsedCommand[2]) <= self.__gameNum:
            # line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text="成績讀取中，請稍等")
            # )

            gameNum = int(parsedCommand[2])
            return self.__pokernow.getScore(self.__url[gameNum])
        
        elif parsedCommand[1] == 'creategame':
            url = self.__pokernow.createNewGame()
            self.__url.apppend(url)
            self.__gameNum += 1
            
            return f'場次: {self.__gameNum}\n url:{url}'
    