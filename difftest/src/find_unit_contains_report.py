import os
import glob

def find_folders_with_report(path, keyword):
    # List to store names of folders with "report" in rst.log
    folders_with_report = []
    
    # Iterate over each folder in the specified path
    for folder in glob.glob(os.path.join(path, '*')):
        if os.path.isdir(folder):
            rst_log_path = os.path.join(folder, 'rst.log')
            # Check if rst.log exists in the folder
            if os.path.isfile(rst_log_path):
                with open(rst_log_path, 'r') as file:
                    content = file.read()
                    # Check if keyword is in the content of rst.log
                    if keyword in content:
                        folders_with_report.append(os.path.basename(folder))
    
    return folders_with_report

# Example usage
path = '/path/to/your/directory'
keyword = 'report'
result = find_folders_with_report(path, keyword)
print("Folders containing 'report' in rst.log:")
for folder in result:
    print(folder)