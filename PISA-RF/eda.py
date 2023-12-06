import os
import logging
import copy
import pandas as pd
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
logger = logging.getLogger("eda")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s -EDA- %(levelname)s:%(message)s")
handler = logging.FileHandler("event.log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

# directory
App_dir = os.getcwd()
Data_dir = os.path.join(App_dir, 'data')
Result_dir = os.path.join(App_dir, 'rs')

#
from preprocessing import Preprocessing
from load import timeit

class EDA(Preprocessing):
    def __init__(self, codebook_name, PV_var):
        super().__init__(codebook_name=codebook_name)
        self.PV_var = PV_var
        self.data_3_ESCS = {'full': {'SK': pd.DataFrame(), 'US': pd.DataFrame()},
                            'sliced': {'SK': pd.DataFrame(), 'US': pd.DataFrame()}}
        self.data_final = {'full': {'SK': pd.DataFrame(), 'US': pd.DataFrame()},
                        'sliced': {'SK': pd.DataFrame(), 'US': pd.DataFrame()}}
                        

    @timeit
    def slice_by_ESCS(self, acad_threshold: int, is_visualize=False) -> dict:
        r"""
        calculate ESCS variable and devide dataset by full and sliced
        
        Parameters
        ----------
        acad_threshold: int
            academic score thrshold
        """
        logger.debug('step3. slice data by ESCS')

        def visualize(data: dict, option: str, threshold_info: dict,
                    figName: str):
            r"""visualize threshold and ratio of sample distribution
            option: str
                full or sliced
            figName: str
                title of figure
            """
            fig = plt.figure(figsize=(17,9))
            for IDX, (nationalName, inputNational) in enumerate(data.items()):

                plt.subplot(2, 2, 2*IDX+1)
                plt.hist(inputNational['AcademicScore'])
                plt.title(f'\n학업성취{self.nation_real_name[nationalName]}\n')
                plt.xlabel('\n점수\n')
                plt.axvline(threshold_info[nationalName]['academic_score'], color='r', linewidth=1, linestyle='--')
                
                plt.subplot(2, 2, 2*IDX+2)
                plt.hist(inputNational['ESCS'])
                plt.title(f'\n사회문화경제{self.nation_real_name[nationalName]}\n')
                plt.xlabel('\n점수\n')
                if option=='full':
                    plt.axvline(threshold_info[nationalName]['escs_score'], color='r', linewidth=1, linestyle='--')

                
            plt.savefig(os.path.join(Result_dir, f'{figName}_{option}.png'))
            plt.show()
        
        ## 1. calculate threshold value
        threshold_info, data_appended = EDA.thresholdCalculator(self.data_2_dropNA,
                                                            PV_var = self.PV_var,
                                                            acad_threshold = acad_threshold) ##!#!## 학업성취 코딩 방법을 바꿀 때 여기 arg를 조정
        
        
        ## 2. slice
        self.data_3_ESCS['full'] = copy.copy(data_appended) # no drop case, so just copied
        self.data_3_ESCS['sliced'] = EDA.slice_data_by_escs(data_appended, escsThreshold = threshold_info)
        assert type(self.data_3_ESCS['full']) == dict, print(self.data_3_ESCS['full'])


        ## 3. labeling resilient student
        self.data_3_ESCS['full'] = EDA.labeling_resilient(data = self.data_3_ESCS['full'], 
                                                option = 'full',
                                                threshold_info = threshold_info)
        self.data_3_ESCS['sliced'] = EDA.labeling_resilient(data = self.data_3_ESCS['sliced'], 
                                                option = 'sliced',
                                                threshold_info = threshold_info)
        

        ## 4. visualize resilient student
        if is_visualize == True:
            #!# 앞선 visualize 단계와 마찬가지임, debug단계가 아니면 확인하지 않는 부분임
            resilientCount_Ratio_full = EDA.table_resilient_ratio(data=self.data_3_ESCS['full'])
            resilientCount_Ratio = EDA.table_resilient_ratio(data=self.data_3_ESCS['sliced'])
        
            visualize(self.data_3_ESCS['full'], option='full', figName='읽10', threshold_info= threshold_info)
            visualize(self.data_3_ESCS['sliced'], option = 'sliced', figName ='읽10(target paper)', threshold_info= threshold_info)
        
            logger.debug(f"학업탄력성 보유학생수(full): {resilientCount_Ratio_full}")
            logger.debug(f'학업탄력성 보유학생수(sliced): {resilientCount_Ratio}')
            return resilientCount_Ratio
        return None
    
    @timeit
    def AdjustMinor(self):
        r"""for adjust miscellaneous things
        - merge two country dataframe
        - drop PV value (not predictor)
        - reorder column
        """
        logger.debug('ste4. adjust miscellanous thing, like column order, drop unnecessary column')
        def merge_country(inputData: dict) -> pd.DataFrame:
            output = pd.concat([inputData['SK'], inputData['US']], axis=0)
            assert inputData['SK'].shape[0] + inputData['US'].shape[0] == output.shape[0]
            return output
        
        def drop_useless_column(inputData: pd.DataFrame) -> pd.DataFrame:
            dropAcademic = ['CNTRYID', 'AcademicScore']
            for column in inputData.columns:
                if 'PV' in column:
                    dropAcademic.append(column)

            return inputData.drop(dropAcademic, axis=1)
            

        def columnOrder(inputData: pd.DataFrame,
                        important_columns=['resilient']) -> pd.DataFrame:
            r"""spss 편하도록, 주요 변수들을 앞으로 빼는 작업"""
            column_ID = ['CNT', 'CNTSCHID', 'CNTSTUID']
            inputData.set_index(column_ID+important_columns, inplace=True)
            inputData.reset_index(inplace=True)

            return inputData

        tmp_full = merge_country(self.data_3_ESCS['full'])
        tmp_sliced = merge_country(self.data_3_ESCS['sliced'])
        
        tmp2_full = drop_useless_column(tmp_full)
        tmp2_sliced = drop_useless_column(tmp_sliced)

        self.data_final['full'] = columnOrder(tmp2_full)
        self.data_final['sliced'] = columnOrder(tmp2_sliced)
        return self.data_final

    @staticmethod
    def thresholdCalculator(data: dict,
                            PV_var: int,
                            acad_threshold: int):
        r"""calculate 2 kinds of threshold, and append mean column in data
        """
        assert type(PV_var) == int, 'insert valid PV_var type'
        assert type(acad_threshold) == int, 'insert valid threshold type'
        assert (PV_var > 0) and (PV_var < 11), print('>> Error__PV_var: ', PV_var)

        threshold_dict = {'SK': {'academic_score': acad_threshold}, 'US': {'academic_score': acad_threshold}}
        targetColumn = ['PV'+ str(PV_var) + 'READ']
        rs = data.copy()

        for nationalName, inputNational in data.items():
            rs[nationalName]['AcademicScore'] = inputNational.loc[:, targetColumn].mean(axis=1)
            inputNational = inputNational.astype({'ESCS': "float64"})
            threshold_dict[nationalName]['escs_score'] = inputNational['ESCS'].quantile(0.25)

        return threshold_dict, rs
    
    @staticmethod
    def slice_data_by_escs(data: dict, escsThreshold: dict) -> dict:
        r"""slice data by escs score
        """
        assert type(data) == dict, 'insert valid data'
        assert type(escsThreshold) == dict, 'insert valid threshold'

        rs = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}
        for nationalName, inputNational in data.items():
            before = inputNational.shape[0]
            toDrop = []
            for idx, val in zip(inputNational['ESCS'].index, inputNational['ESCS'].values):
                if val < escsThreshold[nationalName]['escs_score']:
                    continue
                else:
                    toDrop.append(idx)
            
            rs[nationalName] = inputNational.drop(toDrop, axis=0)
            after = rs[nationalName].shape[0]
            logger.debug(f'>> before: {before} >> after: {after}' )
        
        return rs
    
    @staticmethod
    def labeling_resilient( 
                        data, # 전체 Full, escs 하위 25%로 데이터셋이 2개로 나뉘므로 인풋을 줘야함
                        option: str, # full: 전체 데이터, sliced: 잘린 데이터
                        threshold_info: dict
                        ):
        r"""
        Parameters
        ----------
        option: str
            full or sliced

        if condition1: using academic score
            & condition2: using escs score
            full: condition1 & condition2
            sliced: condition1
            - since sliced data already sliced by escs score
        """
        if (option == 'full') or (option == 'sliced'): pass
        else:
            raise ValueError('input valid option args')
            
        assert type(threshold_info) == dict
        rs = {'SK': pd.DataFrame(), 'US': pd.DataFrame()}
        
        
        for nationalName, inputNational in data.items():
            threshold_acad = threshold_info[nationalName]['academic_score']
            threshold_escs = threshold_info[nationalName]['escs_score']
            
            iamResilient = []
            for idx in inputNational.index:
                val_acad = inputNational.loc[idx, 'AcademicScore']
                val_escs = inputNational.loc[idx, 'ESCS']
                if option == 'full':
                    if (val_acad > threshold_acad) and (val_escs < threshold_escs):
                        iamResilient.append(1)
                    else: iamResilient.append(0)
                elif option == 'sliced': #!# 여기서 에러 날수도..?
                    if val_acad > threshold_acad:
                        iamResilient.append(1)
                    else: iamResilient.append(0)

            inputNational['resilient'] = iamResilient
            rs[nationalName] = inputNational.copy()

        return rs
    
    @staticmethod
    def table_resilient_ratio(data: dict) -> list:
        r"""회복탄력성을 지닌 학생의 전체 대비 비율을 계산함"""
        count_ratio = {'SK': [], 'US': []} #!# count, ratio로 dict형태인게 더 나아보임
        for nationalName in count_ratio.keys():
            total = data[nationalName].shape[0]
            is_resilient = data[nationalName]['resilient'].values

            resilientCount = [x for x in is_resilient if x == 1]
            resilientRatio = round(len(resilientCount)/total * 100, 2)
            count_ratio[nationalName].append(len(resilientCount))
            count_ratio[nationalName].append(resilientRatio)
            print(f'>> 회복탄력성 보유 학생수({nationalName}): ', len(resilientCount), f'({resilientRatio})%')
        return count_ratio

    
    def save_result(self):
        r"""save attributes"""
        save_dir = os.path.join(App_dir, 'result')
        if os.path.isdir(save_dir) == False:
            os.mkdir(save_dir)
        with pd.ExcelWriter(os.path.join(save_dir, "preprocessing.xlsx")) as writer:
            self.data_final['full'].to_excel(writer, sheet_name = "full", index=False)
            self.data_final['sliced'].to_excel(writer, sheet_name = "sliced", index=False)

def main():
    eda = EDA(codebook_name='codebook.xlsx', PV_var=10)
    eda.Join_group_data()
    eda.Drop_student(na_threshold=30)
    eda.slice_by_ESCS(acad_threshold=480)
    eda.AdjustMinor()
    eda.save_result()

if __name__ == '__main__':
    main()