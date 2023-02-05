# Last updated 4 February 2023

# convert a droppped file [IMPLEMENTED]
# convert multiple dropped files [IMPLEMENTED]
# convert a dropped folder [IMPLEMENTED]
# convert multiple dropped folders [IMPLEMENTED]

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

# tl;dr, make it useable from ARGS, STDIN, and DRAG&DROP + STDIN

# use imagemagick for image files (and use an editable list of other formats)
# use ffmpeg for everything else (as "default" case)

# specify output folder
# if multiple input folders are specified, preserve the directory structure and create multiple new folders
# handle cases where a file with the same name already exists in the directory (append a 1 or something)
# option to skip any failures, otherwise will halt the program and display an error message



import argparse
from genericpath import exists
import pathlib
import subprocess
import os



def run_convert_subprocess(input_path, output_path, desired_file_format):
    if desired_file_format in ["jpg", "jpeg", "png", "tif", "tiff", "bmp", "webp", "heif", "heic"]:
        print("Converting {} to {} with ImageMagick".format(input_path.name, desired_file_format))
        subprocess.run(["magick", str(input_path), str(output_path)])
        print("Done!")
    else:
        print("Converting {} to {} with FFmpeg".format(input_path, desired_file_format))
        subprocess.run(["ffmpeg", "-y", "-i", str(input_path), str(output_path)])  # -y for force overwriting
        print("Done!")



parser = argparse.ArgumentParser()
parser.add_argument("input_files_folders", nargs="*", help="The input file(s) and/or folder(s) to convert")  # This takes in drag-n-drop args too!!!
parser.add_argument("-f", "--file_format", help="The format you want to convert to (will prompt if not specified)")
parser.add_argument("-of", "--output_folder", help="The folder to place the output in (default is the same folder as input)")
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

    # Prompt for output folder
    output_folder = input("Folder to place output in (optional) ----> ").strip("\"")
    if output_folder == "":
        output_folder = None
    else:
        output_folder = pathlib.Path(output_folder)
        if not output_folder.exists():
            raise FileNotFoundError("Output folder " + str(output_folder) + " does not exist")


# Find file paths in input_files_folders
input_files_folders_split_initial = input_files_folders
input_files_folders = []

# Merge strings that were split by an escaped space
input_files_folders_split = []
running_string = ""
for split in input_files_folders_split_initial:
    running_string += split
    if split.endswith("\\"):
        running_string = split[:-1] + " "
    else:
        input_files_folders_split.append(running_string)
        running_string = ""

# Handle quotation marks
running_string = None
for split in input_files_folders_split:
    if "\"" in split or "'" in split:
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
                print("Found {} in folder {}".format(item.name, input_path.name))
    else:
        data_tuple = (input_path_str, "")
        input_data.append(data_tuple)


# Main conversion loop
file_format = file_format.lower()
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
        if not exists(output_folder_path):
            os.mkdir(output_folder_path)
    
    # Manufacture the output file path
    output_name = None
    if "." not in input_path.name:
        output_name = input_path.name + "." + file_format
    elif input_path_str.split(".")[-1] == file_format:
        output_name = ".".join(input_path.name.split(".")[:-1]) + "1." + file_format
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
    run_convert_subprocess(input_path, output_path, file_format)


print("All done!")
