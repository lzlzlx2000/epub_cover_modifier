import os
import zipfile
import xml.etree.ElementTree as ET
import shutil


def modify_epub_cover(epub_path, output_dir, new_cover_filename='cover.jpg'):
    # Create a temporary directory
    temp_dir = 'temp_epub'
    os.makedirs(temp_dir, exist_ok=True)

    # Extract the epub
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Find and parse the content.opf file
    opf_path = None
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith('.opf'):
                opf_path = os.path.join(root, file)
                break
        if opf_path:
            break

    if not opf_path:
        print(f"Error: content.opf not found in {epub_path}")
        shutil.rmtree(temp_dir)
        return

    # Parse the content.opf file
    tree = ET.parse(opf_path)
    root = tree.getroot()

    # Define the namespace
    ns = {'opf': 'http://www.idpf.org/2007/opf'}

    # Find the manifest element
    manifest = root.find('opf:manifest', ns)

    # Find the cover image item
    cover_item = manifest.find(".//opf:item[@properties='cover-image']", ns)

    if cover_item is not None:
        # Get the old filename
        old_filename = cover_item.get('href').split('/')[-1]
        old_path = os.path.join(os.path.dirname(opf_path), cover_item.get('href'))

        # Update the cover image item attributes
        new_href = cover_item.get('href').replace(old_filename, new_cover_filename)
        cover_item.set('href', new_href)

        # Save the modified content.opf file
        tree.write(opf_path, encoding='utf-8', xml_declaration=True)

        print(
            f"Updated content.opf in {epub_path}: Changed cover image reference from {old_filename} to {new_cover_filename}")

        # Rename the actual image file
        new_path = os.path.join(os.path.dirname(old_path), new_cover_filename)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed image file from {old_filename} to {new_cover_filename}")
        else:
            print(f"Warning: Cover image file {old_filename} not found in {epub_path}")
    else:
        print(f"Error: Cover image item not found in content.opf of {epub_path}")

    # Create a new epub file
    output_epub_path = os.path.join(output_dir, os.path.basename(epub_path))
    with zipfile.ZipFile(output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    print(f"Created modified epub: {output_epub_path}")

    # Clean up temporary directory
    shutil.rmtree(temp_dir)


def process_all_epubs(output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process all epub files in the current directory
    for filename in os.listdir('.'):
        if filename.endswith('.epub'):
            epub_path = os.path.join('.', filename)
            modify_epub_cover(epub_path, output_dir)


# Usage
output_dir = './output'  # Output directory
process_all_epubs(output_dir)