import os

import uis.windows as window
import uis.sp_utilis as ut
from importlib import reload
reload(window)
reload(ut)


import substance_painter.application as app
import substance_painter.resource as res



if __name__ == "__main__":
    res.import_project_resource(
        r"E:\AssetLibrary\Assets\1Mpsqcd\1Mpsqcd.spsm",
        res.Usage.SMART_MATERIAL,
        name="Test",
    )
    # resource = ut.GetSelectedResource()
    # url = resource.url
    # print(url)


















