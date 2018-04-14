# return_modeling
This code models starts by pulling data from January 2000 to November 2017. The purpose of the code is to model log returns with lagged log returns and moving average of returns. Then, using the model, calculate 60 day returns after 1/1/2016 and 1/3/2017.

## Data
The data pulled from the Yahoo API was saved as a .h5 file. If you don't wish to spend time downloading the data or the Yahoo API isn't working for you, the .h5 data panel can be found at the link [here, labeled as 'api_data.'](https://goo.gl/DoHABj)

## Classes
### Reader
Takes in the provided firm data from the NYSE and NASDAQ, and filters out values using a limiting market capitalization. In the main code, $500 million was the minimum market cap allowed. This left roughly 3100 firms to pull data and run the model on.

### API
Pulls return data from the Yahoo Finance API. Because of the large list of firms, the process can take upwards of 20 minutes. To avoid repeating the download process with every run of the code, the date panel is then saved as a [.h5 file](https://goo.gl/DoHABj). It can then be read from within the working directory.

### Model
This creates the x and y variables for the model. The time periods over which each variable is calculated can be changed to the users desire. Each variable is calculated by pulling the adjusted close prices from the API data panel. Using the date as an index, the prices can be found and the desired variables can be calculated. The variables are described below.

#### Log Returns
Log returns, the dependant variable, can be calculated over three specific periods. In this code, the returns are over 1, 5 and 22 days. Log returns can be calculated using the following formula:

    R(n,t) = log(P_t / P_t-n)

    where:
        t = current day
        n = number of days prior
        P_x = adjusted close price at a given day

#### Moving Average
The first independent variable is the moving averages. The moving averages are conducted across 5, 22 and 200 days. The moving average equation is:

    MA(m,t) = (P_t-1 + ... + P_t-m)/m

    where:
        t = current day
        m = window of average
        P_x = adjusted close price at a given day

#### Lagged Log Returns
Lagged log returns is the final variable. They are calculated over 5, 22 and 68 days in this code. The equation is:

    PA(k,t) = log(P_t-1 / P_t-k)

    where:
        t = current day
        k = number of days prior
        P_x = adjusted close price at a given day

## Main Script
To model the return variables, a nested for loop was created. The loop can add as many dates as the users wants, so long as it falls within the pulled api data panel. The first loop iterates through the two sets of dates desired. A data frame of the all the dates to be used was pulled using the starting date and a desired period (in this case, 60 days). The next loop iterates through each variation of the log returns. The 6 independent variables and a constant are then modeled with the log returns for each firm. Stats_model.api was used for the OLS in this case.

After each iteration, the coefficients and P > |t| values (P values) for each variable were saved for the respective variation of log returns. Once all the loops are completed, the average and standard deviation of the coefficients are calculated for the time period. The average of the P values are also calculated, to observe the effectiveness of the model. The averaged values and standard deviation are then output to a .csv with appropriate labels.

## Observations
The next step was to observe the significance of the model in its ability to predict the log returns of the roughly 3000 firms over the 60 day time period. P values support strong evidence against the null hypothesis if they are <= 0.05. In the 2016 model, all the variations of log returns had 4 of the 6 variables as statistically significant. For 2017 however, the 1 day log returns had no variable coefficient with a P value under 0.05. 5 and 22 day log returns for 2017 had at least one statistically significant variable.

Because of the wide breadth of firms captured by the criteria of market capitalization, it should be expected that a predictive model would be difficult. Since there is likely very little correlation between many of the firms due to different industries, market correlation, and outliers, a completely statistically significant set of coefficients wasn’t necessarily expected. However, this model should still capture a relatively accurate prediction of the average of the firms over the time period. Given a more precise filter of firms, a statistically significant model should be possible.
