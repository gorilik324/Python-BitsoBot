from bot import Bot
import time

if __name__ == "__main__":
    book = input("Enter book: ")
    bot = Bot(book)

    while True:
        bot.update()
        time.sleep(10)
