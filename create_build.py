import os
import pathlib
import shutil
import subprocess

import PyInstaller

from src import app_version as av
from src import echo_p4_constants as ep4c

# Application Start-up Script Name
application_start_up_script_name = "__main__.py"

# Get the current directory path
current_folder_path = os.path.dirname(os.path.realpath(__file__))
project_folder_path = current_folder_path
src_folder_path = os.path.join(project_folder_path, ep4c.SOURCE_FOLDER_NAME)
release_folder_path = os.path.join(project_folder_path, "release")
dist_folder_path = os.path.join(project_folder_path, "dist")  # PyInstaller creates this folder

# License File Path
project_license_file_path = os.path.join(project_folder_path, "LICENSE.md")

# Create release folder if it does not exist
release_folder = pathlib.Path(release_folder_path)
if not release_folder.exists():
    release_folder.mkdir()

# Get the version number
version_string: str = av.APP_VERSION_STRING

version_folder_path = os.path.join(release_folder_path, version_string)
version_folder = pathlib.Path(version_folder_path)
# Delete the version folder if it exists
if version_folder.exists():
    shutil.rmtree(version_folder_path)
# Create version folder if it does not exist
if not version_folder.exists():
    version_folder.mkdir()

# Create the Application Build folder
application_name = "EchoP4"
# Application Executable File Name - Windows Only
application_executable_file_name = application_name + ".exe"
application_build_folder_path = os.path.join(version_folder_path, application_name)
application_build_folder = pathlib.Path(application_build_folder_path)
# Delete the Application Build folder if it exists
if application_build_folder.exists():
    shutil.rmtree(application_build_folder_path)
# Create Application Build folder if it does not exist
if not application_build_folder.exists():
    application_build_folder.mkdir()

# Create options for pyinstaller
app_name_args_string = "--name=" + application_name
# Start-up script path
main_script_path = os.path.join(src_folder_path, application_start_up_script_name)
# Icon File Path for the Application
icon_path = "echo_p4.ico"
icon_args_string = "--icon=" + icon_path

try:
    completed_process = subprocess.run(["pyinstaller", "--onefile", "--windowed", app_name_args_string, icon_args_string, main_script_path],
                                       capture_output=True, text=True)
    print("return-code: " + str(completed_process.returncode))
    print("stdout: " + completed_process.stdout)
    print("stderr: " + completed_process.stderr)
except BaseException as e:
    print(e)

# Executable File Path
executable_file_path = os.path.join(dist_folder_path, application_executable_file_name)
executable_file = pathlib.Path(executable_file_path)
if not executable_file.exists():
    print("Executable file does not exist")
    exit(1)
# Create a binary directory in the Application Build folder
binary_folder_path = os.path.join(application_build_folder_path, ep4c.BINARY_FOLDER_NAME)
binary_folder = pathlib.Path(binary_folder_path)
# Create the binary folder if it does not exist
if not binary_folder.exists():
    binary_folder.mkdir()
# Copy the executable file to the binary folder
binary_executable_file_path = os.path.join(binary_folder_path, application_executable_file_name)
shutil.copy(executable_file_path, binary_executable_file_path)

# Copy the assets folder to the Application Build folder
assets_folder_path = os.path.join(application_build_folder_path, "assets")
assets_folder = pathlib.Path(assets_folder_path)
# Delete the assets folder if it exists
if assets_folder.exists():
    shutil.rmtree(assets_folder_path)
# Copy the source assets folder to the distribution assets folder
project_assets_folder_path = os.path.join(project_folder_path, "assets")
project_assets_folder = pathlib.Path(project_assets_folder_path)
if not project_assets_folder.exists():
    print("Source assets folder does not exist")
    exit(1)
shutil.copytree(project_assets_folder_path, assets_folder_path)

# Copy config defaults folder to the Application Build folder
config_defaults_folder_path = os.path.join(application_build_folder_path, ep4c.CONFIG_FOLDER_NAME, ep4c.CONFIG_DEFAULTS_FOLDER_NAME)
config_defaults_folder = pathlib.Path(config_defaults_folder_path)
# Delete the config defaults folder if it exists
if config_defaults_folder.exists():
    shutil.rmtree(config_defaults_folder_path)
# Copy the source config defaults folder to the distribution config defaults folder
project_config_defaults_folder_path = os.path.join(project_folder_path, ep4c.CONFIG_FOLDER_NAME, ep4c.CONFIG_DEFAULTS_FOLDER_NAME)
project_config_defaults_folder = pathlib.Path(project_config_defaults_folder_path)
if not project_config_defaults_folder.exists():
    print("Source config defaults folder does not exist")
    exit(1)
shutil.copytree(project_config_defaults_folder_path, config_defaults_folder_path)

# Copy data defaults folder to the Application Build folder
data_defaults_folder_path = os.path.join(application_build_folder_path, ep4c.DATA_FOLDER_NAME, ep4c.DATA_DEFAULTS_FOLDER_NAME)
data_defaults_folder = pathlib.Path(data_defaults_folder_path)
# Delete the data defaults folder if it exists
if data_defaults_folder.exists():
    shutil.rmtree(data_defaults_folder_path)
# Copy the source data defaults folder to the distribution data defaults folder
project_data_defaults_folder_path = os.path.join(project_folder_path, ep4c.DATA_FOLDER_NAME, ep4c.DATA_DEFAULTS_FOLDER_NAME)
project_data_defaults_folder = pathlib.Path(project_data_defaults_folder_path)
if not project_data_defaults_folder.exists():
    print("Source data defaults folder does not exist")
    exit(1)
shutil.copytree(project_data_defaults_folder_path, data_defaults_folder_path)

# Copy Tools defaults folder to the Application Build folder
tools_defaults_folder_path = os.path.join(application_build_folder_path, ep4c.TOOLS_FOLDER_NAME, ep4c.TOOLS_DEFAULTS_FOLDER_NAME)
tools_defaults_folder = pathlib.Path(tools_defaults_folder_path)
# Delete the tools defaults folder if it exists
if tools_defaults_folder.exists():
    shutil.rmtree(tools_defaults_folder_path)
# Copy the source tools defaults folder to the distribution tools defaults folder
project_tools_defaults_folder_path = os.path.join(project_folder_path, ep4c.TOOLS_FOLDER_NAME, ep4c.TOOLS_DEFAULTS_FOLDER_NAME)
project_tools_defaults_folder = pathlib.Path(project_tools_defaults_folder_path)
if not project_tools_defaults_folder.exists():
    print("Source tools defaults folder does not exist")
    exit(1)
shutil.copytree(project_tools_defaults_folder_path, tools_defaults_folder_path)

# Copy the license file to the Application Build folder
license_file_path = os.path.join(application_build_folder_path, "LICENSE.md")
shutil.copy(project_license_file_path, license_file_path)

# Create a zip file of the Application Build folder
zip_file_path = os.path.join(version_folder_path, application_name + ".zip")
# Delete the zip file if it exists
if os.path.exists(zip_file_path):
    os.remove(zip_file_path)
# Create the zip file
shutil.make_archive(application_build_folder_path, "zip", application_build_folder_path)

print("Zip File Created")

print("Build Complete")
