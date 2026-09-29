import subprocess
import os


substancePainterPath = "C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe"
modulePath = "D:\Documents\ZCXCode\SubstanceTest\deploy"
env = os.environ.copy()
env["SUBSTANCE_PAINTER_PLUGINS_PATH"] = modulePath

# 启动进程
process = subprocess.Popen([substancePainterPath], 
                          text=True,
                          env=env)
print(f"返回码: {process.returncode}")