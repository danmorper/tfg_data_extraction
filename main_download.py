from download.download import Download

def main(mm_yyyy: str):
    start_date = "01-" + mm_yyyy
    end_date = "31-" + mm_yyyy
    download = Download(start_date, end_date, mm_yyyy)
    download.download_data()