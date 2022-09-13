library('haven') 
library('readxl')
library('dplyr')
library('randomForest') 


set.seed(41) # set random seed
# NA2mean <- function(x) replace(x, is.na(x), mean(x, na.rm = TRUE))


###
# load and slicing data will be converted to function
###
df <- read_excel('C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\data\\preprocessing.xlsx', sheet='full')
df$resilient <- as.factor(df$resilient)

df_SK <- df[df$CNT=='Korea', ]
df_US <- df[df$CNT=='United States', ]

df_SK <- df_SK[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID
df_US <- df_US[-c(1,2,3)]

print(dim(df_SK))
print(dim(df_US))

###
# Start Random Forest
####
doRandomForest <- function(inputDf, title) {
  inputDf[sapply(inputDf, is.character)] <- lapply(inputDf[sapply(inputDf, is.character)], 
                                               as.factor)
  df.roughfix <- na.roughfix(inputDf)
  
  train_idx <- sample(1:nrow(df.roughfix), size=0.7*nrow(df.roughfix), replace=F)
  
  df_train <- df.roughfix[train_idx, ]
  df_test <- df.roughfix[-train_idx, ]
  print(dim(df_test))
  
  rf <- randomForest(resilient ~., data = df_train, mtry = floor(sqrt(ncol(df_train))), ntree = 10)
                     # do.trace = TRUE # if set True, console window get dirty

  pred <- predict(object = rf, newData = df_test, type='class', se=T)
  print(length(pred))
  # print(pred)
  plot(x = pred, y= df_test$resilient)

  rf.pred.train <- predict(object= rf, newData = df_train)
  
  # cor.test #!# TBD
  # varImpPlot(rf, main=title)
  # importance(rf)
}

# doRandomForest(df, title='full data')
# str(df_SK)
doRandomForest(df_SK, title='south korea')
doRandomForest(df_US, title='us')


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