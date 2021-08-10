from shutil import copy2
import constants as const
from BOGClient import BOGClient

def run_client(token: str):
    client = BOGClient()
    client.run(token)


if __name__ == '__main__':
    if const.TOKEN:
        run_client(const.TOKEN)
    else:
        print("Your environment variables were not set!")
        print("Please modify your .env file")
        copy2(const.TEMP_ENV_PATH, const.ENV_PATH)
        exit(1)
