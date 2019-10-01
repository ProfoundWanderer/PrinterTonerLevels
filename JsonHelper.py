#!/usr/bin/python3

import datetime
import logging
import json
from pathlib import Path
import sys
import TonerLevels


def toner_history(combined_info):
    """
    1. Store today's information to json file
    2. Open current_day.json and previous_day.json
    3. Pull the dicts out of each file
    4. If toner levels are at or below 10% add message about that color level to low_toner_message
    5. If toner levels today are higher than yesterday add message to level_change_message to ensure toner was ordered
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    low_toner_message = ""
    level_change_message = ""

    # save today's json to file
    with open("current_day.json", "w", encoding="utf-8") as f:
        json.dump(combined_info, f, ensure_ascii=False, indent=4)

    # open current_day.json
    today_data_file = Path("current_day.json")
    if today_data_file.is_file():
        with open("current_day.json", "r") as read_file:
            current_data = json.load(read_file)

    # open previous_day.json
    yesterday_data_file = Path("previous_day.json")
    if yesterday_data_file.is_file():
        with open("previous_day.json", "r") as read_file:
            previous_data = json.load(read_file)
    else:  # the first run won't have a previous day unless manually added so this catches that first run
        if today_data_file.is_file():
            with open("current_day.json", "r") as read_file:
                previous_data = json.load(read_file)

    yesterday_dict = previous_data['printerinfo']
    today_dict = current_data['printerinfo']

    for yesterday_dict_item, today_dict_item in zip(yesterday_dict, today_dict):
        logging.info(f"The {today_dict_item['office_and_name']}({today_dict_item['id']}) printer is at "
                     f"{today_dict_item['level']}% {today_dict_item['color']} toner as of {current_time}.")
        if today_dict_item['level'] <= 10:
            low_toner_message += (
                f"The {today_dict_item['office_and_name']} printer is at {today_dict_item['level']}% "
                f"{today_dict_item['color']} toner as of {current_time}. The printer ID is {today_dict_item['id']}.\n"
            )
        if yesterday_dict_item['level'] < today_dict_item['level']:
            level_change_message += (
                f"The {today_dict_item['office_and_name']} printer is at {today_dict_item['level']}% "
                f"{today_dict_item['color']} toner as of {current_time} but yesterday it was at "
                f"{yesterday_dict_item['level']}%. Make sure more toner was ordered. The printer ID is "
                f"{today_dict_item['id']}.\n"
            )

    # if no ink level change and all levels are above 10% then exit
    if yesterday_dict == today_dict and not any([low_toner_message, level_change_message]):
        logging.info("All toner levels in printers are above 10% and levels today are not higher than yesterday.")
        logging.info("TonerLevels.py script has ended.")
        with open("previous_day.json", "w", encoding="utf-8") as f:
            json.dump(combined_info, f, ensure_ascii=False, indent=4)
            logging.info("All good: Saved today's levels as previous_day.json")
        sys.exit(0)

    with open("previous_day.json", "w", encoding="utf-8") as f:
        json.dump(combined_info, f, ensure_ascii=False, indent=4)
        logging.info("Check Levels: Saved today's levels as previous_day.json")

    TonerLevels.send_email(low_toner_message, level_change_message)
