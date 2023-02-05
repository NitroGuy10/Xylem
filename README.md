# Xylem

A customizable file converter.

Xylem doesn't do any actual conversion itself, instead it prepares several calls to conversion applications that you can [configure](#configuration) yourself.

Xylem is useful if you don't want to set up a long complicated command, with several esoteric arguments, to a conversion program you might not even remember the name of, every time you want to convert a file.
It's also super useful for converting the contents of entire folders at once (which is the main thing I use it for).

## Installation

Make sure you have [Python 3](https://www.python.org/) installed.
Other than that, there are no dependencies...
well, besides the converters that you [configure](#configuration).

Just clone (download) this repository and you're good to go!

## Usage

The output of `python3 xylem.py -h` (thanks, argparse!):

```
usage: xylem.py [-h] [-f FILE_FORMAT] [-of OUTPUT_FOLDER] [-s | -o] [input_files_folders ...]

Xylem: A customizable file converter by NitroGuy

positional arguments:
  input_files_folders   The input file(s) and/or folder(s) to convert

options:
  -h, --help            show this help message and exit
  -f FILE_FORMAT, --file_format FILE_FORMAT
                        The format you want to convert to (will prompt if not specified)
  -of OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        The folder to place the output in (will prompt if not specified)
  -s, --skip            Skip conversions that would otherwise overwrite a file
  -o, --overwrite       Overwrite files in such cases

https://github.com/NitroGuy10/Xylem
```

Something that I like about Xylem is that there are actually three different ways to invoke it.

1. Run the script like normal.
That could mean typing `python3 xylem.py` or double clicking on the script if your OS has got that set up.
The script will walk you through inputting the necessary arguments.

2. Run the script with arguments (pictured above), like `python3 xylem.py my_movie.mkv my_movie2.mkv my_movies_folder -f mp4 -of output_folder`.
This way, Xylem can start converting right away (probably) without asking you for anything else.

3. Drag & drop the files/folders you want to convert ONTO the xylem.py script.
This essentially lets you skip the step of typing in file paths as arguments.
This works on Windows (assuming .py files are set up to be associated with Python) but it probably won't work on many other OS's.

   - *Although*... either way, your OS probably *would* let you drag and drop a file into the terminal window to paste its file path.
   That's pretty useful.

Anyway, as I hinted to before, you really can convert any combination of multiple files or folders.
Just pass them all in as arguments and Xylem will take care of the traversal for you. It won't recursively dig down into subfolders though.
That's kind of scary.

If you don't supply enough arguments, Xylem will prompt you to enter them.

```
Input file(s) and/or folder(s) to convert (separated by spaces) ----> my_mixtape.wav my_other_mixtape.wav
Folder to place output in (optional) ----> out
Format to convert to ----> .mp3
```

If Xylem can't figure out what converter to use based on your [configuration](#configuration), it'll ask you to choose one... based on your [configuration](#configuration).

DISCLAIMER: I don't think [FFmpeg](https://ffmpeg.org/) can convert .bruh files yet.

```
Format to convert to ----> .bruh
A converter could not be automatically identified for .bruh files
To avoid this prompt in the future, modify config.json
Converters available:
1.   ImageMagick
2.   FFmpeg
Input the number corresponding with the converter to use: 2
```

Depending on your [configuration](#configuration) (how many times have I said that), Xylem might also ask you a few extra questions depending on the file format you're converting to.

Note: If you're an advanced user looking to specify the answers to these prompts beforehand as arguments, I'm afraid your best option would be to [pipe](https://en.wikipedia.org/wiki/Pipeline_(Unix)) them in.

```
Format to convert to ----> .mp3
MP3 Bitrate in bps (Optional): 320000
```

Something that *won't* be handled for you if you don't specify any arguments, is the overwriting behavior.
By default, if a conversion would cause a file to be overwritten, Xylem intentionally crashes.
I would assume this is the behavior that most desire.
However, if you want to instead *skip* a conversion or *overwrite* a file in such a circumstance, you can tell Xylem to do that with the `-s` and `-o` flags, respectively.

If everything is OK, you should then see a flurry of text from the conversion program, piped to stdout for your convenience and entertainment, followed by Xylem exiting, and you being left with a folder of freshly converted files.

## Configuration

A starter config.json is already provided, featuring pretty much the only settings that I, myself, need.

```json
{
    "converters": [
        {
            "name": "ImageMagick",
            "formats": ["jpg", "jpeg", "png", "tif", "tiff", "bmp", "webp", "heif", "heic"],
            "runCommand": ["magick", "$$INPUT_PATH$$", "$$OUTPUT_PATH$$"]
        },
        {
            "name": "FFmpeg",
            "formats": ["webm", "mkv", "gif", "avi", "mov", "wmv", "mp4", "m4v", "mpg", "mpeg", "mp2", "aac", "aiff", "flac", "m4a", "mp3", "ogg", "wav", "wma", "wv", "apng"],
            "runCommand": ["ffmpeg", "-y", "-i", "$$INPUT_PATH$$", "$$OUTPUT_PATH$$"]
        }
    ],
    "formatArgs": {
        "mp3": [
            {
                "prompt": "MP3 Bitrate in bps (Optional): ",
                "inputType": "string",
                "argumentsIfEmpty": [],
                "argumentsIfNotEmpty": ["-ab", "$$STRING$$"],
                "argumentsBeforeIndex": 4
            }
        ],
        "gif": [
            {
                "prompt": "Loop? [y/n]: ",
                "inputType": "y/n",
                "argumentsIfNo": ["-loop", "-1"],
                "argumentsIfYes": ["-loop", "0"],
                "argumentsBeforeIndex": 4
            }
        ]
    }
}
```

My hope is that this configuration file is pretty self-explanatory.
In "converters", we specify a list of conversion programs, the formats that Xylem will look at to automatically choose the correct one, and the commands needed to run them.
\$\$INPUT_PATH\$\$ and \$\$OUTPUT_PATH\$\$, wherever they appear in any of the command strings, will be replaced by the input and output file paths, respectively, when the command is run.

In "formatArgs", we specify extra prompts to give the user if they choose to convert to a certain file format.
"inputType" can be "string" for any kind of input, or "y/n" for yes/no input.
Depending on the user's response, the corresponding list of arguments will be inserted into the run command for all calls to the converter.
Oh, and for "argumentsIfNotEmpty", any occurrence of \$\$STRING\$\$ will be replaced with what the user provided.

And a note on "argumentsBeforeIndex": the added arguments will be inserted BEFORE the index specified as expected, BUT if multiple prompts are given, the index you provide in the config may not reflect the correct position in the run command anymore due to there being other arguments added.
My suggestion for dealing with this is to prompt the user in decreasing order, starting from the argument with the highest "argumentsBeforeIndex".

