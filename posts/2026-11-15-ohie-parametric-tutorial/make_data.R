# Builds assets/tutorials/ohie_parametric/ohie.csv for the OHIE parametric tutorial.
# Run from a checkout of kalashnov/treatment-with-cost that has the OHIE public-use files:
#   cd treatment-with-cost && Rscript <site>/_tutorials/ohie_parametric/make_data.R <site>/assets/tutorials/ohie_parametric/ohie.csv
# Mirrors build_models(data, size = 0.5) in fit_models.R up to the nuisance forests (same seeds),
# so the in-browser linear IV fit reproduces the paper's linear parametric numbers.
suppressMessages({library(dplyr); library(grf); library(splitstackshape)})
source('datasets.R'); source('fit_models.R')  # prepare_medicare_data(), vars

out <- commandArgs(trailingOnly = TRUE)[1]
set.seed(0)
data <- prepare_medicare_data()  # cost = number of prescribed medications (rx_num_mod_12m)

# same household-stratified half split as build_models(size = 0.5)
train_cl <- as.integer(stratified(data$stratify_vars, group = names(data$stratify_vars), size = 0.5, keep.rownames = TRUE)$rn)
train <- data$cluster %in% train_cl
tr <- which(train)

# nuisance forests E[Y1|X], E[Y2|X]: out-of-bag on the training half, predictions on the test half
f1 <- regression_forest(data$demeaning_vars[tr, ], data$Y1[tr], clusters = data$cluster[tr], seed = 0)
f2 <- regression_forest(data$demeaning_vars[tr, ], data$Y2[tr], clusters = data$cluster[tr], seed = 0)
Y1.hat <- Y2.hat <- numeric(length(train))
Y1.hat[tr] <- predict(f1)$predictions;  Y1.hat[-tr] <- predict(f1, data$demeaning_vars[-tr, ])$predictions
Y2.hat[tr] <- predict(f2)$predictions;  Y2.hat[-tr] <- predict(f2, data$demeaning_vars[-tr, ])$predictions

# model features, built exactly as in build_models(): 18 covariates, centred birth year and its square,
# a missing-survey flag, then every missing value replaced by the column mean
X <- data$pretreatment_vars[vars]
X$birthyear_list <- X$birthyear_list - mean(X$birthyear_list[tr], na.rm = TRUE)
X$birthyear_list2 <- X$birthyear_list^2
X$is_na_m0 <- as.numeric(is.na(X$rx_num_mod_0m))
X[] <- lapply(X, function(x) replace(x, is.na(x), mean(x, na.rm = TRUE)))
names(X) <- paste0("X.", names(X))

d <- data.frame(household = data$cluster,  # the page redoes the split with stratified() and seed 0
                hhsize = data$pretreatment_vars$numhh_list,  # lottery-list household size: the page computes
                W = data$treatment, health = data$Y1, medication = data$Y2,  # the winning probability from it
                health.hat = Y1.hat, medication.hat = Y2.hat, X)
num <- sapply(d, is.double)
d[num] <- lapply(d[num], signif, digits = 7)  # keeps the file small; results unchanged to 4 decimals
write.csv(d, out, row.names = FALSE)
cat('wrote', nrow(d), 'rows,', sum(train), 'train, to', out, '\n')
