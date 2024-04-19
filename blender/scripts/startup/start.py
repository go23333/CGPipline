        
def register():
    import getpass
    import sys

    user_name = getpass.getuser()

    if user_name == "zhaocunxi":
        paths = [r"D:\Documents\ZCXCode\CGPipline\blender\scripts"]
    else:
        paths = [r"O:\CGPipline\blender\scripts"]
    for path in paths:
        if path not in sys.path:
            sys.path.append(path)


def unregister():
    pass