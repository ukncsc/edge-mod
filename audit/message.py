
def format_audit_message(error_message, user_message):
    message = error_message

    if user_message:
        message = message + ('\n' if message else '') + user_message

    return message
