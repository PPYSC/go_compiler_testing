import os

def find_folders_with_executables(path):
    matching_folders = []

    for folder_name in os.listdir(path):
        folder_path = os.path.join(path, folder_name)

        if os.path.isdir(folder_path) and (folder_name.startswith('d') or folder_name.startswith('u')):
            exe0_path = os.path.join(folder_path, 'exe0')
            exe1_path = os.path.join(folder_path, 'exe1')

            if os.path.isfile(exe0_path) and os.path.isfile(exe1_path):
                matching_folders.append(folder_name)

    return matching_folders

# Example usage
path = '/path/to/your/directory'
matching_folders = find_folders_with_executables(path)

for folder in matching_folders:
    print(folder)