import sys


def log(message):
    message = str(message)
    message = getInfos(1) + "\n" + message

    sys.stdout.write(message + "\n")

class FakeException(Exception):
    pass
def getInfos(level):
    """Get information from where the method has been fired.
    Such as module name, method, line number...

    Args:
        level (int): Level

    Returns:
        str: The info

    """
    try:
        raise FakeException("this is fake")
    except Exception:
        # get the current execution frame
        f = sys.exc_info()[2].tb_frame

    # go back as many call-frames as was specified
    while level >= 0:
        f = f.f_back
        level = level - 1

    infos = ""

    # Module Name
    moduleName = f.f_globals["__name__"]
    if moduleName != "__ax_main__":
        infos += moduleName + " | "

    # Class Name
    # if there is a self variable in the caller's local namespace then
    # we'll make the assumption that the caller is a class method
    obj = f.f_locals.get("self", None)
    if obj:
        infos += obj.__class__.__name__ + "::"

    # Function Name
    functionName = f.f_code.co_name
    if functionName != "<module>":
        infos += functionName + "()"

    # Line Number
    lineNumber = str(f.f_lineno)
    infos += " line " + lineNumber + ""

    if infos:
        infos = "[" + infos + "]"

    return infos


if __name__ == "__main__":
    log("TEST")