import os
import logging
import copy
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
logger = logging.getLogger("eda")
formatter = logging.Formatter("%(asctime)s %(levelname)s:%(message)s")
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

class exploratory_data_analysis(Preprocessing):
    def __init__(self):
        super().__init__()
        pass

def main():
    pass

if __name__ == '__main__':
    main()