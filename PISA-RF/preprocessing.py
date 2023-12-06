import os
import logging
import copy
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# visualize
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
sns.set_style("darkgrid")
plt.rcParams['axes.unicode_minus'] = False # unicode minus를 사용하지 않기 위한 설정 (minus 깨짐현상 방지)
plt.rcParams["figure.autolayout"] = True

# font
import matplotlib.font_manager as fm
font_list = [font.name for font in fm.fontManager.ttflist]
plt.rcParams['font.family'] = 'Malgun Gothic'

# logging
logger = logging.getLogger("preprocessing")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s -preprocessing- %(levelname)s:%(message)s")
handler = logging.FileHandler("event.log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


App_dir = os.getcwd()
Data_dir = os.path.join(App_dir, 'data')
Result_dir = os.path.join(App_dir, 'rs')

from load import timeit

class Preprocessing:
    def __init__(self, codebook_name):
        self.data = Preprocessing._load_data()
        self.cb = pd.read_excel(os.path.join(Data_dir, codebook_name))

        self.nation_real_name = {'SK': '대한민국', 'US': '미국'}
        self.data_1_join = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}
        self.data_2_dropNA = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}
        
        self.rs_deescriptive_Full = pd.DataFrame()
        self.rs_deescriptive_SK = pd.DataFrame()
        self.rs_deescriptive_US = pd.DataFrame()

    @timeit
    def Join_group_data(self):
        r"""
        join student, school and teacher dataframe
        """
        logger.debug(f'step1. join dataframe')

        for nationalName, inputNational in self.data.items():
            df_student = inputNational[0].copy()
            df_school = inputNational[1].copy()
            df_teacher = inputNational[2].copy()
            logger.debug(f'student data: {df_student.shape}')
            logger.debug(f'school data: {df_school.shape}')
            logger.debug(f'teacher data: {df_teacher.shape}')
            
            df_student.reset_index(drop=True, inplace=True)
            rs = copy.deepcopy(df_student)
            before = df_student.shape

            # merge school data
            if df_school.shape[1] <= Preprocessing._demographic_column_count(self):
                logger.debug('school data is empty')
            else:
                Preprocessing._match_info(data_ref=df_student, data=df_school)
            
            # merge teacher data
            if df_teacher.shape[1] <= Preprocessing._demographic_column_count(self):
                logger.debug('teacher data is empty')
            else:
                Preprocessing._match_info(data_ref=df_student, data=df_teacher)

            after = rs.shape
            logger.debug(f'Bef: {before}, Aft: {after}')
            self.data_1_join[nationalName] = rs
        return rs
    
    @timeit
    def Drop_student(self, na_threshold: int, is_visualize=False):
        r"""
        drop student who have too many NA value
        Parameters
        ----------
        na_threshold: int
            drop student who have NA value above this threshold
        """
        logger.debug(f'step2. Verify na and Drop student')
        def column_wise_NA(inputData) -> dict:
            r"""generate column-wise NA ratio"""
            if type(inputData) == dict:
                merged = pd.concat([inputData['SK'], inputData['US']])
                assert merged.shape[0] == inputData['SK'].shape[0] + inputData['US'].shape[0]
            
            elif type(inputData) == pd.DataFrame:
                merged = copy.deepcopy(inputData)
            
            else:
                raise TypeError('dictionary or pd.DataFrame is allowed')
            
            describeDF = merged.describe().T
            describeDF['NA_ratio'] = round(100 - describeDF['count']/merged.shape[0]*100, 2)

            newColumnOrder = [describeDF.columns[0], 'NA_ratio'] + list(describeDF.columns[1:-1])
            describeDF= describeDF[newColumnOrder]
            return describeDF

        # 각 학생별로 데이터 검수
        def row_wise_NA(inputData: dict, is_visualize: bool, na_threshold: int) -> dict:
            r"""calculate NA ratio per student"""
            merged = pd.concat([inputData['SK'], inputData['US']])
            assert merged.shape[0] == inputData['SK'].shape[0] + inputData['US'].shape[0]

            for_histogram = {}
            rs = {}
            for label, data in zip(['full', 'SK', 'US'], [merged, inputData['SK'], inputData['US']]):
                for_histogram[label] = []
                to_drop = []

                for i in range(len(data.index)) :
                    na_cnt = data.iloc[i].isnull().sum()
                    na_ratio = round((na_cnt/data.shape[1]) * 100, 0)
                    for_histogram[label].append(na_ratio)
                    if na_cnt > na_threshold:
                        to_drop.append(i)
                logger.debug(f'NA drop of {label}: {len(to_drop)}')
                rs[label] = data.drop(to_drop, axis=1)

            if is_visualize == True:
                fig = plt.figure(figsize=(17,6))

                plt.subplot(1, 3, 1)
                plt.hist(for_histogram['full'])
                plt.title('\n전체 데이터\n')
                plt.xlabel('\n전체 변수 대비 결측비율(%)\n')
                plt.ylabel('빈도')
                
                plt.subplot(1, 3, 2)
                plt.hist(for_histogram['SK'])
                plt.title('\nSouth Korea\n')
                plt.xlabel('\n전체 변수 대비 결측비율(%)\n')
                plt.ylabel('빈도')
                
                plt.subplot(1, 3, 3)
                plt.hist(for_histogram['US'])
                plt.title('\nUnited States\n')
                plt.xlabel('\n전체 변수 대비 결측비율(%)\n')
                plt.ylabel('빈도')

                plt.savefig(os.path.join(Data_dir, f'NA_ratio.png'))
                plt.show()


            return rs
        
        #!# 이 부분은 sequential한 단계에서 빠져야할 것 같음, EDA에 가까움
        # visualize와 같이, debug 단계만 사용되면 되고, 나머지에서는 굳이 계산할 필요가 없음
        self.rs_deescriptive_Full = column_wise_NA(self.data_1_join)
        self.rs_deescriptive_SK = column_wise_NA(self.data_1_join['SK'])
        self.rs_deescriptive_US = column_wise_NA(self.data_1_join['US'])

        clean_data_using_rowwise_NA = row_wise_NA(self.data_1_join, na_threshold=na_threshold, is_visualize=is_visualize)
        self.data_2_dropNA['SK'] = clean_data_using_rowwise_NA['SK']
        self.data_2_dropNA['US'] = clean_data_using_rowwise_NA['US']
        return self.data_2_dropNA

    @staticmethod
    def _load_data():
        with open(os.path.join(App_dir, 'data', 'cleaned.pkl'), 'rb') as f:
            loadedData = pickle.load(f)
        return loadedData
    
    @staticmethod
    def _match_info(data_ref: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        r"""match student-school info, and student-teacher info"""
        raise NotImplementedError
    
    def _demographic_column_count(self) -> int:
        r"""count demographic columns"""
        identifier_cb = self.cb[self.cb['category']=='identifier']
        return identifier_cb.shape[0]


def main():
    processor = Preprocessing(codebook_name='codebook.xlsx')
    processor.Join_group_data()
    processor.Drop_student(na_threshold=30, is_visualize=True)

    # 3, 4, 5, 6은 나중에 수행해도 무방

if __name__ == '__main__':
    main()