from mail_getter import *
from time import sleep
import traceback as tb


def mail_getter_looper():
    mail_getter = MailGetter()
    while True:
        try:
            mail_getter.get_all_files_from_msgs()
            mail_getter.parse_files()
            sleep(GET_MAIL_DELAY)
        except Exception as e:
            logger.warning("ERROR: Getting mail failed")
            print(e)
            sleep(GET_MAIL_DELAY)


if __name__ == '__main__':
    init_service()
    mail_getter_looper()

