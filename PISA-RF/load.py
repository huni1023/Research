import os
import time
import pickle
import shutil
import zipfile
import numpy as np
import pandas as pd

from sys import platform
from functools import wraps
from tqdm import tqdm
from datetime import datetime



App_dir = os.getcwd()

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper

class Load:
    def __init__(self, codeBook):
        global args
        r""" Load Student, School, Teacher, Codebook data
        - put PISA 2018 data SPSS file in data folder 
        - PISA 2018 database: https://www.oecd.org/pisa/data/2018database/
        """
        if os.path.isdir(os.path.join(App_dir, 'data')) == False:
            os.mkdir(os.path.join(App_dir, 'data'))
            print('>> raw data folder is created')

        self.Data_dir = os.path.join(App_dir, 'data')

        
        codebook_Folder = 'drive-download-20220816T053902Z-001'

        print('>>>>> Init: load raw data')
        cond1 = os.path.isfile(os.path.join(self.Data_dir, "data_stu.pkl"))
        cond2 = os.path.isfile(os.path.join(self.Data_dir, "data_sch.pkl"))
        cond3 = os.path.isfile(os.path.join(self.Data_dir, "data_tch.pkl"))
        if cond1 and cond2 and cond3:
            with open(os.path.join(self.Data_dir, "data_stu.pkl"), 'rb') as f:
                self.rawStu = pickle.load(f)
            with open(os.path.join(self.Data_dir, "data_sch.pkl"), 'rb') as f:
                self.rawSCH = pickle.load(f)
            with open(os.path.join(self.Data_dir, "data_tch.pkl"), 'rb') as f:
                self.rawTCH = pickle.load(f)
        else:
            try:
                # loading takes pretty long time
                tmp_stu = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_STU_QQQ.zip'),
                                                    spss_filename="STU/CY07_MSU_STU_QQQ.sav")
                print('>> Student data set', tmp_stu.shape)
                self.rawStu = Load._clean_nation(tmp_stu, category="stu")

                tmp_sch = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_SCH_QQQ.zip'),
                                                    spss_filename="SCH/CY07_MSU_SCH_QQQ.sav")
                print('>> School data set', tmp_stu.shape)
                self.rawSCH = Load._clean_nation(tmp_sch, category="sch")

                tmp_tch = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_TCH_QQQ.zip'),
                                                    spss_filename="TCH/CY07_MSU_TCH_QQQ.sav")
                print('>> Teacher data set', tmp_stu.shape)
                self.rawTCH = Load._clean_nation(tmp_tch, category="tch")

                self.dataLS = [self.rawStu, self.rawSCH, self.rawTCH]
            except:
                raise ValueError('put PISA 2018 data SPSS file in data folder')
        

        # self.cb = pd.read_excel(os.path.join(self.Data_dir, codebook_Folder, codeBook), sheet_name='변수선택(1213)')


    @timeit
    def defaultCleaner(self):
        """cleaning required nations and variable, save result for further analysis
        """
        cleaned_Nation = Load._devide_nation(self)
        # self.default_cleaningData = Load._cleaningVariable(data = cleaned_Nation, codeBook = self.cb)
        self.default_cleaningData = Load._clean_variable(self, data = cleaned_Nation)

        # save result
        with open(os.path.join(self.Data_dir, 'cleaned.pkl'), 'wb') as f:
            pickle.dump(self.default_cleaningData, f, pickle.HIGHEST_PROTOCOL)


        # for cross check
        with pd.ExcelWriter(os.path.join(self.Data_dir, 'cleanedData(SK).xlsx')) as writer:
            self.default_cleaningData['SK'][0].to_excel(writer, sheet_name='stu', index=False)
            self.default_cleaningData['SK'][1].to_excel(writer, sheet_name='sch', index=False)
            self.default_cleaningData['SK'][2].to_excel(writer, sheet_name='tch', index=False)  

        with pd.ExcelWriter(os.path.join(self.Data_dir, 'cleanedData(US).xlsx')) as writer:
            self.default_cleaningData['US'][0].to_excel(writer, sheet_name='stu', index=False)
            self.default_cleaningData['US'][1].to_excel(writer, sheet_name='sch', index=False)
            self.default_cleaningData['US'][2].to_excel(writer, sheet_name='tch', index=False)

    @timeit
    def _load_zipfile(self, zipfile_dir: str, spss_filename: str) -> pd.DataFrame:
        r"""load spss data from zipfile"""
        assert zipfile_dir[-4:] == '.zip'
        assert spss_filename[-4:] == '.sav'
        zip_folder = zipfile.ZipFile(zipfile_dir, 'r')
        before = os.listdir(self.Data_dir)

        zip_folder.extract(spss_filename, path=self.Data_dir)
        after = os.listdir(self.Data_dir)
        difference_dir = list(set(after) - set(before))[0]

        rs = pd.read_spss(os.path.join(self.Data_dir, spss_filename))
        
        shutil.rmtree(os.path.join(self.Data_dir, difference_dir))

        return rs

    @staticmethod
    def _clean_nation(data: pd.DataFrame, category: str) -> pd.DataFrame:
        r"""in this analysis, i need only Korea and US
        - because student file is too big, save sliced dataframe temporaily in pickle file
        Parameters
        ----------
        category: str
            stu, tch, sch
        """
        if (category == 'stu') or (category == 'sch') or (category == 'tch'): pass
        else:
            raise ValueError('invalid argument, only stu, sch, tch allowed')
        
        df_kr = data[data['CNTRYID'] == 'Korea']
        df_us = data[data['CNTRYID'] == 'Korea']
        
        rs = pd.concat([df_kr, df_us], axis=0)
        
        with open(os.path.join(self.Data_dir, f'data_{category}.pkl'), 'wb') as f:
            pickle.dump(rs, f, pickle.HIGHEST_PROTOCOL)
        return rs

        
    def _devide_nation(self, SouthKorea = 'Korea', US='United States'):
        nationalData = {'SK': [], 'US': []}
        for nation_name, code in zip(nationalData.keys(), [SouthKorea, US]):
            for data in self.dataLS:
                temp2 = data[data['CNTRYID'] == code]
            
                nationalData[nation_name].append(temp2)
                print('>> sliced shape: ', temp2.shape)
            
        return nationalData

    @timeit
    def _clean_variable(self, data: dict) -> dict:
        r"""cleaning variables using codebook
        - categories 에서 individual & family, school 구분
        #!# 꼭 이 함수가 여기에 있어야할까?
        #!# 어쩌면, 코드북 따라서 정리하는건 preprocessing에서 처리해야하는게 아닐지?
        """
        rs = {}
        
        for nation_name in data.keys():
            Column_toSave = {'Stu': [], 'Sch': [], 'Tch': []}
            for fileName, variable, category in tqdm(zip(self.cb['file name'].values, self.cb['NAME'].values, self.cb['categories']), desc=">> variable check"):
                if type(fileName) != str: # 코드북 내에서도 분석에서 제할 변수는 file name을 비움
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
                
            rs[nation_name] = [data[nation_name][0][Column_toSave['Stu']],
                                    data[nation_name][1][Column_toSave['Sch']],
                                    data[nation_name][2][Column_toSave['Tch']],
                                    ]
            assert len(Column_toSave['Tch']) < 4, print(Column_toSave['Tch'])

        assert 'SK' in rs.keys()
        assert 'US' in rs.keys()
        return rs
        


def main():
    Loader = Load(codeBook='PISA2018_CODEBOOK (변수선택-공유).xlsx')
    # Loader.defaultCleaner()



if __name__ == '__main__':
    main()