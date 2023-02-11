# EchoP4

## Features  
- **One-Click Actions** —  Most common use-case actions when working with the Unreal Engine & C++ codebase.
- **View Group Member Names** — Display the names of group members in the group list along with the username or id.
- **View Checked out Files** — Display the files that are checked out for the configured project along with the user details.
- **MIT license**

## Installation
1. Download the latest release from the [releases](https://github.com/shankarsiddharth/EchoP4/releases) page.
2. Extract the zip file. `EchoP4.zip` => `EchoP4`
3. Place the extracted folder in an Unreal Engine project folder same tree level as the `<PROJECT_NAME>.uproject` file.

The folder structure should look like this:
```
<UNREAL_PROJECT_FOLDER>
    ├── Content
    ├── ....
    ├── EchoP4
        |── assets
        |── bin
            |── EchoP4.exe
        |── config
        |── data
        |── tools
        |── LICENSE.md
    ├── <PROJECT_NAME>.uproject
```

## Initial Configuration Setup
1. Run the `EchoP4.exe` file.
2. Enter the port, username, and password for the P4 server in the `Echo P4 Config UI`.
   > Note: The password is encrypted and the encryption key is stored in a separate file.
3. Click on the `Login` button.
4. Select the project/group to configure from the available list in the `Group Config UI`.
5. Click on the `Select Group/Project` button.   
6. `EchoP4` application will now be configured for the selected project/group.

## Custom Tools Setup (optional)
After the initial configuration setup, this application can be used as a custom tool in P4V.
1. Open the `P4V` application.
2. Click on the `Tools` > `Manage Tools` > `Custom Tools...`.
3. `Manage Custom Tools` window will open.
4. Click on the `Import Custom Tools...` button.
5. Select the `EchoP4/tools/echo_p4_tool.xml` file.
6. Click on the `Import` button in the `Import Preview` window.
7. Click on the `OK` button in the `Manage Custom Tools` window.
8. The `EchoP4` tool will now be available in the `Tools` menu in P4V.


## Credits

- [Dear PyGui](https://github.com/hoffstadt/DearPyGui)

- [Dear ImGui](https://github.com/ocornut/imgui)

- [ImPlot](https://github.com/epezent/implot)

- [imnodes](https://github.com/Nelarius/imnodes)

## License
EchoP4 is licensed under the [MIT License](https://github.com/shankarsiddharth/EchoP4/blob/main/LICENSE.md).
