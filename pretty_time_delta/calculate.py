def calc_seconds_float(seconds_float):
    seconds_float = round(seconds_float, 2)

    seconds = int(str(seconds_float).split('.')[0])
    milliseconds = int(str(seconds_float).split('.')[1])

    return(seconds, milliseconds)


def calc_days(seconds):
    seconds = int(seconds)
    seconds_day = 86400

    days = int(seconds // seconds_day)
    remaining_seconds = seconds - (days * seconds_day)

    return (days, remaining_seconds)


def calc_hours(seconds):
    seconds = int(seconds)
    seconds_hour = 3600

    hours = int(seconds // seconds_hour)
    remaining_seconds = seconds - (hours * seconds_hour)

    return (hours, remaining_seconds)


def calc_minutes(seconds):
    seconds = int(seconds)
    seconds_minute = 60

    minutes = int(seconds // seconds_minute)
    remaining_seconds = seconds - (minutes * seconds_minute)

    return (minutes, remaining_seconds)


def calc(seconds):
    seconds_float = float(seconds)

    (
        starting_seconds,
        milliseconds
    ) = calc_seconds_float(seconds_float)

    (
        days,
        remaining_seconds
    ) = calc_days(starting_seconds)

    (
        hours,
        remaining_seconds
    ) = calc_hours(remaining_seconds)

    (
        minutes,
        remaining_seconds
    ) = calc_minutes(remaining_seconds)

    seconds = int(remaining_seconds)

    return(days, hours, minutes, seconds, milliseconds)


class PrettyTimeDelta:
    def __init__(self, seconds):

        (
            self.days,
            self.hours,
            self.minutes,
            self.seconds,
            self.milliseconds
        ) = calc(seconds)

    def format(self):

        formatted_duration = []

        if self.days and self.days == 1:
            formatted_duration.append(f'{self.days} Day')

        elif self.days and self.days >= 2:
            formatted_duration.append(f'{self.days} Days')

        if self.hours and self.hours == 1:
            formatted_duration.append(f'{ self.hours} Hour')

        elif self.hours and self.hours >= 2:
            formatted_duration.append(f'{ self.hours} Hours')

        if self.minutes and self.minutes == 1:
            formatted_duration.append(f'{self.minutes} Minute')

        elif self.minutes and self.minutes >= 2:
            formatted_duration.append(f'{self.minutes} Minutes')

        if self.seconds and self.seconds == 1:
            formatted_duration.append(f'{self.seconds} Second')

        elif self.seconds and self.seconds >= 2:
            formatted_duration.append(f'{self.seconds} Seconds')

        if self.milliseconds and self.milliseconds == 1:
            formatted_duration.append(f'{self.milliseconds} Milliseconds')

        elif self.milliseconds and self.milliseconds >= 2:
            formatted_duration.append(f'{self.milliseconds} Milliseconds')

        if len(formatted_duration) > 1:
            insert_position = len(formatted_duration) - 1
            formatted_duration.insert(insert_position, 'and')

        pretty_time_string = str(" ".join(formatted_duration))

        return pretty_time_string
