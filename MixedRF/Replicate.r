library('haven')
library('readxl')
library('dplyr')
library('randomForest') 
library('caTools')
library('caret')


set.seed(41) # set random seed
# NA2mean <- function(x) replace(x, is.na(x), mean(x, na.rm = TRUE))


###
# load and slicing data will be converted to function
###
Loader <- function() {
  if (Sys.info()['sysname'] == 'Darwin') {
    data_path <- '/Users/huni/Proj/Research/MixedRF/data/imputed_HK_c.xlsx'  
  } else {
    data_path <- 'C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\data\\imputed_HK_c.xlsx'
  }
  
  df <- read_excel(data_path)
  df$resilient <- as.factor(df$resilient)
  df <- subset(df, select=-c(ESCS))
  summary(df)
  
  # df <- df_SK[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID
  result <- list('HK' = df)
  return(result)
}

dfObj = Loader()


###
# Start Random Forest
####
doRandomForest <- function(inputDf, title) {
  inputDf[sapply(inputDf, is.character)] <- lapply(inputDf[sapply(inputDf, is.character)], 
                                               as.factor)
  df.roughfix <- na.roughfix(inputDf)
  # print(summary(df.roughfix))
  
  sample = sample.split(df.roughfix$resilient, SplitRatio = 0.7)
  df_train = subset(df.roughfix, sample == TRUE)
  df_test  = subset(df.roughfix, sample == FALSE)
  
  
  rf <- randomForest(resilient ~., data = df_train, mtry = floor(sqrt(ncol(df_train))), ntree = 500)

  #!# pred <- predict(object = rf, newData = df_test) # it occurs error
  pred <- predict(rf, df_test, type="class")
  print(confusionMatrix(pred, df_test$resilient))
  varImpPlot(rf, main=title, mar = c(1, 1, 1, 1))
}

doRandomForest(dfObj$HK, title='Hong Kong')

# library(pdp)
# partial(rf_IB, pred.var='L2Y6C0804', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S0401', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S2702', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6C1401', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S2704', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6C0212', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6C1404', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6C1403', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6C0810', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S0408', plot=TRUE)
# 
# 
# partial(rf_IG, pred.var='L2Y6S0401', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6S2704', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6C0809', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6S0407', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6C1401', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6S0412', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6S0408', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6C0211', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6C0810', plot=TRUE)
# partial(rf_IG, pred.var='L2Y6C0212', plot=TRUE)