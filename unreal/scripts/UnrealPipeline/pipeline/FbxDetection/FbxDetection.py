import os
import unreal
import openpyxl as op
# import maya.cmds as cmds
from openpyxl import Workbook
from openpyxl.styles import Font

from Qt import QtCore
from Qt import QtWidgets

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



def txtWrite(data,desktop_log_name):
    
    desktop_path = "d:/Desktop/"
    # if not os.path.exists(desktop_path):
    #     desktop_path = "c:/Desktop/"
        
    desktop_log_path = desktop_path+desktop_log_name
    file_path = desktop_log_path
    with open(file_path, "w") as file:
        file.write(data+"\n")

def cellSplit(work_book):
    ws = work_book.active
    # 获取所有合并单元格的范围列表
    merged_ranges_list = list(ws.merged_cells.ranges)
    # 遍历每一个合并区域
    for merged_range in merged_ranges_list:
        min_row, min_col, max_row, max_col = merged_range.min_row, merged_range.min_col, merged_range.max_row, merged_range.max_col
        # 获取这个合并区域左上角单元格的值
        merged_value = ws.cell(row=min_row, column=min_col).value
        # 解除合并（如果你想保持内存中工作表未被合并的状态）
        ws.unmerge_cells(start_row=min_row, start_column=min_col, end_row=max_row, end_column=max_col)
        # 将左上角的值填充到原合并区域的所有单元格
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                ws.cell(row=row, column=col).value = merged_value

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
    # print(excel_assets_dict,fbx_dict)

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







class mw(QtWidgets.QWidget, MFieldMixin):

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



def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()