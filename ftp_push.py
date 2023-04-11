import os
import shutil
import ftplib
import tarfile
import time

# Set up FTP connection
ftp = ftplib.FTP('ChangeMe-IP', 'ChangeMe-Username', 'ChangeMe-Password')

# Change working dir to the FTP push dir
ftp.cwd('/')

# Set up the working dirs
push_dir = '/home/ftp_push/ftp'
work_dir = '/home/ftp_push/work'
extract_dir = os.path.join(work_dir, 'extracted')

while True:
    # Get a list of all tar.gz files in the push dir
    archive_files = [f for f in os.listdir(push_dir) if f.endswith('.tar.gz')]

    if archive_files:
        # Sort the list of archive files by modification time (oldest first)
        archive_files.sort(key=lambda f: os.path.getmtime(os.path.join(push_dir, f)))

        # Extract each archive file one at a time
        for archive_file in archive_files:
            # Extract the archive to the extracted dir
            with tarfile.open(os.path.join(push_dir, archive_file), 'r:gz') as tar:
                tar.extractall(extract_dir)

            # Remove the inverter files from the extracted dir
            for filename in os.listdir(extract_dir):
                if filename.startswith('inverter') and (filename.endswith('.nsf') or filename.endswith('.nmf')):
                    os.remove(os.path.join(extract_dir, filename))

            # Create a new tar.gz archive with the same name as the extracted archive
            new_archive_file = os.path.join(work_dir, archive_file)
            with tarfile.open(new_archive_file, 'w:gz') as tar:
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        tar.add(os.path.join(root, file), arcname=file)

            # Push the new archive file to the FTP server
            with open(new_archive_file, 'rb') as f:
                ftp.storbinary('STOR ' + archive_file, f)

            # Delete the extracted files and the new archive file
            os.remove(new_archive_file)
            shutil.rmtree(extract_dir)

            # Remove the original archive file from the push dir
            os.remove(os.path.join(push_dir, archive_file))

    # Wait 10 seconds
    time.sleep(10)

# Close the FTP connection
ftp.quit()