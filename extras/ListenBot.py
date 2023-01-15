import threading
import types
from colorama import Fore,Back,Style, init
    
init(autoreset=True)

class ListenInput(threading.Thread):
    def __init__(self,bot):
        super(ListenInput, self).__init__()
        self.daemon = True
        self.user_input = None
        self.bot = bot

    def run(self):
        while True:
            self.user_input = input('\n')
            try:
                response = getattr(self.bot, self.user_input)
                if type(response) == types.MethodType:
                    self.LogResponse("")
                    response()
                else:
                    self.LogResponse(str(response))
            except:
                self.LogResponse("Sorry I couldn't understand you")
    
    def LogResponse(self,text):
        print(Style.BRIGHT + 'BOT: ' + Style.RESET_ALL + text + '\n')