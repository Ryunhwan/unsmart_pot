import urllib.request

from database import *

def check_internet_on():
    host = 'http://google.com'
    try:
        urllib.request.urlopen(host) #Python 3.x
        print('internet connect')
        return True
    except:
        print('internet disconnect')
        return False


def check_led_timer(hour_now, min_now):
    led_start_hour = get_data(db_control_data_loc + '/led_start_hour')
    led_start_min = get_data(db_control_data_loc + '/led_start_min')
    led_end_hour = get_data(db_control_data_loc + '/led_end_hour')
    led_end_min = get_data(db_control_data_loc + '/led_end_min')
    is_led_on = get_data(db_control_data_loc + '/light')
    is_auto = get_data(db_control_data_loc + '/auto')
    is_led_auto = get_data(db_control_data_loc + '/led_auto')
    if not is_auto:
        return
    if not is_led_auto:
        return

    # 끝나는 시간이 오히려 과거일 경우 다음날로 설정
    if led_end_hour < led_start_hour or (led_end_hour==led_start_hour and led_end_min < led_start_min):
        led_end_hour+=24

    # print('led_start_hour: ', led_start_hour)
    # print('hour_now: ', hour_now)
    # print('led_end_hour: ', led_end_hour)
    # print('led_start_min: ', led_start_min)
    # print('min_now: ', min_now)
    # print('led_end_min: ', led_end_min)

    if hour_now < led_start_hour:
        if is_led_on:
            print('# led off')
            set_data(db_control_data_loc + '/light', False)
            return
        if not is_led_on:
            print('# led off continue')
            return

    elif hour_now == led_start_hour:
        if min_now < led_start_min:
            if is_led_on:
                print('# led off')
                set_data(db_control_data_loc + '/light', False)
                return
            if not is_led_on:
                print('# led off continue')
                return
        elif min_now == led_start_min:
            if is_led_on:
                print('# led on continue')
                return
            if not is_led_on:
                print('# led on')
                set_data(db_control_data_loc + '/light', True)
                return
        elif led_start_min < min_now < led_end_min:
            if is_led_on:
                print('# led on continue')
                return
            if not is_led_on:
                print('# led on')
                set_data(db_control_data_loc + '/light', True)
                return
        elif min_now == led_end_min:
            return
        elif min_now > led_end_min:
            return

    elif led_start_hour < hour_now < led_end_hour:
        if is_led_on:
            print('# led on continue')
            return
        if not is_led_on:
            print('# led on')
            set_data(db_control_data_loc + '/light', True)
            return

    elif hour_now == led_end_hour:
        if min_now < led_start_min:
            return
        elif min_now == led_start_min:
            return
        elif led_start_min < min_now < led_end_min:
            if is_led_on:
                print('# led on continue')
                return
            if not is_led_on:
                print('# led on')
                set_data(db_control_data_loc + '/light', True)
                return
        elif min_now == led_end_min:
            if is_led_on:
                print('# led off')
                set_data(db_control_data_loc + '/light', False)
                return
            if not is_led_on:
                print('# led off continue')
                return
        elif min_now > led_end_min:
            if is_led_on:
                print('# led off')
                set_data(db_control_data_loc + '/light', False)
                return
            if not is_led_on:
                print('# led off continue')
                return

    elif hour_now > led_end_hour:
        if is_led_on:
            print('# led off')
            set_data(db_control_data_loc + '/light', False)
            return
        if not is_led_on:
            print('# led off continue')
            return
