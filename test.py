import os

output_folder = 'C:/Users/alyne/OneDrive/Desktop'
output_files = []

print(os.walk(output_folder))

for (dirpath, dirnames, filenames) in os.walk(output_folder):
    output_files.extend(filenames)

print(output_files)
