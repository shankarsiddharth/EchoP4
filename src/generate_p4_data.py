from P4 import P4, P4Exception  # Import the module
import os
import sys
import json
import pathlib
import echo_p4_constants as ep4c
import p4_tools_helper as p4th


def main():

    P4_GROUP_NAME = "C12-SmartCompanion"

    root_folder_path = p4th.get_root_folder()
    data_folder_path = os.path.join(root_folder_path, ep4c.DATA_FOLDER_NAME)
    team_members_json_file_path = os.path.join(data_folder_path, ep4c.TEAM_MEMBERS_JSON_FILE_NAME)
    group_members_json_file_path = os.path.join(data_folder_path, ep4c.GROUP_MEMBERS_JSON_FILE_NAME)

    data_folder = pathlib.Path(data_folder_path)
    if not data_folder.exists():
        # Folder does not exist, create it
        print("Data folder does not exist. Creating it.")
        print("Creating data folder: " + data_folder_path)
        try:
            os.makedirs(data_folder_path)
        except OSError:
            print("Creation of the data folder failed.")
            input("Press any key to exit...")
            sys.exit(1)
    print("Data folder exists.")

    # try:
    #     with open('team_members.json', 'r', encoding='UTF-8') as team_members_json:
    #         team_members = json.load(team_members_json)
    # except FileNotFoundError as errorMessage:
    #     print(f"FileNotFoundError \n" f"{errorMessage}")

    p4 = P4()  # Create the P4 instance

    try:  # Catch exceptions with try/except

        print("Connecting to Perforce server....")
        p4.connect()  # Connect to the Perforce server

        group_details = p4.run("group", "-o", P4_GROUP_NAME)
        if len(group_details) != 1:
            print("Error: Group details not found for Group: ", P4_GROUP_NAME)
            input("Press any key to exit...")
            sys.exit(1)
        print("Group details found for Group: ", P4_GROUP_NAME)
        with open(group_members_json_file_path, 'w', encoding='UTF-8') as group_members_json:
            json.dump(group_details[0], group_members_json, indent=4)
        print("Group details saved to file: ", group_members_json_file_path)
        group_users_list = group_details[0]['Users']

        team_members = dict()
        for user in group_users_list:
            print("Getting user details for user: ", user)
            user_details = p4.run("user", "-o", user)
            if len(user_details) != 1:
                print("Error: User details not found for User: ", user)
                input("Press any key to exit...")
                sys.exit(1)
            print("User details found for User: ", user)
            team_members[user] = user_details[0]
        with open(team_members_json_file_path, 'w', encoding='UTF-8') as team_members_json:
            json.dump(team_members, team_members_json, indent=4)
        print("Team members details saved to file: ", team_members_json_file_path)

        p4.disconnect()  # Disconnect from the server

    except P4Exception:

        for errorMessage in p4.errors:  # Display errors
            print(errorMessage)
            print("======================================================================================")
            print("Log in using p4 login in cmd prompt (or) login using P4V")
            print("Make sure you have permission to run the p4 commands: group, user")
            print("Once Logged in, run this script again.")


if __name__ == "__main__":
    main()
