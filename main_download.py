from download.download import Download
import calendar
from datetime import datetime

def main(mm_yyyy: str):
    try:
        # Generar la fecha de inicio
        start_date = f"01-{mm_yyyy}"
        month, year = mm_yyyy.split("-")
        year = int(year)
        month = int(month)
        
        # Validar el mes y año
        if not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")
        if year < 1900 or year > 2100:
            raise ValueError(f"Invalid year: {year}")
        
        # Obtener el último día del mes
        end_day = calendar.monthrange(year, month)[1]
        end_date = f"{end_day:02d}-{mm_yyyy}"
        
        # Crear instancia de Download y ejecutar
        download = Download(start_date, end_date, mm_yyyy)
        download.download_data()
    except Exception as e:
        print(f"Error downloading data for {mm_yyyy}: {e}")