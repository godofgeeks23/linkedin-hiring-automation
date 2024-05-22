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
            df = pd.read_csv(file_path)
            data_frames.append(df)

    merged_df = pd.concat(data_frames, ignore_index=True)
    return merged_df

def download_file(url, output_path):
    response = requests.get(url)
    with open(output_path, 'wb') as file:
        file.write(response.content)

def upload_to_drive(file_path):
    file_drive = drive.CreateFile({'title': os.path.basename(file_path)})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()

    # Enable sharing and get the shareable link
    file_drive.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })
    return file_drive['alternateLink']

if __name__ == "__main__":
    csv_directory = 'seperate_csvs'
    role_name = 'UIUX'
    output_csv = role_name + '_merged.csv'
    download_dir = 'downloads'

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    merged_df = merge_csv_files(csv_directory)

    if 'resume_link' in merged_df.columns:
        merged_df['drive_link'] = ''

        for index, row in merged_df.iterrows():
            pdf_url = row['resume_link']
            if pdf_url == 'undefined':
                merged_df.at[index, 'drive_link'] = 'undefined'
            else:
                pdf_filename = os.path.join(download_dir, f'file_{index}.pdf')
                download_file(pdf_url, pdf_filename)
                drive_link = upload_to_drive(pdf_filename)
                merged_df.at[index, 'drive_link'] = drive_link


    merged_df.to_csv(output_csv, index=False)
    print(f"Merged CSV file with Google Drive links saved locally as {output_csv}")
    final_csv_drive_link = upload_to_drive(output_csv)
    print(f"Final CSV file uploaded to Google Drive with link: {final_csv_drive_link}")
