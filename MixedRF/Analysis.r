library('haven') 
library('readxl')
library('dplyr')
library('randomForest') 
library('caTools')

set.seed(41) # set random seed
# NA2mean <- function(x) replace(x, is.na(x), mean(x, na.rm = TRUE))


###
# load and slicing data will be converted to function
###
df <- read_excel('C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\data\\preprocessing.xlsx', sheet='full')
df$resilient <- as.factor(df$resilient)
df <- subset(df, select=-c(ESCS))
summary(df)

df_SK <- df[df$CNT=='Korea', ]
df_US <- df[df$CNT=='United States', ]
df_SK <- df_SK[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID
df_US <- df_US[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID


print(dim(df_SK))
print(dim(df_US))

###
# Start Random Forest
####
doRandomForest <- function(inputDf, title) {
  inputDf[sapply(inputDf, is.character)] <- lapply(inputDf[sapply(inputDf, is.character)], 
                                               as.factor)
  df.roughfix <- na.roughfix(inputDf)
  
  sample = sample.split(inputDf$resilient, SplitRatio = .7)
  df_train = subset(df.roughfix, sample == TRUE)
  df_test  = subset(df.roughfix, sample == FALSE)
  
  
  rf <- randomForest(resilient ~., data = df_train, mtry = floor(sqrt(ncol(df_train))), ntree = 500)

  #!# pred <- predict(object = rf, newData = df_test) # it occurs error
  pred <- predict(rf, df_test, type="class")
  print(confusionMatrix(pred, df_test$resilient))
  varImpPlot(rf, main=title, mar = c(1, 1, 1, 1))
}

doRandomForest(df_SK, title='South Korea')
doRandomForest(df_US, title='US')


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