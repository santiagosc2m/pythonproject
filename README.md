# Google Drive Backup Automation


This Python script was written as a college project to automate the process of backing up files to Google Drive, implementing an incremental backup strategy.

## Requirements

- Python 3.x
- Google APIs Client Library (`google-auth`, `google-auth-oauthlib`, `google-api-python-client`)
- `pytz` for timezone handling

## Setup

1. **Google API Configuration**
   - Obtain credentials by creating a project on the Google Developer Console.
   - Download the JSON file containing your credentials and save it to your local machine.

2. **Python Environment Setup**
   - Install required Python packages using `pip`:
     ```bash
     pip install google-auth google-auth-oauthlib google-api-python-client pytz
     ```

3. **Script Configuration**
   - Set the `folder_path` variable to the directory path containing the files you want to back up.

4. **Mannualy add this scrip in scheduled tasks**

## Script Overview

### Authentication

The script handles authentication with Google Drive using OAuth 2.0. It stores and refreshes credentials automatically.

### Google Drive Operations

- **Folder Creation:** Creates a folder named "Auto_backup" if it doesn't exist on Google Drive.
- **File Listing:** Retrieves a list of files currently stored in the "Auto_backup" folder.
- **File Upload:** Uploads new files from the local directory to Google Drive.
- **File Update:** Updates files on Google Drive if their local versions have been modified since the last backup.

### Backup Log

The script writes a log file (`backup.log`) in the specified `folder_path` directory. This log file includes the timestamp of the last backup execution and the names of files that were updated during the backup process.

### Usage

- Run the script to synchronize files between the local directory and Google Drive:
  ```bash
  python GDrive_backup.py
