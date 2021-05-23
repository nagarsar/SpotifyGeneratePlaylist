from datetime import datetime,timedelta


def get_time_delta(date1, date2, plage=5000):
    """
    inputs date format : yyyy-mm-dd
    return tuple
    abs val of days between date1 and date2
    the percentage difference between date1 and date2 considering a range
    """
    delta_days=0
    percentage=1.0
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")

        delta = d2 - d1
        delta_days = abs(delta.days)
        plage = plage 
        percentage = (-delta_days + plage)/plage

    except:
        pass

    return delta_days, percentage



def get_date(date1,days):
    """
    inputs date format : yyyy-mm-dd
    return 
    date with format yyyy-mm-dd
    """
    date_1 = datetime.strptime(date1, "%Y-%m-%d")

    end_date = date_1 + timedelta(days=days)
    end_date = end_date.strftime("%Y-%m-%d")

    return end_date