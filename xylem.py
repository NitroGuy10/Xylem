# Xylem
# A customizable file converter
# By NitroGuy
# https://github.com/NitroGuy10/Xylem

# Intended functionality:

# your OS may or may not perform drag&drop correctly; Windows does
# convert a droppped file [IMPLEMENTED]
# convert multiple dropped files [IMPLEMENTED]
# convert a dropped folder [IMPLEMENTED]
# convert multiple dropped folders [IMPLEMENTED]
# convert a combination of dropped files and folders [IMPLEMENTED]

# convert a stdin-entered file [IMPLEMENTED]
# convert multiple stdin-entered files [IMPLEMENTED]
# convert a stdin-entered folder [IMPLEMENTED]
# convert muliple stdin-entered folders [IMPLEMENTED]
# convert a combination of stdin-entered files and folders [IMPLEMENTED]

# convert an arg file [IMPLEMENTED]
# convert multiple arg files [IMPLEMENTED]
# convert an arg folder [IMPLEMENTED]
# convert multiple arg folders [IMPLEMENTED]
# convert a combination of arg files and folders [IMPLEMENTED]

# tl;dr, Xylem is usable via ARGS, STDIN, or DRAG&DROP + STDIN


import argparse
import pathlib
import subprocess
import os
import json


if __name__ == "__main__":
    # Argparse stuff
    parser = argparse.ArgumentParser(description="Xylem: A customizable file converter by NitroGuy", epilog="https://github.com/NitroGuy10/Xylem")
    parser.add_argument("input_files_folders", nargs="*", help="The input file(s) and/or folder(s) to convert")  # This takes in drag-n-drop args too!!!
    parser.add_argument("-f", "--file_format", help="The format you want to convert to (will prompt if not specified)")
    parser.add_argument("-of", "--output_folder", help="The folder to place the output in (will prompt if not specified)")
    error_handling_group = parser.add_mutually_exclusive_group()
    error_handling_group.add_argument("-s", "--skip", action="store_true", help="Skip conversions that would otherwise overwrite a file")
    error_handling_group.add_argument("-o", "--overwrite", action="store_true", help="Overwrite files in such cases")
    args = parser.parse_args()

    file_format = args.file_format
    input_files_folders = args.input_files_folders
    output_folder = args.output_folder

    if len(args.input_files_folders) == 0:  # No CLI arguments provided
        # Prompt for input files/folders
        input_files_folders = input("Input file(s) and/or folder(s) to convert (separated by spaces) ----> ").split()

    # Find file paths in input_files_folders
    input_files_folders_split_initial = input_files_folders
    input_files_folders = []

    # Merge strings that were split by an escaped space
    input_files_folders_split = []
    running_string = ""
    for split in input_files_folders_split_initial:
        if split.endswith("\\"):
            running_string += split[:-1] + " "
        else:
            input_files_folders_split.append(running_string + split)
            running_string = ""

    # Handle quotation marks
    running_string = None
    for split in input_files_folders_split:
        if running_string is None and ((split.startswith("'") and split.endswith("'")) or (split.startswith("\"") and split.endswith("\""))):  # A path with no spaces that has quotation marks for some reason
            input_files_folders.append(split.strip("\"'"))
        elif "\"" in split or "'" in split:
            if running_string is None:
                running_string = split
            else:
                running_string += " " + split
                input_files_folders.append(running_string.strip("\"'"))
                running_string = None
        else:
            if running_string is None:
                input_files_folders.append(split)
            else:
                running_string += " " + split
    
    # Print everything that will be converted for a sanity check
    print("Will convert:")
    for input_file_folder in input_files_folders:
        print(input_file_folder)
    print("")

    # Prompt for output folder if not present in args
    if output_folder is None:
        output_folder = input("Folder to place output in (optional) ----> ").strip("\"")
        if output_folder == "":
            output_folder = None
        else:
            output_folder = pathlib.Path(output_folder)
            if not output_folder.exists():
                raise FileNotFoundError("Output folder " + str(output_folder) + " does not exist")

    # Prompt for format if not present in args
    if file_format is None:
        file_format = input("Format to convert to ----> .")

    # Assign output paths and unwrap any folders
    input_data = []
    for input_path_str in input_files_folders:
        input_path = pathlib.Path(input_path_str)
        # Check if the input file/folder exists
        if not input_path.exists():
            raise FileNotFoundError("Input file/folder " + input_path_str + " does not exist")
        
        if input_path.is_dir():
            if len(input_files_folders) == 1:  # If one folder and one folder only is specified, don't create any folders for output, just unwrap the folder into the output dir
                # Actually maybe don't do this
                pass
            for item in input_path.iterdir():
                if item.is_file():
                    data_tuple = (str(item), input_path.name)
                    input_data.append(data_tuple)
                    print(f"Found {item.name} in folder {input_path.name}")
        else:
            data_tuple = (input_path_str, "")
            input_data.append(data_tuple)
    
    # Load config.json
    config_path = pathlib.Path(__file__).parent.joinpath("config.json")
    config = None
    with open(config_path) as config_file:
        config = json.load(config_file)
    
    # Identify the appropriate converter to use
    file_format = file_format.lower()
    converter = None
    for converter_config in config["converters"]:
        if file_format in converter_config["formats"]:
            converter = converter_config
            break
    
    if converter is None:
        # Prompt the user if a converter isn't indentified
        print(f"A converter could not be automatically identified for .{file_format} files")
        print(f"To avoid this prompt in the future, modify config.json")
        print("Converters available:")
        for converter_index in range(len(config["converters"])):
            print(f"{converter_index + 1}.   {config['converters'][converter_index]['name']}")
        desired_converter_index = int(input("Input the number corresponding with the converter to use: "))
        converter = config["converters"][desired_converter_index - 1]
    else:
        # Prompt the user to specify formatArgs
        if file_format in config["formatArgs"]:
            for format_arg in config["formatArgs"][file_format]:
                arg_input = input(format_arg["prompt"]).strip()
                if format_arg["inputType"] == "string":
                    if len(arg_input) == 0:  # If an empty string was given
                        for added_argument_index in range(len(format_arg["argumentsIfEmpty"])):
                            converter["runCommand"].insert(format_arg["argumentsBeforeIndex"] + added_argument_index, format_arg["argumentsIfEmpty"][added_argument_index])
                    else:
                        for added_argument_index in range(len(format_arg["argumentsIfNotEmpty"])):
                            converter["runCommand"].insert(format_arg["argumentsBeforeIndex"] + added_argument_index, format_arg["argumentsIfNotEmpty"][added_argument_index].replace("$$STRING$$", arg_input))
                elif format_arg["inputType"] == "y/n":
                    if arg_input.lower() == "n":
                        for added_argument_index in range(len(format_arg["argumentsIfNo"])):
                            converter["runCommand"].insert(format_arg["argumentsBeforeIndex"] + added_argument_index, format_arg["argumentsIfNo"][added_argument_index])
                    elif arg_input.lower() == "y":
                        for added_argument_index in range(len(format_arg["argumentsIfYes"])):
                            converter["runCommand"].insert(format_arg["argumentsBeforeIndex"] + added_argument_index, format_arg["argumentsIfYes"][added_argument_index])
                    else:
                        raise ValueError("Must input \"y\" or \"n")
                else:
                    raise TypeError(f"Unknown inputType {format_arg['input_type']}")


    # Main conversion loop
    for input_path_str, output_folder_additional_path in input_data:
        input_path = pathlib.Path(input_path_str)
        # Check if the input file exists... again... just to make sure I didn't screw anything up
        if not input_path.exists():
            raise FileNotFoundError("Input file " + input_path_str + " does not exist")

        # Manufacture the output folder path
        output_folder_path = None
        if output_folder is None:  # If no output folder was specified
            output_folder_path = pathlib.Path(os.path.dirname(input_path))
        else:
            output_folder_path = pathlib.Path(os.path.join(output_folder, output_folder_additional_path))
            if not output_folder_path.exists():
                os.mkdir(output_folder_path)
        
        # Manufacture the output file path
        output_name = None
        if "." not in input_path.name:
            output_name = input_path.name + "." + file_format
        else:
            output_name = ".".join(input_path.name.split(".")[:-1]) + "." + file_format
        output_path = pathlib.Path(os.path.join(output_folder_path, output_name))
        
        # Check if output file already exists
        if output_path.exists():
            if args.skip:  # If user chose to skip potential overwrites
                print("File " + str(output_path) + " already exists... skipping")
                continue
            elif args.overwrite:  # If user allowed overwrites
                print("File " + str(output_path) + " already exists... overwriting")
            else:  # If user did not allow skips or overwrites
                raise FileExistsError("File " + str(output_path) + " already exists")

        # At this point, conversion would either not overwrite anything or would overwrite because the user allowed it
        # Convert!
        command_sequence = [command_item.replace("$$INPUT_PATH$$", str(input_path)).replace("$$OUTPUT_PATH$$", str(output_path)) for command_item in converter["runCommand"]]

        print(f"Converting {input_path.name} to {file_format} with {converter['name']}")
        print(" ".join(command_sequence))
        process = subprocess.run(command_sequence)
        print("Conversion finished")
        
        # Halt the program and display an error message if a conversion subprocess fails
        if process.returncode != 0:
            raise RuntimeError(f"Conversion subprocess for {input_path} failed with return code {process.returncode}")

    print("All done!")

