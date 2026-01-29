# Machine Learning Approach

For the machine learning it was decided by the group to focus on using the total combined footfall for all of the DCMS data. The reason for this being twofold, firstly to create a simpler model (versus each museum separately) and secondly, to, if a viable model can be created, predict when footfall fully recovers from COVID. Some museums have fully recovered from the lockdowns however as a comprehensive set footfall overall is lower than 2020.

---

# Classification of Terms

- **Decision Tree**  
  A Decision Tree is a flowchart like structure where each of the nodes represents a feature of the data, the branches are the rules and the final leaves are the outcomes of the algorithm.

- **Ensemble Learning**  
  Ensemble Learning is where several models or methods are used in conjunction to facilitate better learning. Eg random forest.

- **Random Forest**  
  A random forest is simply several decision trees that are run on the same dataset but using different samples. The outcome of each of these are averaged to achieve the final result.

- **Boosting**  
  Instead of running models in parallel, they are run sequentially so each iteratively improves on the last.

- **Non stationary time series**  
  This is a dataset that contains trends. Due to the increasing or decreasing mean over a time series, poorly chosen models can incorrectly conclude that time plays a larger part in the change. A model not appropriate to non stationary data will overfocus on the total for the time point and not the incremental change.

---

# Data Preparation

To start, the data was reshaped to two columns of date and footfall. The date column was converted into a datetime format. The reason for this is that our data most closely represents a time series and this transformation allows the correct type of regression model to be used.

A simple 80/20 training/test data split was created to test several models. The initial models chosen were linear regression, XGBoost and ARIMA.

---

# Initial Models

## Linear Regression

Linear Regression is a model in which a straight line is plotted to determine the predictive relationship between a datapoint and a target. The limitations of this model versus the dataset were known from the outset – linear regression handles trends well but does not predict well based on datasets with upwards and downwards movement.

The reason this model was chosen was to simply provide a benchmark against which other models could be compared.

---

## XGBoost

XGBoost was chosen due to it being an ensemble method that uses boosting. Multiple decision trees are created which reduce the likelihood of overfitting. Due to the anomalous nature of the ‘COVID dip’ it was decided that model choice must be cautious when it comes to overfitting to not ‘bake in’ the dip.

There are many computational improvements in this algorithm in comparison to regular gradient boosting, however due to the small nature of our dataset these were not readily shown. The results of XGBoost were more accurate than linear regression.

---

## ARIMA

ARIMA stands for Autoregressive Integrated Moving Average. This means that the model compares with previous lagged datapoints to come up with predictions, will automatically difference the data to cope with non stationary data and a create a sliding window for calculating the mean is used.

This model was chosen to test due the ease of data fitting as simply the footfall data (without dates) needed to be provided. The curve predicted by this model resulted in a flat line.

---

# Model Selection and Feature Engineering

The decision was made based on this preliminary testing to move forward with XGBoost. The data features were engineered to increase performance of the preliminary testing. Columns were created for different time periods but also for lags. This is to provide the model with a variety of variables for it on which to base its predictions.

---

# Model Evaluation

The model was evaluated using cross validation. The TimeSeriesSplit library was used to create five folds of the data, this was then used to check the consistency of the model over time.

The mean square and root mean square errors were calculated for each of the folds and then the averages of these were taken. These were compared to the mean of the footfall to give an approximate MAE error rate of 22 percent and RMSE of 28 percent. Due the to the nature of the data having the structural break of COVID this is a reasonable error rate; therefore, this model will be taken forward to use in footfall forecasting.

Interestingly, the corresponding figures for the initial test of XGBoost are MAE 10 percent and RMSE 13 percent rates.

The 80/20 data split was then fed into the model with intriguing results. The MAE percentage error was 8 percent, however the RMSE error was dramatic at 45 percent. This suggests that the initial time series K folds worked well but that the entire dataset caused the COVID dip to really increase the volatility of the predictions.


---

# Conclusion and Next Steps

The 8 percent error rate demonstrates that the model can predict well the overall number visitors, while the RMSE percentage shows that the model is not particularly accurate and that it is making many mistakes on correctly predicting footfall on a given month.

Next steps would be to engineer further and either add in flagging to alert the model that COVID is an anomalous event and is not expected to be repeated in 2025 or 2026.

The second would be to add seasonality features such Fourier Transformation but that would require extensive further research and knowledge. The current model could be used to predict an overall volume of visitors over a larger period but its limitation is it could not do this accurately month by month.
