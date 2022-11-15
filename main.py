import os
import argparse
from shutil import rmtree
from glob import glob
from zipfile import ZipFile
from os.path import basename, join


class CBZMerger:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--folder", "-f", help="Folder where CBZ/CBR files are located")
        parser.add_argument("--output", "-o", help="Filename of the merged CBZ/CBR file")
        parser.add_argument("--include-subdirs", action='store_true', help="Decides if CBZ/CBR files in subfolders are included")
        # System to not include first page and/or last page - doesnt work atm
        # parser.add_argument("--first-page", help="Removes first page - y/n")
        # parser.add_argument("--last-page", help="Removes last page - y/n")
        args = parser.parse_args()

        self.check_args(args)

        self.folder = args.folder
        self.output_name = args.output
        self.temp = "temp_folder"
        self.include_subdirs = args.include_subdirs
        # System to not include first page and/or last page - doesnt work atm
        # self.first_page = args.first_page
        # self.last_page = args.last_page

        self.files = self.fetch_files()    
        self.unpack_files()
        self.pack_files()
        self.delete_temp()


    def fetch_files(self):
        """
        finds all files (subdir files also) and checks if theyre 
        cbz or cbr files. then it also checks if '--include-subdirs-'
        is toggled because if its not, then it only takes files
        that are in the folder but not in the sub folders.
        """
        all_paths = []
        for path, subdirs, files in os.walk(self.folder):
            for name in files:
                file_path = os.path.join(path, name)
                if file_path.endswith('.cbr') or file_path.endswith('.cbz'):
                    if self.include_subdirs is not None:
                        all_paths.append(file_path)
                    elif os.path.exists(f"{self.folder}/{name}"):
                        all_paths.append(file_path)
 
        print(f"Found a total of {len(all_paths)} files")
        return sorted(all_paths)


    def list_pages(self, temp_folder): # finds all pages
        pngs = glob(f"{temp_folder}/**/*.png", recursive=True)
        jpgs = glob(f"{temp_folder}/**/*.jpg", recursive=True)
        pages = jpgs + pngs
        # System to not include first page and/or last page - doesnt work atm
        # if self.first_page.lower() == 'y':
        #     pages = pages[1:len(pages)]
        # if self.last_page.lower() == 'y':
        #     pages = pages[:-1]
        pages = pages[:-1]
        return sorted(pages)


    def unpack_files(self): # unpacks the files one after one
        for file_path in self.files:
            name = file_path.split('/')[-1] # finds filename from filepath
            temp_folder = f"temp_{name}"

            print(f"Handling \"{name}\"")
            zip_file = ZipFile(file_path) 
            zip_file.extractall(temp_folder)
            for filename in self.list_pages(temp_folder):
                os.renames(filename, join(f"{self.temp}", name, basename(filename)))


    def pack_files(self): # packs the files into one file
        pages = self.list_pages(self.temp)
        print(f"Merging {len(pages)} pages into \"{self.output_name}\"")
        with ZipFile(self.output_name, "w") as output_file:
            for page in pages:
                output_file.write(page)


    def delete_temp(self):
        directory = os.listdir()
        for _object in directory:
            if self.temp == _object:
                print('Job done! Deleting temp files...')
                rmtree(self.temp)


    def check_args(self, args):
        if args.folder is None or args.output is None:
            print("Use '-h' for help")
            exit()


if __name__ == "__main__":
    CBZMerger()
