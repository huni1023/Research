import os
import time
import logging
import pickle
import shutil
import zipfile
import numpy as np
import pandas as pd

from sys import platform
from functools import wraps
from tqdm import tqdm
from datetime import datetime

# logging
logger = logging.getLogger("load")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
handler = logging.FileHandler("event.log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


App_dir = os.getcwd()

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} Took: {total_time:.4f} seconds')
        return result
    return timeit_wrapper

class Load:
    def __init__(self, codeBook):
        r""" Load Student, School, Teacher, Codebook data
        - put PISA 2018 data SPSS file in data folder (stduent, schoo, teacher)
        - PISA 2018 database: https://www.oecd.org/pisa/data/2018database/
        """
        if os.path.isdir(os.path.join(App_dir, 'data')) == False:
            os.mkdir(os.path.join(App_dir, 'data'))
            logger.debug('raw data folder is created')

        self.Data_dir = os.path.join(App_dir, 'data')

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
        logger.debug('load raw data')
        cond1 = os.path.isfile(os.path.join(self.Data_dir, "data_stu.pkl"))
        cond2 = os.path.isfile(os.path.join(self.Data_dir, "data_sch.pkl"))
        cond3 = os.path.isfile(os.path.join(self.Data_dir, "data_tch.pkl"))
        if cond1 and cond2 and cond3:
            with open(os.path.join(self.Data_dir, "data_stu.pkl"), 'rb') as f:
                self.rawStu = pd.read_pickle(f)
            with open(os.path.join(self.Data_dir, "data_sch.pkl"), 'rb') as f:
                self.rawSCH = pd.read_pickle(f)
            with open(os.path.join(self.Data_dir, "data_tch.pkl"), 'rb') as f:
                self.rawTCH = pd.read_pickle(f)
        else:
            try:
                tmp_stu = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_STU_QQQ.zip'),
                                                    spss_filename="STU/CY07_MSU_STU_QQQ.sav") # loading student takes pretty long time
                logger.debug(f'Student data set: {tmp_stu.shape}')
                self.rawStu = Load._clean_nation(self, tmp_stu, category="stu")

                tmp_sch = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_SCH_QQQ.zip'),
                                                    spss_filename="SCH/CY07_MSU_SCH_QQQ.sav")
                logger.debug(f'School data set: {tmp_stu.shape}')
                self.rawSCH = Load._clean_nation(self, tmp_sch, category="sch")

                tmp_tch = Load._load_zipfile(self, zipfile_dir=os.path.join(self.Data_dir, 'SPSS_TCH_QQQ.zip'),
                                                    spss_filename="TCH/CY07_MSU_TCH_QQQ.sav")
                logger.debug(f'Teacher data set: {tmp_stu.shape}')
                self.rawTCH = Load._clean_nation(self, tmp_tch, category="tch")

            except:
                raise ValueError('put PISA 2018 data SPSS file in data folder')
        
        self.dataLS = [self.rawStu, self.rawSCH, self.rawTCH]
        self.cb = pd.read_excel(os.path.join(self.Data_dir, codeBook))


    @timeit
    def defaultCleaner(self):
        """cleaning required nations and variable, save result for further analysis
        """
        cleaned_nation = Load._devide_nation(self) # 국가먼저 작업해줘야함, 뒤에서 코드북에 없는 데이터는 날리기 때문임
        cleaned_variable = Load._clean_variable(self, data = cleaned_nation)
        self.default_cleaningData = Load._validate_column(self, data = cleaned_variable)

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

    def _clean_nation(self, data: pd.DataFrame, category: str) -> pd.DataFrame:
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
        df_us = data[data['CNTRYID'] == 'United States']
        
        rs = pd.concat([df_kr, df_us], axis=0)
        
        with open(os.path.join(self.Data_dir, f'data_{category}.pkl'), 'wb') as f:
            pickle.dump(rs, f, pickle.HIGHEST_PROTOCOL)
        return rs

    def _devide_nation(self) -> dict:
        nationalData = {'SK': [], 'US': []}
        for data in self.dataLS:
            for nation_name, nation_code in zip(nationalData.keys(), ['Korea', 'United States']):
                logger.debug(f'*nation: {nation_name}, { nation_code}')
                temp2 = data[data['CNTRYID'] ==  nation_code].copy()
                nationalData[nation_name].append(temp2)
                logger.debug(f'sliced shape: {temp2.shape}')
            
        return nationalData
    
    def _clean_variable(self, data: dict):
        r"""left only necessary variable
        #!# at the beginning of the research you cannot sure which variable will be used, 
        #!# so codebook is vulunerable ~~~~~ this stage is iterable,
        """
        rs = dict()
        for nation, data_ls in data.items():
            rs[nation] = []
            for data in data_ls:
                col_ls = [col for col in data.columns if col in self.cb['variable_code'].values]
                rs[nation].append(data[col_ls])
        return rs
    
    def _validate_column(self, data: dict) -> dict:
        r"""check validity of each column,
        cross check column na ratio
        """
        warning_cnt = 0
        
        for idx in range(len('student school teacher'.split())):
            invalid_col = {'SK': [], 'US': []}
            for nation in 'SK US'.split():
                threshold = data[nation][idx].shape[0] * 0.8
                for col in data[nation][idx].columns:
                    na_count = data[nation][idx][col].isna().sum()
                    if na_count > threshold:
                        invalid_col[nation].append(col)
            diff_SK_US = set(invalid_col['SK']) - set(invalid_col['US'])
            diff_US_SK = set(invalid_col['US']) - set(invalid_col['SK'])
            logger.debug(f"difference set: SK - US, {diff_SK_US}")
            logger.debug(f"difference set: US - SK, {diff_US_SK}")
            if (len(diff_US_SK) == 0) and (len(diff_SK_US) == 0):
                pass
            else:
                warning_cnt += 1
                logger.warn(f'check your codebook, some column has too many NA value, {diff_SK_US}, {diff_US_SK}')
        
        if warning_cnt == 0:
            return data
        else:
            raise ValueError('your codebook have invalid features, data count is invalid btw two country')
            



def main():
    Loader = Load(codeBook='codebook.xlsx')
    Loader.defaultCleaner()



if __name__ == '__main__':
    main()