library('haven') 
library('randomForest') 
library('dplyr')
library('readxl')

set.seed(41) # set random seed
NA2mean <- function(x) replace(x, is.na(x), mean(x, na.rm = TRUE))


df <- read.csv('/Users/huni/Dropbox/[0]groundground/2021 random Forest/0220/DATA/Individual data_cleaningdone_v2.csv')

df_SK <- df[!(df$CNT=='Korea'),]
df_US <- df[!(df$CNT=='United State')]

df_SK <- df_SK[-c(1,2,3)] # index, ID, gender #!# to be checked
df_US <- df_US[-c(1,2,3)]



###
# Start Random Forest
####
doRandomForest <- function(inputDf, title) {
  train_idx <- sample(1:nrow(inputDf), size=0.7*nrow(inputDf), replace=F)
  test_idx <- -train_idx
  
  df_train <- inputDf[train_idx, ]
  df_test <- df_IB[test_idx, ]
  
  rf <- randomForest(resilient ~.,
                     data = df_train,
                     mtry = floor(ncol(inputDf)/3), #!# it's categorical problem
                     ntree = 1000 #!# value should be checked
  )
  rf.pred <- predict(rf, newData = df_test)
  rf.pred.train <- predict(rf, newData = df_train)
  plot(x = rf.pred, y= df_test$resilient)
  
  # cor.test #!# TBD
  varImpPlot(rf, main=title)
  importance(rf)
}

doRandomForest(df)
doRandomForest(df_SK)
doRandomForest(df_US)


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