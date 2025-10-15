from datetime import datetime

from langchain.tools import tool
from pytz import timezone

TIMEZONE = 'America/Sao_Paulo'


@tool('Date_today')
def get_current_datetime():
    """This tool returns the current date and time in Brazil when called."""
    time_format = '%d/%m/%Y %H:%M:%S'
    now = datetime.now(timezone(TIMEZONE)).strftime(time_format)

    return {'result': now}
