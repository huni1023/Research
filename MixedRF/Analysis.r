library('haven')
library('readxl')
library('dplyr')
library('randomForest') 
library('caTools')
library('caret')
library('ggplot2')


set.seed(41) # set random seed

###
# load and slicing data will be converted to function
###
Loader <- function(sheetName, PV_num) {
  if (Sys.info()['sysname'] == 'Darwin') {
    data_path <- '/Users/huni/Proj/Research/MixedRF/data/preprocessing.xlsx'  
  } else {
    # dev <- 'Proj'   # labtop
    dev <- 'Dev'# desktop
    data_path <- file.path('C:\\Users\\jhun1\\', dev, 'Research\\MixedRF\\rs', sprintf('preprocessing%s.xlsx', PV_num))
    # data_path <- file.path('C:\\Users\\jhun1\\Dev\\Research\\MixedRF\\rs', sprintf('preprocessing%s.xlsx', PV_num)) 
    
  }
  print(paste('>> PV', PV_num, 'READ variable is loaded'))
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
dfObj = Loader(sheetName = 'sliced', PV_num="10")

###
# Start Random Forest
####
doRandomForest <- function(inputDf, title, idx=0) {
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
  
  pred <- predict(rf, df_test, type="class")
  print(confusionMatrix(pred, df_test$resilient)) # rs1. confusion matrix
  
  # png(filename = sprintf('C:\\Users\\jhun1\\Proj\\Research\\MixedRF\\rs\\%s_%s.png', title, idx)) #labtop
  png(filename = file.path('C:\\Users\\jhun1\\Dev\\Research\\MixedRF\\rs', sprintf('%s_%s.png', title, idx))) # desktop
  dev.off() #after using png function, this code line is essential. if not, plot pannel will not show nothing
  
  # importance plot
  db.imp <- importance(rf, type=1)
  df.imp <- data.frame(db.imp)
  df.imp.descending <- df.imp %>% arrange(desc(MeanDecreaseAccuracy))
  df.imp.percentage <- df.imp.descending %>% mutate(Percentage=round(MeanDecreaseAccuracy/sum(MeanDecreaseAccuracy)*100,2))
  print(df.imp.percentage)
  
  plt <- ggplot(df.imp.percentage,
                aes( x = reorder(rownames(df.imp.percentage), Percentage),
                     y = Percentage
                )) +
    geom_col() +
    xlab("variable") +
    coord_flip() + 
    ggtitle(sprintf("Variabel Importance Plot__%s__PV%sREAD", title, idx))
  
  print(plt)
  # varImpPlot(rf, main=title, mar = c(1, 1, 1, 1))
  
  
  rs <- list('model'= rf, 'df.mda'= df.imp.percentage) 
  return(rs) # data return as list, first element: randomForest model, seconde element: cleaned dataFrame
}

"
sample test
- run RF and plot

"
rf.SK <- doRandomForest(dfObj$SK, title='South Korea')
rf.US <- doRandomForest(dfObj$US, title='US')

plot(rf.US$model$err.rate[, 1])
varImpPlot(rf.SK$model,
           sort = T,
           n.var = 10,
           main = "Top 10 - Variable Importance")


"
main analysis1
- iterate same data 5 times
- RF result comparison file
"
rf_loop <- function(data, title) {
  for (x in 1:5) {
    doRandomForest(inputDf= data, title=title, idx=x)
  }
}

rf_loop(dfObj$SK, title='South Korea')
rf_loop(dfObj$US, title='United States')


"
main analysis2
- iterate 10 different data
- RF result comparison_v2 file
"
rf_loop2 <- function() {
  for (x in 1:10) {
    dfObj = Loader(sheetName = 'sliced', PV_num=as.character(x))
    doRandomForest(inputDf= dfObj$SK, title="South Korea", idx=x)
    # doRandomForest(inputDf= dfObj$US, title="United States", idx=x)
  }
}
rf_loop2()


"
#!# 23.08.23
history를 몰라서 사용하기 어려울듯듯
"
library(pdp)
# # get top 10 variable
# top10.SK <- topPredictors(rf.SK, n = 10)
# top10.US <- topPredictors(rf.US, n = 10)

# drawing pdp like subplot
# # Construct partial dependence functions for top four predictors
# pd <- NULL
# for (i in top4) {
#   tmp <- partial(mtcars.rf, pred.var = i)
#   names(tmp) <- c("x", "y")
#   pd <- rbind(pd, cbind(tmp, predictor = i))
# }

# Display partial dependence functions
ggplot(pd, aes(x, y)) +
  geom_line() +
  facet_wrap(~ predictor, scales = "free") +
  theme_bw() +
  ylab("mpg")