import os
import pandas as pd
import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def merge_csv_files(directory):
    data_frames = []

    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            print(f"📂 Reading file: {file_path}")
            df = pd.read_csv(file_path)
            data_frames.append(df)

    merged_df = pd.concat(data_frames, ignore_index=True)
    return merged_df


def upload_to_drive(file_path):
    print(f"💡 Uploading {file_path} to Google Drive")
    file_drive = drive.CreateFile({'title': os.path.basename(file_path)})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    print(f"✅ File {file_path} uploaded to Google Drive")

    print("Setting file permissions to public...")
    file_drive.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })
    print("✅ File permissions set to public. Done.")
    return file_drive['alternateLink']


if __name__ == "__main__":
    csv_directory = 'seperate_csvs'
    role_name = 'AIML_Engineer'
    output_csv = role_name + '_merged.csv'
    
    merged_df = merge_csv_files(csv_directory)

    # go through each row and find if a pdf file is present with name same as 'name' column in the row, in the csv_directory folder
    for index, row in merged_df.iterrows():
        name = row['name']
        pdf_filename = os.path.join(csv_directory, f'{name}.pdf')
        docx_filename = os.path.join(csv_directory, f'{name}.docx')
        if os.path.exists(pdf_filename):
            resume_gdrive_link = upload_to_drive(pdf_filename)
            merged_df.at[index, 'resume_file_gdrive_link'] = resume_gdrive_link
        elif os.path.exists(docx_filename):
            resume_gdrive_link = upload_to_drive(docx_filename)
            merged_df.at[index, 'resume_file_gdrive_link'] = resume_gdrive_link
        else:
            merged_df.at[index, 'resume_file_gdrive_link'] = 'undefined'

    merged_df.to_csv(output_csv, index=False)
    print(f"Merged CSV file with Google Drive links saved locally as {
          output_csv}")
    final_csv_drive_link = upload_to_drive(output_csv)
    print(f"💯 Final CSV file uploaded to Google Drive with link: {
          final_csv_drive_link}")
