library('haven')
library('readxl')
library('dplyr')
library('randomForest') 
library('caTools')
library('caret')
library('ggplot2')


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
  
  rf <- randomForest(resilient ~.,
                     data = df_train,
                     mtry = floor(sqrt(ncol(df_train))),
                     ntree = 5000,
                     na.action = na.roughfix,
                     importance=TRUE
                     )
  
  #!# pred <- predict(object = rf, newData = df_test) # it occurs error
  pred <- predict(rf, df_test, type="class")
  print(confusionMatrix(pred, df_test$resilient)) # rs1. confusion matrix
  
  png(filename = sprintf('C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\data\\%s.png', title))
  # varImpPlot(rf, main=title, mar = c(1, 1, 1, 1)) 
  
  db.imp <- importance(rf, type=1)
  df.imp <- data.frame(db.imp)
  # print(df.imp)
  df.imp.descending <- df.imp %>% arrange(desc(MeanDecreaseAccuracy))
  df.imp.percentage <- df.imp.descending %>% mutate(Percentage=round(MeanDecreaseAccuracy/sum(MeanDecreaseAccuracy)*100,2))
  # print(df.imp.percentage)
  
  plt <- ggplot(df.imp.percentage,
                aes( x = reorder(rownames(df.imp.percentage), Percentage),
                     y = Percentage
                     )) +
                geom_col() +
                xlab("variable") +
                coord_flip() + 
                ggtitle(sprintf("Variabel Importance Plot__%s", title))
  
  print(plt)
  dev.off()
  rs <- list('model'= rf, 'df.mda'= df.imp.percentage)
  return(rs)
}

# sample test
rf.SK <- doRandomForest(dfObj$SK, title='South Korea')
rf.US <- doRandomForest(dfObj$US, title='US')

# plot err rate per tree
plot(rf.SK$model$err.rate[, 1])
plot(rf.US$model$err.rate[, 1])



#main analysis
rf_loop <- function(title, rfModel, df.mda) {
  
}




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