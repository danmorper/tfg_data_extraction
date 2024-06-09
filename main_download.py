from download.download import Download
import calendar
from datetime import datetime

def main(mm_yyyy: str):
    start_date = f"01-{mm_yyyy}"
    
    # Dividir correctamente mm_yyyy en month y year
    month, year = mm_yyyy.split("-")
    year = int(year)
    month = int(month)
    
    end_day = calendar.monthrange(year, month)[1]  # Obtiene el último día del mes
    end_date = f"{end_day:02d}-{mm_yyyy}"
    download = Download(start_date, end_date, mm_yyyy)
    download.download_data()