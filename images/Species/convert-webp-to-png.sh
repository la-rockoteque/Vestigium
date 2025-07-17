#!/bin/bash
# Convert all .webp to .png in the current directory

for file in *.webp; do
    # Strip extension and add .png
    filename="${file%.*}"
    echo "Converting $file to $filename.png"
    dwebp "$file" -o "$filename.png"
done

echo "All .webp files have been converted to .png."