import time
from bot import Bot
from extras.ListenBot import ListenInput
                
if __name__ == '__main__':
    market   = input('Enter book: ')
    
    bot = Bot(market)
    li = ListenInput(bot)
    li.start()
    while True:
        bot.update()
        time.sleep(20)