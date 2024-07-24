from datetime import timedelta
from datetime import date
today = date.today()
print(today)

yesterday = today - timedelta(days = 1)
print(yesterday)