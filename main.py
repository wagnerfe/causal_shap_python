import numpy as np
import pandas as pd
import math
import xgboost
from explainer import Explainer
import shap
import time

if __name__ == '__main__':

    bike = pd.read_csv("Bike-dataset/day.csv")
    # Difference in days, which takes DST into account
    bike["trend"] = bike["instant"]-1
    bike["cosyear"] = np.cos(math.pi*bike["trend"]/365*2)
    bike["sinyear"] = np.sin(math.pi*bike["trend"]/365*2)
    # Unnormalize variables (see data set information in link above)
    bike["temp"] = bike["temp"] * (39 - (-8)) + (-8)
    bike["atemp"] = bike["atemp"] * (50 - (-16)) + (-16)
    bike["windspeed"] = 67 * bike["windspeed"]
    bike["hum"] = 100 * bike["hum"]

    x_var = ["trend", "cosyear", "sinyear", "temp", "atemp", "windspeed", "hum"]
    y_var = ["cnt"]

    X_data = bike[x_var]
    Y_data = bike[y_var]

    train_index = pd.read_csv('Bike-dataset/train_index.csv')["Resample1"].to_numpy()-1
    test_index = bike.index.difference(train_index)

    X_train = X_data.iloc[train_index]
    Y_train_nc = Y_data.iloc[train_index] # not centered
    Y_train = Y_train_nc.subtract(Y_train_nc.mean())

    X_test = X_data.iloc[test_index]
    Y_test_nc = Y_data.iloc[test_index] # not centered
    Y_test = Y_test_nc.subtract(Y_train_nc.mean())


    model = xgboost.XGBRegressor()
    model.load_model("Bike-dataset/R-bike-model.json")

    explainer_symmetric = Explainer(X_train, model)
    p = Y_train.mean()

    partial_order = [[0], [1, 2], [3, 4, 5, 6]]

    confounding = [False, True, False]

    explanation_causal = explainer_symmetric.explain_causal(X_test,
                                                            p,
                                                            ordering=partial_order,
                                                            confounding=confounding,
                                                            seed=None)

    shap.plots.waterfall(explanation_causal[126][[1, 3]])
    shap.plots.waterfall(explanation_causal[139][[1, 3]])