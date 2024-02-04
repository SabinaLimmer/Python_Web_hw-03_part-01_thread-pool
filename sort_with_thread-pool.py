import os
import shutil
import sys
import re
from unidecode import unidecode
from concurrent.futures import ThreadPoolExecutor

# Dictionary with file categories
file_categories = {
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "audio": [".mp3", ".ogg", ".wav", ".amr"],
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "archives": [".zip", ".gz", ".tar"],
    "unknown": []
}

# Function to create target folders
def create_target_folders(folder_path):
    for directory in file_categories:
        category_folder = os.path.join(folder_path, directory)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder, exist_ok=True)

# Function to normalize file names
def normalize(file_name):
    normalized_name = unidecode(file_name)
    normalized_name = re.sub(r'[^\w\s]', '_', normalized_name)
    return normalized_name

# Function to process a single file
def process_file(file_path, folder_path):
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    normalized_file_name = normalize(file_name)
    new_file_name = normalized_file_name + file_extension

    if file_extension.lower() in file_categories["images"]:
        shutil.move(file_path, os.path.join(folder_path, 'images', new_file_name))
    elif file_extension.lower() in file_categories["video"]:
        shutil.move(file_path, os.path.join(folder_path, 'video', new_file_name))
    elif file_extension.lower() in file_categories["documents"]:
        shutil.move(file_path, os.path.join(folder_path, 'documents', new_file_name))
    elif file_extension.lower() in file_categories["audio"]:
        shutil.move(file_path, os.path.join(folder_path, 'audio', new_file_name))
    elif file_extension.lower() in file_categories["archives"]:
        shutil.move(file_path, os.path.join(folder_path, 'archives', new_file_name))
        file_path_archives = os.path.join(folder_path, 'archives', new_file_name)
        folder_path_archives = os.path.join(folder_path, 'archives', normalized_file_name)
        os.makedirs(folder_path_archives, exist_ok=True)
        shutil.unpack_archive(file_path_archives, folder_path_archives)
    else:
        shutil.move(file_path, os.path.join(folder_path, 'unknown', new_file_name))

# Function to process the folder and organize files using ThreadPoolExecutor
def process_folder(folder_path):
    with ThreadPoolExecutor() as executor:
        futures = []
        for root, dirs, files in os.walk(folder_path):
            categories_paths = [os.path.join(folder_path, folder) for folder in file_categories.keys()]
            if not any(category_path in root for category_path in categories_paths):
                for file in files:
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(process_file, file_path, folder_path))

        # Wait for all threads to complete
        for future in futures:
            future.result()

    for folder in os.listdir(folder_path):
        folder_full_path = os.path.join(folder_path, folder)
        if os.path.isdir(folder_full_path) and folder not in file_categories.keys():
            if not os.listdir(folder_full_path):
                os.rmdir(folder_full_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of args, provide target folder.")
    else:
        target_folder = sys.argv[1]
        create_target_folders(target_folder)
        process_folder(target_folder)
        print("Sorting and organizing completed.")
