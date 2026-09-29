import subprocess
import os
import time
import openpyxl as op
import json
import tempfile
import sys

from openpyxl import Workbook
from openpyxl.styles import Font

from PyQt5 import QtCore
from PyQt5 import QtWidgets
# from PyQt5 import QtGui

import win32api
import win32con

from dayu_widgets.label import MLabel
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.combo_box import MComboBox
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import getpass
import sys


def get_app_root():
    if getattr(sys, 'frozen', False):
        # 应用程序被打包成了exe
        return os.path.dirname(sys.executable)
    else:
        return False
app_root = get_app_root()
print(f"应用程序根目录: {app_root}")


user_name = getpass.getuser()

if user_name == "songshunjie":
    root_path = R"D:\a1\gc\git\CGPipline\maya\ZynnMaya\scripts"
    code_path = root_path+'/mayaTools/mayaBlackBox/'
else:
    root_path = R'S:\CGPipline\maya\ZynnMaya\scripts'
    code_path = root_path+'/mayaTools/mayaBlackBox/'
    
if not os.path.exists(root_path):     #外包环境
    if app_root:
        root_path = app_root
        code_path = root_path+'/mayaBlackBox/'
    else:
        root_path = 'Y:/scripts'
        code_path = root_path+'/mayaTools/mayaBlackBox/'




vendor_path = R'S:\CGPipline\maya\ZynnMaya\vendor'

try:
    sys.path.remove(code_path)
    sys.path.remove(vendor_path)
    
except:
    pass

sys.path.insert(0,code_path)
sys.path.insert(1,vendor_path)

FILTERS = ['QunJi_']





def readExcel(excel_path):
    df=op.load_workbook(excel_path,data_only=True)
    sheet=df['Sheet1']

    asset_dict={}
    i=0
    #确定行和列
    rowcount=sheet.max_row
    colcount=3
    #读取所需的Excel内容
    for i in range(1,rowcount+1):
        row_data_list=[]
        for j in range(1,colcount+1):
            row_data_list.append(sheet.cell(row=i,column=j).value)
        if row_data_list[0]:
            sc_name = row_data_list[0].split('_')[1]
            try:
                asset_dict[row_data_list[0]].append([row_data_list[1].split('.')[0],row_data_list[2]])
            except:
                asset_dict[row_data_list[0]] = []
                asset_dict[row_data_list[0]].append([row_data_list[1].split('.')[0],row_data_list[2]])

    
    return asset_dict,sc_name

def fbxDictGet(fbx_folder_path,sc_name=''):
    fbx_dict = {}
    for root, dirs, files in os.walk(fbx_folder_path):
        root = root.split('\\')[-1]
        for file in files:
            #判断fbx后缀名以及场次名称是否符合规则
            if '.fbx' in str(file).lower() and sc_name in root:
                try:
                    fbx_dict[root].append(file)
                except:
                    fbx_dict[root] = []
                    fbx_dict[root].append(file)
    
    return fbx_dict
          



