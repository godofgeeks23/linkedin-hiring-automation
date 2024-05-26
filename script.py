import os
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def merge_csv_files(directory, output_file):
    data_frames = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            data_frames.append(df)

    merged_df = pd.concat(data_frames, ignore_index=True)

    merged_df.to_csv(output_file, index=False)


def upload_to_drive(file_path):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({'title': os.path.basename(file_path)})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()

    print(f'File {file_path} uploaded to Google Drive.')


if __name__ == "__main__":
    csv_directory = 'seperate_csvs'
    role_name = 'UIUX'
    output_csv = role_name + '_merged.csv'
    merge_csv_files(csv_directory, output_csv)
    print(f"Merged CSV file saved as {output_csv}")
    upload_to_drive(output_csv)
