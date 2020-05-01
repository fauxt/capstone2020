def package_downloads(download_job, client_id, job_id):
    folder_name = download_job['folder_name']
    file_name = download_job['file_name'].replace(" ", "_") +\
        '.' + download_job['file_type']
    data = [{
        'folder_name': folder_name,
        'file_name': file_name,
        'data': download_job['data']
    }]

    return_download = {
        'client_id': client_id,
        'job_id': job_id,
        'data': data,
    }
    return return_download