def dataComparison(excel_assets_dict,fbx_dict,save_path):

    for cam_folder_name,fbx_list in fbx_dict.items():

        file_split = cam_folder_name.split('_')
        #获取镜头号
        cam = file_split[2]
        fbx_base_name_list = []
        for fbx in fbx_list:
            fbx_base_name = fbx.split('_',4)[-1].rsplit('_',1)[0]
            fbx_base_name_list.append(fbx_base_name)

        if cam_folder_name not in excel_assets_dict:    #fbx文件夹存在而excel不存在时跳过
            print(cam_folder_name+'不在表中')
            continue
        for excel_asset_data in excel_assets_dict[cam_folder_name]:
            for fbx_base_name in fbx_base_name_list:
                if fbx_base_name == excel_asset_data[0].rsplit('_',1)[0]:
                    #当fbx存在时,使excel中对应的资产数量减一
                    excel_asset_data[1] = excel_asset_data[1]-1
        
    # print(excel_assets_dict)

    wb = Workbook()
    ws = wb.active

    # 写入数据行（字典的值）
    row_num=1   #行数

    for cam_index, fbx_datas in excel_assets_dict.items():  # 从第2行开始写入数据
        if fbx_datas:
            write_switch = False
            for fbx_data in fbx_datas:
                #当fbx数量不为0时,记录fbx资产
                if fbx_data[1] != 0:
                    row_num_str = str(row_num)
                    write_switch = True
                    ws['A'+row_num_str] = cam_index
                    #根据条件设置字体颜色,缺少为红色,多余为蓝色
                    if fbx_data[1] >0:
                        ws['B'+row_num_str] = fbx_data[0]+'  缺少数量 '+str(fbx_data[1])
                        ws['B'+row_num_str].font = Font(color="FF0000")  # 红色
                    elif fbx_data[1] <0:
                        ws['B'+row_num_str] = fbx_data[0]+'  多余数量 '+str(abs(fbx_data[1]))
                        ws['B'+row_num_str].font = Font(color="0000FF")  # 蓝色
                    
                    #每次写入后行号加一
                    row_num += 1

            if write_switch:
                #每个镜头之间间隔一行空行
                row_num += 1

    # 自动调整列宽以便更好地显示内容
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # 获取列字母
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # 保存工作簿
    wb.save(save_path+"excel_examine.xlsx")







