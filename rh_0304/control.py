
def ptc_control(is_ptc_on, temperature, temp_goal):
    if temperature >= temp_goal:
        if is_ptc_on:
            print('# ptc off')
            return False
        else:
            print('# ptc off continue')
            return is_ptc_on
    else:
        if is_ptc_on:
            print('# ptc on continue')
        else:
            print('# ptc on')
            return True

