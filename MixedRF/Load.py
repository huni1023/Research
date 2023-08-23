import os
import argparse
import numpy as np
import pandas as pd

from sys import platform
from tqdm import tqdm
from datetime import datetime
from zoneinfo import ZoneInfo

# argument
parser = argparse.ArgumentParser(description= 'Option')
parser.add_argument('--full', action='store_true', default=False,
                    help="load all data and cleaning from the beginning")
args = parser.parse_args() # only python
# args = parser.parse_args(args=[]) # for jupyternotebook


class Load:
    def __init__(self, stuFolder, schFolder, tchFolder, codeBook):
        global args
        
        if 'darwin' in platform:
            self.BASE_DIR = '/Users/huni/Dropbox/[3]Project/[혼합효과 랜덤포레스트_2022]'
        else:
            if os.getlogin() == 'jhun1':
                self.BASE_DIR = r'C:\Users\jhun1\Dropbox\[2]Project\[혼합효과 랜덤포레스트_2022]'
                
            elif os.getlogin() == 'snukh':
                self.BASE_DIR = r'C:\Users\snukh\Downloads\[혼합효과 랜덤포레스트_2022]' 
        rawData_Folder = 'PISA2018'
        codebook_Folder = 'drive-download-20220816T053902Z-001'

        if args.full == True:
            print('>>>>> Init: load raw data')
            print(datetime.now(tz=ZoneInfo("Asia/Seoul")))
            stuFile = [FILE for FILE in os.listdir(os.path.join(self.BASE_DIR, rawData_Folder, stuFolder)) if FILE[-4:] == '.sav'][0]
            schFile = [FILE for FILE in os.listdir(os.path.join(self.BASE_DIR, rawData_Folder, schFolder)) if FILE[-4:] == '.sav'][0]
            tchFile = [FILE for FILE in os.listdir(os.path.join(self.BASE_DIR, rawData_Folder, tchFolder)) if FILE[-4:] == '.sav'][0]

            self.rawStu = pd.read_spss(os.path.join(self.BASE_DIR, rawData_Folder, stuFolder, stuFile))
            self.rawSCH = pd.read_spss(os.path.join(self.BASE_DIR, rawData_Folder, schFolder, schFile))
            self.rawTCH = pd.read_spss(os.path.join(self.BASE_DIR, rawData_Folder, tchFolder, tchFile))
            self.dataLS = [self.rawStu, self.rawSCH, self.rawTCH]

            # desciptive
            print('>> Stu data set', self.rawStu.shape)
            print('>> Sch data set', self.rawSCH.shape)
            print('>> Tch data set', self.rawTCH.shape)
        
        else:
            print('>> Only Codebook will be loaded')
            pass
        
        self.cb = pd.read_excel(os.path.join(self.BASE_DIR, codebook_Folder, codeBook), sheet_name='변수선택(1213)')



    def defaultCleaner(self):
        print('\n\n>>>> Cleaning: default nation and variable')


        ### dictionary by nation
        def cleaningNational(dataLS, SouthKorea = 'Korea', US='United States'):
            nationalData = {'SK': [], 'US': []}

            for nation_name, code in zip(nationalData.keys(), [SouthKorea, US]):
                print(f'\n>> slicing: {nation_name}')
                for data in dataLS:
                    # print(data.head(5))
                    temp2 = data[data['CNTRYID'] == code]
                
                    nationalData[nation_name].append(temp2)
                    print('>> sliced shape: ', temp2.shape)
            
            return nationalData
            

        def cleaningVariable(data, codeBook):
            output = {}
            
            for nation_name in data.keys():
                Column_toSave = {'Stu': [], 'Sch': [], 'Tch': []}
                for fileName, variable, category in tqdm(zip(codeBook['file name'].values, codeBook['NAME'].values, codeBook['categories']), desc=">> variable check"):
                    # 코드북 내에서도 분석에서 제할 변수는 file name을 비움
                    if type(fileName) != str:
                        continue


                    else: 
                        if category == 'identifier':
                            Column_toSave['Stu'].append(variable)
                            
                            if variable == 'CNTSTUID':
                                continue
                            else: # 코드북 구조 문제: 학교, 교사 셋에는 해당 변수가 없어서 추가해줌
                                Column_toSave['Sch'].append(variable)
                                Column_toSave['Tch'].append(variable)

                        else:
                            if 'STU' in fileName:
                                if variable in data[nation_name][0].columns:
                                    Column_toSave['Stu'].append(variable)
                                else:
                                    print('>> none(stu)', variable)

                            elif 'SCH' in fileName:
                                if variable in data[nation_name][1].columns:
                                    Column_toSave['Sch'].append(variable)
                                else:
                                    print('>> none(sch)', variable)

                            elif 'TCH' in fileName:
                                if variable in data[nation_name][2].columns:
                                    Column_toSave['Tch'].append(variable)
                                else:
                                    print('>> none(tch)', variable)
                    
                
                # print('>>>> save: ', Column_toSave)
                output[nation_name] = [data[nation_name][0][Column_toSave['Stu']],
                                        data[nation_name][1][Column_toSave['Sch']],
                                        data[nation_name][2][Column_toSave['Tch']],
                                        ]
                assert len(Column_toSave['Tch']) < 4, print(Column_toSave['Tch'])

            assert 'SK' in output.keys()
            assert 'US' in output.keys()
            return output

        cleaned_Nation = cleaningNational(dataLS = self.dataLS)
        self.default_cleaningData = cleaningVariable(data = cleaned_Nation, codeBook = self.cb)

        # categories 에서 일단은 codebook에 있는 변수가 다 있나 확인
        # categories 에서 individual & family, school 구분


if __name__ == '__main__':
    Loader = Load(stuFolder="STU", schFolder='SCH', tchFolder='TCH',
                codeBook='PISA2018_CODEBOOK (변수선택-공유).xlsx'
                )
    if args.full == True:
        Loader.defaultCleaner()
        print(Loader.default_cleaningData.keys())

        with pd.ExcelWriter(os.path.join(os.getcwd(), 'data', 'cleanedData(SK).xlsx')) as writer:
            Loader.default_cleaningData['SK'][0].to_excel(writer, sheet_name='stu', index=False)
            Loader.default_cleaningData['SK'][1].to_excel(writer, sheet_name='sch', index=False)
            Loader.default_cleaningData['SK'][2].to_excel(writer, sheet_name='tch', index=False) 


        with pd.ExcelWriter(os.path.join(os.getcwd(), 'data', 'cleanedData(US).xlsx')) as writer:
            Loader.default_cleaningData['US'][0].to_excel(writer, sheet_name='stu', index=False)
            Loader.default_cleaningData['US'][1].to_excel(writer, sheet_name='sch', index=False)
            Loader.default_cleaningData['US'][2].to_excel(writer, sheet_name='tch', index=False)