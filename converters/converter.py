__author__ = 'Xomak'

import json
import csv

__author__ = 'Xomak'


def normalize_list(input_list):
    """Converts list of moveable items into list of its' positions"""

    output_list = list()
    sorted_list = list(input_list)
    sorted_list.sort()
    for element in sorted_list:
        element_position = input_list.index(element)
        output_list.append(element_position)
    return output_list


def convert_users(input_filename, output_filename):
    """
    Converts user from CSV, downloaded from old web-interface, into JSON-file, suitable for DataReader
    :param input_filename: Input file's name
    :param output_filename: Output file's name
    :return: None
    """
    output_json = []
    with open(input_filename, newline='', encoding='utf-8') as input_file:
        with open(output_filename, 'w', newline='') as output_file:
            reader = csv.reader(input_file, delimiter=',', quotechar='"')
            for input_row in reader:
                current_user = dict()
                # User_id
                current_user['id'] = input_row[0]

                # If user has results
                if input_row[5]:
                    user_lists = []
                    json_data = json.loads(input_row[5])
                    json_lists = json_data['lists']
                    for order_list in json_lists:
                        current_list = order_list['items']
                        normalized_list = normalize_list(current_list)
                        user_lists.append(normalized_list)
                    json_selected_people = json_data['selectedPeople']
                    current_user['lists'] = user_lists
                    current_user['name'] = input_row[1]
                    current_user['selectedPeople'] = json_selected_people
                    output_json.append(current_user)
            json.dump(output_json, output_file)


if __name__ == '__main__':
    convert_users('../data/users.csv', '../data/users.json')