class FbxDetectionWindow(QtWidgets.QWidget, MFieldMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.aai_shot_path='/Game/Shots/'
        self.asset_shot_path='/Game/Assets/Shots/'
        
        self.uii()

    def uii(self):   
        self.setWindowTitle('动画fbx完整性检测工具')
        self.resize(300,200)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        self.excel_path=MLineEdit().file().medium()
        self.excel_path.setPlaceholderText(self.tr("选择需要检测的Excel文件"))
        self.fbx_path=MLineEdit().folder().medium()
        self.fbx_path.setPlaceholderText(self.tr("选择需要检测的fbx文件夹"))
        create_folder=MPushButton(text="开始检测")
        create_folder.clicked.connect(self.execute)
        

        folder_lay.addWidget(self.excel_path)
        folder_lay.addWidget(self.fbx_path)
        folder_lay.addWidget(create_folder)


        import_lay=QtWidgets.QVBoxLayout()
        
        lay.addLayout(folder_lay)
        lay.addLayout(import_lay)
        self.setLayout(lay)


    def execute(self):
        # excel_path = 'Y:/SSDSY_CS/Progress/镜头资产引用表/EP001/sc001.xlsx'
        # fbx_folder_path = 'Y:/SSDSY_CS/EP001/Animation/fbx'
        excel_path = self.excel_path.text()
        fbx_folder_path = self.fbx_path.text()

        excel_assets_dict,sc_name = readExcel(excel_path)
        fbx_dict = fbxDictGet(fbx_folder_path,sc_name)
        save_path = "d:/Desktop/"
        dataComparison(excel_assets_dict,fbx_dict,save_path)



def FbxDetectionWindowStart():
    with application() as app:
        global fbx_detection
        fbx_detection = FbxDetectionWindow()
        dayu_theme.apply(fbx_detection)
        fbx_detection.show()





class MyThread(QtCore.QThread):

    def __init__(self,maya_bin,method):
        super(MyThread,self).__init__()

        
        self.maya_bin=maya_bin
        self.method=method

    def run(self):

        if self.method=='an_fbx':
            self.cmdAnFbx()

        elif self.method=='camera_detect':
            self.cmdCameraDetect()



    def cmdAnFbx(self):

        # "D:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" D:\a1\gc\git\CGPipline\maya\ZynnMaya\scripts\mayaTools\SongShunJie\BG_AnimationAutoBake_v2.py

        mayapy_path=self.maya_bin+'\\mayapy.exe'
        py_path=code_path+R'BG_AnimationAutoBake_v2.py'

        cmd_command=f'"{mayapy_path}" '+py_path
        print(cmd_command)

        subprocess.run(cmd_command)


    def cmdCameraDetect(self):

        mayapy_path=self.maya_bin+'\\mayapy.exe'
        py_path=code_path+R'CameraDetection.py'

        cmd_command=f'"{mayapy_path}" '+py_path
        print(cmd_command)

        subprocess.run(cmd_command)



class AnExport(QtWidgets.QWidget, MFieldMixin):
    def __init__(self,maya_bin,parent=None):
        super().__init__(parent)

        self.start_endK_d=None
        self.start_offset=0
        self.end_offset=0


        self.maya_bin=maya_bin

        self.UI()


    def UI(self):   
        self.setWindowTitle('Maya动画FBX批量导出')
        self.resize(420,200)
        lay=QtWidgets.QVBoxLayout()

        method_lay=QtWidgets.QVBoxLayout()
        
        #文件输入框
        mayapy_lay=QtWidgets.QVBoxLayout()
        excel_path_label=MLabel('选择Excel文件:')
        self.excel_path_text=MLineEdit().file().medium()
        self.excel_path_text.setPlaceholderText(self.tr("选择Excel镜头表文件"))
        self.excel_path_text.textChanged.connect(self.initKeyValue)

        maya_path_label=MLabel('选择maya文件夹:')
        self.maya_path_text=MLineEdit().folder().medium()
        self.maya_path_text.setPlaceholderText(self.tr("选择maya文件夹"))
        self.maya_path_text.textChanged.connect(self.initKeyValue)

        mayapy_lay.addWidget(excel_path_label)
        mayapy_lay.addWidget(self.excel_path_text)
        mayapy_lay.addWidget(maya_path_label)
        mayapy_lay.addWidget(self.maya_path_text)


        #Excel与maya检测
        camera_detect=MPushButton(text="检测Excel文件与所选maya文件夹是否匹配")
        camera_detect.clicked.connect(self.detectionFile)

        #偏移帧布局
        lay_offset=QtWidgets.QHBoxLayout()
        start_offset_label=MLabel('起始偏移帧:')
        self.start_offset_text=MLineEdit()
        self.start_offset_text.setText(str(self.start_offset))
        end_offset_label=MLabel('结束偏移帧:')
        self.end_offset_text=MLineEdit()
        self.end_offset_text.setText(str(self.end_offset))

        lay_offset.addWidget(start_offset_label)
        lay_offset.addWidget(self.start_offset_text)
        lay_offset.addWidget(end_offset_label)
        lay_offset.addWidget(self.end_offset_text)

        #错误提示窗口
        self.error_label=MLabel('')
        self.error_label.setMaximumHeight(18)
        #动画fbx批量导出
        self.fbx_path_text=MLineEdit().folder().medium()
        self.fbx_path_text.setPlaceholderText(self.tr("FBX导出目录"))
        an_export=MPushButton(text="烘焙并导出FBX到指定位置")
        #按下创建json文件
        # an_export.pressed.connect(self.createJson)
        an_export.clicked.connect(self.execute)
        #松开执行mayapy代码
        # an_export.clicked.connect(self.threadAn)

        prompt_label=MLabel('执行前请确保已经获取所有所需的引用文件')
        prompt_label.setMinimumHeight(36)

        
        method_lay.addLayout(mayapy_lay)
        method_lay.addWidget(self.error_label)
        method_lay.addLayout(lay_offset)
        method_lay.addStretch()
        method_lay.addWidget(camera_detect)
        method_lay.addWidget(self.fbx_path_text)
        method_lay.addWidget(an_export)
        method_lay.addStretch()

        import_lay=QtWidgets.QVBoxLayout()
        

        lay.addLayout(method_lay)
        
        lay.addLayout(import_lay)
        self.setLayout(lay)

    def execute(self,*args):
        
        fbx_export_path=self.fbx_path_text.text()
        
        #获取文件路径
        dir_path =self.maya_path_text.text()
        ma_path=[]
        for dirpath, dirnames, filenames in os.walk(dir_path):
            #过滤无用文件夹
            if 'incrementalSave' not in dirpath and '.mayaSwatches' not in dirpath:
                for filename in filenames:
                    if '.ma' in filename or '.mb' in filename:
                        path=os.path.join(dirpath, filename)
                        ma_path.append(path.replace('\\','/'))
        print(ma_path)

        # if ma_path:
        #     if self.maya_bin.split('\\')[-2].lower() == 'maya2023':
        #         self.createJson2023(ma_path,fbx_export_path)
        #         self.cmdStart()
        #     else:
        #         #通过文件路径打开ma文件
        #         for ma in ma_path:
        #             self.createJson(ma,fbx_export_path)
        #             self.cmdStart()
        #             print(ma)

        # 通过文件路径打开ma文件
        for ma in ma_path:
            self.createJson(ma,fbx_export_path)
            self.cmdStart()
            print(ma)



    #初始化excel的数据
    def initKeyValue(self):
        self.start_endK_d=None
        
        
    def excelGetOld(self,*args):
		
        #获取Excel表格信息
        # excel_path=cmds.textField('excel',text=1,q=1)
        df=op.load_workbook(self.excel_path_text.text(),data_only=True)
        sheet=df['镜头表']
        
        all_list=[]
        i=0
        #确定行和列
        rowcount=sheet.max_row
        colcount=7
		#读取所需的Excel内容
        for i in range(13,rowcount+1):
            value_list=[]
            for j in range(3,colcount+1):
                value_list.append(sheet.cell(row=i,column=j).value)
            all_list.append(value_list)
        return all_list
    
    def excelGet(self):

        #获取Excel表格信息
        # excel_path=cmds.textField('excel',text=1,q=1)
        df=op.load_workbook(self.excel_path_text.text(),data_only=True)
        sheet=df['Sheet']
        
        all_list=[]
        i=0
        #确定行和列
        rowcount=sheet.max_row
        colcount=6
		#读取所需的Excel内容
        for i in range(2,rowcount+1):
            value_list=[]
            for j in range(1,colcount+1):
                value = sheet.cell(row=i,column=j).value
                if value:
                    value_list.append(sheet.cell(row=i,column=j).value)
            if value_list:
                all_list.append(value_list)
        return all_list
    
    def excelGetData(self):
        excel_datas = None
        #旧版格式获取失败时,使用新版格式
        try:
            excel_datas = self.excelGetOld()
        except:
            excel_datas = self.excelGet()

        return excel_datas



    def excel_key_data(self):
        
        #判断excel数据是否已经获取过
        if self.start_endK_d==None:

            sc=[]
            cam=[]
            start_endK=[]
            excel_data_list=self.excelGetData()
            ep=excel_data_list[0][0]
            self.start_endK_d={}
            for i in excel_data_list:
                if i[0]==ep and len(i)>=5:
                    start_end_c=[]
                    sc.append(i[1])
                    cam.append(i[2])
                    start_end_c.append(i[3])
                    start_end_c.append(i[4])
                    start_endK.append(start_end_c)
                    self.start_endK_d[i[2]]=start_end_c
            # print(self.start_endK_d)
            return self.start_endK_d
        else :
            return self.start_endK_d
    
    def detectionFile(self,*args):
        
        #获取文件路径
        dir_path =self.maya_path_text.text()
        excel_path=self.excel_path_text.text()

        file_null=False
        flie_exist=False
        
        if dir_path and excel_path:
            if excel_path.split('.')[-1]=='xlsx':
                start_endK_d=self.excel_key_data()
                ma_file=[]
                for dirpath, dirnames, filenames in os.walk(dir_path):
                    for filename in filenames:
                        if filename.split('.')[-1]=='ma'  or filename.split('.')[-1]=='mb':
                            if any(sub in filename for sub in FILTERS):     #群集使用全名
                                ma_file.append(filename.rsplit('.',1)[0])
                            else:
                                ma_file.append(filename.rsplit('_',1)[0])

                # print(start_endK_d)
                # print(ma_file)
                if ma_file:
                    for ma_name in ma_file:	
                        if ma_name not in start_endK_d :
                            file_null=True
                        else:
                            flie_exist=True

                    if file_null==True and flie_exist==False:
                        self.error_label.setText('Excel与当前所选文件夹内容不匹配')
                        self.error_label.setStyleSheet('color: red;')
                    if file_null==True and flie_exist==True:
                        self.error_label.setText('Excel与当前所选文件夹内容不完全匹配')
                        self.error_label.setStyleSheet('color: yellow;')
                    if file_null==False and flie_exist==True:
                        self.error_label.setText('Excel与当前所选文件夹内容匹配')
                        self.error_label.setStyleSheet('color: white;')

                else:
                    self.error_label.setText('未在当前文件夹下找到maya文件')
                    self.error_label.setStyleSheet('color: red;')
            else:
                self.error_label.setText('请选择后缀为xlsx的表格文件')
                self.error_label.setStyleSheet('color: red;')
        else:
            self.error_label.setText('输入框不能为空')
            self.error_label.setStyleSheet('color: red;')


    def threadAn(self):
        self.t_an=MyThread(self.maya_bin,'an_fbx')
        self.t_an.start()

    def createJson2023(self,maya_paths,fbx_export_path):
        json_datas = []
        for maya_path in maya_paths:
            start_offset = self.start_offset_text.text()
            end_offset = self.end_offset_text.text()
            if any(sub in maya_path for sub in FILTERS):     #群集使用全名
                base_name = maya_path.rsplit('/')[-1].rsplit('.',1)[0]
            else:
                base_name = maya_path.rsplit('/')[-1].rsplit('_',1)[0]
            start_endK_d = self.excel_key_data()
            temp_path = tempfile.gettempdir()
            # temp_path=temp_path.replace('\\','/')
            json_path = os.path.join(temp_path,'mayajson.json')
            # print(json_path)
            #创建写入json文件的字典
            path_dict={}
            
            for k,v in start_endK_d.items():
                # print(k,v)
                # print(base_name)
                if k == base_name:
                    path_dict['frame']=v
                    break
            path_dict['maya_path']=maya_path
            path_dict['fbx_export_path']=fbx_export_path
            path_dict['offset_frame']=[start_offset,end_offset]
            path_dict['root_path']=root_path.replace('\\','/')
        
            json_datas.append(path_dict)
        # print(path_dict)
        #将材质名称和包含的贴图创建为json文件
        with open(json_path,'w') as json_file:
            json.dump(json_datas,json_file)
        
        
        

    def createJson(self,maya_path,fbx_export_path):
        start_offset = self.start_offset_text.text()
        end_offset = self.end_offset_text.text()
        if any(sub in maya_path for sub in FILTERS):     #群集使用全名
            base_name = maya_path.rsplit('/')[-1].rsplit('.',1)[0]
        else:
            base_name = maya_path.rsplit('/')[-1].rsplit('_',1)[0]
        start_endK_d = self.excel_key_data()
        temp_path = tempfile.gettempdir()
        # temp_path=temp_path.replace('\\','/')
        json_path = os.path.join(temp_path,'mayajson.json')
        #创建写入json文件的字典
        path_dict={}
        
        for k,v in start_endK_d.items():
            if k == base_name:
                path_dict['frame']=v
                break
        path_dict['maya_path']=maya_path
        path_dict['fbx_export_path']=fbx_export_path
        path_dict['offset_frame']=[start_offset,end_offset]
        path_dict['root_path']=root_path.replace('\\','/')
        # print(path_dict)

        #将材质名称和包含的贴图创建为json文件
        with open(json_path,'w') as json_file:
            json.dump(path_dict,json_file)
            
    def cmdStart(self):

        #获取mayabatch路径
        mayabatch_path = self.maya_bin+'\\mayabatch.exe'
        mel_path = code_path+R'MayaBackMel.mel'
        mel_path = mel_path.replace('\\','/')
        plugin_path = code_path
        plugin_path = plugin_path.replace('\\','/')

        if self.maya_bin.split('\\')[-2].lower() == 'maya2018':
            plugin_name = 'BG_AnimationAutoBake'
        elif self.maya_bin.split('\\')[-2].lower() == 'maya2023':
            plugin_name = 'BG_AnimationAutoBake_v2'
        cmd_command = f'"{mayabatch_path}" -command "source \\"{mel_path}\\";backgroundCMD \\"{plugin_path}\\" \\"{plugin_name}\\";"'
        print(cmd_command)

        subprocess.run(cmd_command)





class mw(QtWidgets.QWidget, MFieldMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.maya_versions = ['2018','2023']
        
        self.uii()

    def uii(self):   
        self.setWindowTitle('Maya文件批处理')
        self.resize(360,200)
        lay=QtWidgets.QVBoxLayout()

        method_lay=QtWidgets.QVBoxLayout()
        
        #mayapy路径
        mayapy_lay=QtWidgets.QVBoxLayout()
        mayapy_label=MLabel('MAYA2018安装目录(如果未识别到,请手动选择bin文件夹):')
        mayapy_label.setMinimumHeight(36)

        self.maya_versions_cb = MComboBox()
        self.maya_versions_cb.addItems(self.maya_versions)
        self.maya_versions_cb.setMinimumWidth(100)
        self.maya_versions_cb.setMinimumHeight(30)
        self.maya_versions_cb.currentIndexChanged.connect(self.setMayaVersions)
        # self.cbSceneName.setEditable(True)
        
        self.mayapy_exe=MLineEdit().folder().medium()
        self.mayapy_exe.setPlaceholderText(self.tr("选择MAYA的bin文件夹"))
        self.mayapy_exe.setText(self.getMayapyPath('2018'))
        #检测到内容改变后规范文件路径名称
        self.mayapy_exe.textChanged.connect(self.binSuffix)
        mayapy_lay.addWidget(mayapy_label)
        mayapy_lay.addWidget(self.maya_versions_cb)
        mayapy_lay.addWidget(self.mayapy_exe)


        #摄像机检测
        camera_detect=MPushButton(text="摄像机轴向检测")
        camera_detect.clicked.connect(self.cmdCameraDetect)

        #动画fbx批量导出
        an_export=MPushButton(text="动画fbx批量导出")
        an_export.clicked.connect(self.cmdANfbx)

        #动画fbx完整性检测工具
        fbx_detection=MPushButton(text="动画fbx完整性检测工具")
        fbx_detection.clicked.connect(self.fbxDetection)

        method_lay.addLayout(mayapy_lay)
        method_lay.addStretch()
        method_lay.addWidget(camera_detect)
        method_lay.addWidget(an_export)
        method_lay.addWidget(fbx_detection)
        method_lay.addStretch()

        import_lay=QtWidgets.QVBoxLayout()
        

        lay.addLayout(method_lay)
        
        lay.addLayout(import_lay)
        self.setLayout(lay)


    #执行摄像机检测程序
    def cmdCameraDetect(self):

        self.t_cam_det=MyThread(self.mayapy_exe.text(),'camera_detect')
        self.t_cam_det.start()

    #执行动画fbx完整性检测程序
    def fbxDetection(self):
        FbxDetectionWindowStart()

        # import BG_FbxDetection
        # BG_FbxDetection.start()
        


    #执行动画导出程序
    def cmdANfbx(self):

        with application() as app:
            global test_an
            test_an = AnExport(self.mayapy_exe.text())
            dayu_theme.apply(test_an)
            test_an.show()




        # self.t_an_fbx=MyThread(self.mayapy_exe.text(),'an_fbx')
        # self.t_an_fbx.start()

    


    def binSuffix(self):
        oldtext=self.mayapy_exe.text()
        if 'bin' in self.mayapy_exe.text():
            self.mayapy_exe.setText(oldtext.split('bin')[0]+'bin')
        


    def setMayaVersions(self):
        maya_version = self.maya_versions_cb.currentText()
        self.mayapy_exe.setText(self.getMayapyPath(maya_version))
        
        

    def getMayapyPath(self,maya_version):

        maya_name = 'Maya'+maya_version

        # path = R'SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders'
        path = Rf'SOFTWARE\Autodesk\Maya\{maya_version}\Setup\InstallPath'
        #通过获取Windows注册表查找软件
        key = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, path, 0, win32con.KEY_READ)
        
        i=0
        while i<100000:
            try:
                value= win32api.RegEnumValue(key,i)
                i+=1
                # print(value)
                if maya_name in str(value):
                    mayapy_path=value[1].split('bin')[0]+'bin'
                    break
            except:
                break
        if mayapy_path:
            print(mayapy_path)
            return mayapy_path
        else:
            return ''
        






def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()


start()

