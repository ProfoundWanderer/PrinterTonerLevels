#!/usr/bin/python3

import logging
import os
import re
import rrdtool


def grab_data(file_directory, toner_file_list):
    """
    This function:
    1. Goes through each file in the target directory `for file in os.listdir(file_directory)`
    2. If the file is in toner_file_list `if file in toner_file_list` then it goes to step 3 but if it isn't it
       goes to the next file
    3. If the file is in file_directory and toner_file_list then it joins the file and file_directory to
        access it`os.path.join(file_directory, file)` and assigns it to rrd_files
    4. Goes through the rrd files and gets there value and filename
    5. Puts the information in a list and returns it
    """
    rrd_files = [
        os.path.join(file_directory, file)
        for file in os.listdir(file_directory)
        if file in toner_file_list
    ]

    data_container = []
    for rrd_file in rrd_files:  # loop through each files in rrd_files
        # this gets the LAST value in the file (which is actually the current value)
        data = rrdtool.lastupdate(rrd_file)
        # gets the filename and extension but splits it so only the filename remains
        file_name = os.path.basename(rrd_file).split(".")[0]
        # adds the filename and value to data_container
        data_container.extend([file_name, data.values()])

    return separate_data(data_container)


def separate_data(data):
    """
    This function separates the data then puts it in a dictionary in order to use it in revise_data()
    """
    # declaring a dictionary to hold the keys and values I am declaring to use later
    low_toner_dict = {}
    low_dict_key = None
    toner_color = ""
    int_toner_level = ""

    for i in data:
        # this makes the printer name the dict key
        if isinstance(i, str):
            low_dict_key = i
        if not isinstance(i, str):
            i = list(i)
            current_level = i[1]
            if isinstance(current_level, dict):
                """
                These are ugly but gets the dict keys and values (there are only one of each) and makes it
                into a list then gets the first thing in each list and assigns it to a variable. This prints
                them like (eg 30 instead of dict_value[30])
                """
                toner_color = list(current_level.keys())[0]
                toner_level = list(current_level.values())[0]
                int_toner_level = int(toner_level)

        low_toner_dict[low_dict_key] = [toner_color, int_toner_level]

    return revise_data(low_toner_dict)


def revise_data(low_toner_dict):
    """
    1. This revises the data to make names and color more readable.
    2. Puts the newly revised data into a dict that is ready to be put into a json file
    """
    json_ready_dict = {'printerinfo': []}

    # Changes the name to be more easily readable and assigns the correct printer ID
    for office_and_printer, color_level in low_toner_dict.items():
        if "dfw-bizhub_c458" in office_and_printer:
            office_and_printer = "Dallas BizHub C458"
            printer_id = "94933518"
        elif "dfw-m521dn-checkprinter" in office_and_printer:
            office_and_printer = "Dallas M521dn CheckPrinter"
            printer_id = "93633638"
        elif "frtx-hp570dn" in office_and_printer:
            office_and_printer = "Frisco HP570dn"
            printer_id = "94873874"
        elif "hotx-hp570dn" in office_and_printer:
            office_and_printer = "Houston Office HP570dn"
            printer_id = (
                "Unsure of the ID but the serial number is: CNCKLBV2CK"
            )
        elif "orl-m570dn" in office_and_printer:
            office_and_printer = "Orlando M570dn"
            printer_id = "94785679"
        elif "sauk-m570dn" in office_and_printer:
            office_and_printer = "Sauk Rapids M570dn"
            printer_id = "93352461"
        # this else should never trigger at this point but is just a safety net more or less
        else:
            logging.error(
                f"Can not recognize {office_and_printer} as a valid office and printer."
            )
            raise ValueError

        if color_level:
            """ - Removes the "Snmp_" in front of the color and the number at the end.
                - Makes color to title case.
                - Before the previous and next line of code `snmp_magenta3` and after `Magenta`."""
            clean_color = re.sub(r"(Snmp_)|(\d$)", "", color_level[0].title())

            printerinfo = {'office_and_name': office_and_printer, 'level': color_level[1], 'color': clean_color,
                           'id': printer_id}
            json_ready_dict['printerinfo'].append(printerinfo)
        else:
            logging.error(
                f"The toner and toner level is missing for {office_and_printer}."
            )
            raise ValueError

    return json_ready_dict
