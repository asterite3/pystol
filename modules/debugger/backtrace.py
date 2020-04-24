import traceback

try:
    respond(traceback.format_stack(get_current_frame()))
except Exception as ex:
    traceback.print_exc()
    respond('printing traceback failed: ' + str(ex))
    raise