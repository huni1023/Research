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
Loader <- function(sheetName) {
  if (Sys.info()['sysname'] == 'Darwin') {
    data_path <- '/Users/huni/Proj/Research/MixedRF/data/preprocessing.xlsx'  
  } else {
    data_path <- 'C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\data\\preprocessing.xlsx'
  }
  
  df <- read_excel(data_path, sheet=sheetName)
  df$resilient <- as.factor(df$resilient)
  df <- subset(df, select=-c(ESCS))
  summary(df)
  
  df_SK <- df[df$CNT=='Korea', ]
  df_US <- df[df$CNT=='United States', ]
  df_SK <- df_SK[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID
  df_US <- df_US[-c(1,2,3)] # CNT, CNTSCHID, CNTSTUID
  result <- list('SK' = df_SK, 'US'= df_US)
  return(result)
}

# dfObj = Loader(sheetName = 'full')
dfObj = Loader(sheetName = 'sliced')

###
# Start Random Forest
####
doRandomForest <- function(inputDf, title) {
  inputDf[sapply(inputDf, is.character)] <- lapply(inputDf[sapply(inputDf, is.character)], 
                                               as.factor)
  df.roughfix <- na.roughfix(inputDf)
  
  sample = sample.split(df.roughfix$resilient, SplitRatio = 0.7)
  df_train = subset(df.roughfix, sample == TRUE)
  df_test  = subset(df.roughfix, sample == FALSE)
  # sample = sample.split(inputDf$resilient, SplitRatio = 0.7)
  # df_train = subset(inputDf, sample == TRUE)
  # df_test  = subset(inputDf, sample == FALSE)
  
  rf <- randomForest(resilient ~.,
                     data = df_train,
                     mtry = floor(sqrt(ncol(df_train))),
                     ntree = 10000,
                     na.action = na.roughfix,
                     importance=TRUE
                     )
  # rf <- randomForest(resilient ~.,
  #                    data = df_train,
  #                    mtry = floor(sqrt(ncol(df_train))),
  #                    ntree = 5000,
  #                    na.action = na.roughfix,
  #                    importance=FALSE,
  #                    nodesize = 5
  #                    )

  #!# pred <- predict(object = rf, newData = df_test) # it occurs error
  pred <- predict(rf, df_test, type="class")
  print(confusionMatrix(pred, df_test$resilient))
  varImpPlot(rf, main=title, mar = c(1, 1, 1, 1))
  return(rf)
}

rf.SK <- doRandomForest(dfObj$SK, title='South Korea')
rf.US <- doRandomForest(dfObj$US, title='US')

# plot err rate per tree
plot(rf.SK$err.rate[, 1])
plot(rf.US$err.rate[, 1])

library(pdp)
# get top 10 variable
top10.SK <- topPredictors(rf.SK, n = 10)
top10.US <- topPredictors(rf.US, n = 10)

# drawing pdp like subplot
# Construct partial dependence functions for top four predictors
pd <- NULL
for (i in top4) {
  tmp <- partial(mtcars.rf, pred.var = i)
  names(tmp) <- c("x", "y")
  pd <- rbind(pd, cbind(tmp, predictor = i))
}
# Display partial dependence functions
ggplot(pd, aes(x, y)) +
  geom_line() +
  facet_wrap(~ predictor, scales = "free") +
  theme_bw() +
  ylab("mpg")

# partial(rf_IB, pred.var='L2Y6C0804', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S0401', plot=TRUE)
# partial(rf_IB, pred.var='L2Y6S2702', plot=TRUE)