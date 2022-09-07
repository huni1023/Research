library('haven') 
library('randomForest') 
library('dplyr')
library('readxl')
library('mice')

set.seed(41) # set random seed
NA2mean <- function(x) replace(x, is.na(x), mean(x, na.rm = TRUE))


df_raw <- read.csv('/Users/huni/Dropbox/[0]groundground/2021 random Forest/0220/DATA/Individual data_cleaningdone_v2.csv')
head(df_raw)

df_raw_IB <- df_raw[!(df_raw$L2GENDER==2),] # for boy
df_raw_IG <- df_raw[!(df_raw$L2GENDER==1),] # for girl

df_raw_IB <- df_raw_IB[-c(1,2,3)] # index, ID, gender
df_raw_IG <- df_raw_IG[-c(1,2,3)]

df_IB <- df_raw_IB
sum(is.na(df_IB))

df_IG <- df_raw_IG
sum(is.na(df_IG))


train_idx_IB <- sample(1:nrow(df_IB), size=0.7*nrow(df_IB), replace=F)
test_idx_IB <- -train_idx_IB
df_train_IB <- df_IB[train_idx_IB, ]
df_test_IB <- df_IB[test_idx_IB, ]

rf_IB <- randomForest(p_COMMUNITY_COM ~., 
                        data=df_train_IB, 
                        mtry=floor(ncol(df_IB)/3), 
                        ntree=10000, 
                        importance=TRUE, 
                        do.trace=1000)
rf_IB.pred <- predict(rf_IB, newdata = df_test_IB)
rf_IB.pred.train <- predict(rf_IB, newdata = df_train_IB)
plot(x=rf_IB.pred , y=df_test_IB$p_COMMUNITY_COM)
rf_IB.EM <- mean(rf_IB.pred - df_test_IB$p_COMMUNITY_COM)
rf_IB.EM.train <- mean(rf_IB.pred.train - df_train_IB$p_COMMUNITY_COM)
cor.test(rf_IB.pred, df_test_IB$p_COMMUNITY_COM)
cor.test(rf_IB.pred.train, df_train_IB$p_COMMUNITY_COM)
# png('/Users/huni/Dropbox/[0]groundground/2021 random Forest/IB.png')
varImpPlot(rf_IB, main='Individual BOY')
# dev.off()
importance(rf_IB)





train_idx_IG <- sample(1:nrow(df_IG), size=0.7*nrow(df_IG), replace=F)
test_idx_IG <- -train_idx_IG
df_train_IG <- df_IG[train_idx_IG, ]
df_test_IG <- df_IG[test_idx_IG, ]
rf_IG <- randomForest(p_COMMUNITY_COM ~., data=df_train_IG, mtry=floor(ncol(df_IG)/3), ntree=10000, importance=TRUE, do.trace=1000)
rf_IG.pred <- predict(rf_IG, newdata = df_test_IG)
rf_IG.pred.train <- predict(rf_IG, newdata = df_train_IG)
plot(x=rf_IG.pred , y=df_test_IG$p_COMMUNITY_COM)
rf_IG.EM <- mean(rf_IG.pred - df_test_IG$p_COMMUNITY_COM)
rf_IG.EM.train <- mean(rf_IG.pred.train - df_train_IG$p_COMMUNITY_COM)
cor.test(rf_IG.pred, df_test_IG$p_COMMUNITY_COM)
cor.test(rf_IG.pred.train, df_train_IG$p_COMMUNITY_COM)
# png('/Users/huni/Dropbox/[0]groundground/2021 random Forest/IG.png')
varImpPlot(rf_IG, main='Individual GIRL')
# dev.off()
importance(rf_IG)


library(pdp)
partial(rf_IB, pred.var='L2Y6C0804', plot=TRUE)
partial(rf_IB, pred.var='L2Y6S0401', plot=TRUE)
partial(rf_IB, pred.var='L2Y6S2702', plot=TRUE)
partial(rf_IB, pred.var='L2Y6C1401', plot=TRUE)
partial(rf_IB, pred.var='L2Y6S2704', plot=TRUE)
partial(rf_IB, pred.var='L2Y6C0212', plot=TRUE)
partial(rf_IB, pred.var='L2Y6C1404', plot=TRUE)
partial(rf_IB, pred.var='L2Y6C1403', plot=TRUE)
partial(rf_IB, pred.var='L2Y6C0810', plot=TRUE)
partial(rf_IB, pred.var='L2Y6S0408', plot=TRUE)


partial(rf_IG, pred.var='L2Y6S0401', plot=TRUE)
partial(rf_IG, pred.var='L2Y6S2704', plot=TRUE)
partial(rf_IG, pred.var='L2Y6C0809', plot=TRUE)
partial(rf_IG, pred.var='L2Y6S0407', plot=TRUE)
partial(rf_IG, pred.var='L2Y6C1401', plot=TRUE)
partial(rf_IG, pred.var='L2Y6S0412', plot=TRUE)
partial(rf_IG, pred.var='L2Y6S0408', plot=TRUE)
partial(rf_IG, pred.var='L2Y6C0211', plot=TRUE)
partial(rf_IG, pred.var='L2Y6C0810', plot=TRUE)
partial(rf_IG, pred.var='L2Y6C0212', plot=TRUE)
