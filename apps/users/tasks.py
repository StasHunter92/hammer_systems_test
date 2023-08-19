import time


# ----------------------------------------------------------------------------------------------------------------------
# Create tasks
def send_sms(one_time_password: str) -> str:
    """
    SMS imitation for the task (ex. Celery)
    Args:
        one_time_password: generated one time password
    Returns:
        string with 'Success' status
    """
    time.sleep(2)
    print(f'OTP: {one_time_password}')
    return 'Success'
