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
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
handler = logging.FileHandler("event.log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)


App_dir = os.getcwd()
Data_dir = os.path.join(App_dir, 'data')
Result_dir = os.path.join(App_dir, 'rs')


class Preprocessing:
    def __init__(self, codebook_name, PV_var):
        self.data = Preprocessing._load_data()
        self.cb = pd.read_excel(os.path.join(Data_dir, codebook_name))
        self.PV_var = PV_var

        self.nation_real_name = {'SK': '대한민국', 'US': '미국'}
        self.valid_data = {'SK': list(), 'US': list()}
        self._2_joined = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}
        self._3_dropNa = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}

        # self._4_ESCS = {'full': {'SK': pd.DataFrame(), 'US': pd.DataFrame()},
        #                 'sliced': {'SK': pd.DataFrame(), 'US': pd.DataFrame()}}
        # self._5_shouldBeCal = {'full': {'SK': pd.DataFrame(), 'US': pd.DataFrame()},
        #                        'sliced': {'SK': pd.DataFrame(), 'US': pd.DataFrame()}}
        # self.finalRS = {'full': {'SK': pd.DataFrame(), 'US': pd.DataFrame()},
        #                 'sliced': {'SK': pd.DataFrame(), 'US': pd.DataFrame()}}
        
        self.rs_deescriptive_Full = pd.DataFrame()
        self.rs_deescriptive_SK = pd.DataFrame()
        self.rs_deescriptive_US = pd.DataFrame()

    def Drop_empty_column(self):
        r"""
        - drop feature, if it has too many NA (over 80%) 
        """
        toDrop = {}
        
        for nationName, nationalData in self.data.items():
            toDrop[nationName] = []
            for idx, (label, inputDf) in enumerate(zip('stu sch tch'.split(), nationalData)):
                if label == 'tch': #!# 굳이 tch을 살펴보지 않은 이유는?
                    pass
                else:
                    for column in inputDf.columns:
                        if inputDf[column].isna().sum() > (inputDf.shape[0] * 0.8):
                            print('>>> too much NA: ', column)
                            toDrop[nationName].append(column)
                            continue
                        
                        elif 'missing' in inputDf[column].values:
                            print('>>> missing: ', column)
                            toDrop[nationName].append(column)
                            continue
                        
                        else:
                            continue

            for nation, grouped_data in self.data.items():
                self.valid_data[nation] = []
                for idx, each_group_data in enumerate(grouped_data):
                    if idx == 0 : # in case of 'student'
                        #!# 코드북고 함께 확인필요, 굳이 RESPECT열을 떨군 이유가?
                        self.valid_data[nation].append(each_group_data.drop('PERSPECT', axis=1))
                    else: 
                        self.valid_data[nation].append(each_group_data)
                        
        return toDrop


    def Join_group_data(self):
        r"""
        join student and school dataframe
        #!# 교사데이터는 어디서 합치는가
        """
        print('\n\n>>>> 2. Join DataFrame')

        for nationalName, inputNational in self.valid_data.items():
            # print('>> join nation: ', nationalName)
            df_student = inputNational[0].copy()
            df_school = inputNational[1].copy()
            
            df_student.reset_index(drop=True, inplace=True)
            
            rs = copy.deepcopy(df_student)
            before = df_student.shape


            df_school.drop(['CNTRYID', 'CNT'], axis=1, inplace=True)
            if df_school.index.name != 'CNTSCHID':
                df_school.set_index('CNTSCHID', drop=True, inplace=True)
            
            if df_school.shape[1] == 0:
                print('>> school data is empty')
                pass
            else:
                for idx in tqdm(df_student.index, desc=">> mapping"):
                    toBeInput = df_school.loc[idx, 'CNTSCHID'].values # 학생 데이터에 들어가야할 학교 데이터 찾기
                    assert len(toBeInput) == df_school.shape[1]
                    
                    toBeInput_T = toBeInput.reshape(1, 8)
                    rs.loc[idx, list(df_school.columns)] = toBeInput_T[0]
            
                after = rs.shape
                print('>>>> Bef: ', before, '....', 'Aft: ', after)
                assert 'EDUSHORT' in rs.columns #!# 왜 필요할까

            self._2_joined[nationalName] = rs
        return rs
    
    def Drop_student(self, na_threshold: int, is_visualize=True):
        r"""
        drop student who have too many NA value
        Parameters
        ----------
        na_threshold: int
            drop student who have NA value above this threshold
        """
        print('\n>>>> 3. Verify na and Drop student')
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
                print(f'>> NA drop of {label}: ', len(to_drop))
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
        self.rs_deescriptive_Full = column_wise_NA(self._2_joined)
        self.rs_deescriptive_SK = column_wise_NA(self._2_joined['SK'])
        self.rs_deescriptive_US = column_wise_NA(self._2_joined['US'])

        clean_data_using_rowwise_NA = row_wise_NA(self._2_joined, na_threshold=na_threshold, is_visualize=is_visualize)
        self._3_dropNa['SK'] = clean_data_using_rowwise_NA['SK']
        self._3_dropNa['US'] = clean_data_using_rowwise_NA['US']
        return self._3_dropNa

    @staticmethod
    def _load_data():
        with open(os.path.join(App_dir, 'data', 'cleaned.pkl'), 'rb') as f:
            loadedData = pickle.load(f)
        return loadedData


def main():
    processor = Preprocessing(codebook_name='',
                  PV_var=10)
    processor.Drop_empty_column()
    processor.Join_group_data()
    processor.Drop_student(na_threshold=30, is_visualize=True)

    # 3, 4, 5, 6은 나중에 수행해도 무방

if __name__ == '__main__':
    main()