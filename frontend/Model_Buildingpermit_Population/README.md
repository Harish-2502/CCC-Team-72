
# README: Data Modelling for Population Prediction

## Overview

This Jupyter notebook is designed to process and analyze data related to population and building permits in melbourne. The primary goal is to create a simple linear regression model to predict population based on the number of building permits issued. This document explains the data processing, cleaning, and modeling steps in detail.

## Libraries Used

The following libraries are used in this notebook:

- pandas
- numpy
- seaborn
- matplotlib.pyplot
- statsmodels
- plotly
- elasticsearch

## Data Sources

1. **Regional Population Dataset**:
   - Contains population-related information in Victoria, including births, deaths, and migration.
   - Key feature: `erp_YYYY` columns, which hold the estimated regional population for Melbourne from 2001 to 2021.

2. **Building Permits Dataset**:
   - Contains information about building permits in Melbourne.

## Data Processing Steps

### Loading Data from Elasticsearch

Both datasets are retrieved from Elasticsearch indices.

- **Regional Population Dataset**:
  - Index: `abs-regional_population_lga_2001-2021`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `response`.

- **Building Permits Dataset**:
  - Index: `building-permits`
  - All documents are fetched in chunks of 100 until all documents are retrieved.
  - Loaded into a pandas DataFrame named `predictor`.

### Data Cleaning

#### Regional Population Dataset

1. **Column Name Cleanup**:
   - The column names in the dataset had random spaces, which were removed using the `str.replace(' ', '')` method in pandas. This ensures consistency and avoids issues when referencing column names in the code.

2. **Key Columns Extraction**:
   - The dataset contains population estimates (`erp_YYYY` columns) for each year from 2001 to 2021. These columns were extracted into a new DataFrame, `response_clean`, with two main columns: `year` and `population`.
   - The year information was extracted from the column names by removing the `erp_` prefix and converting the remaining string to an integer.
   - The resulting DataFrame, `response_clean`, contains two columns: `year` and `population`.

#### Building Permits Dataset

1. **Initial Cleanup**:
   - The `issue_date` column, which indicates the date the permit was issued, was converted to a datetime format using `pd.to_datetime`.
   - A new column, `year`, was created by extracting the year from the `issue_date`.
   - Records where `issue_date` was greater than `completed_by_date` or where the year was in the future were removed to ensure data validity.

2. **Duplicate Handling**:
   - The dataset had duplicate records for permits issued to different parts of the same building or for different stages of the same permit. To handle this, duplicate permits were identified and removed by keeping only one record per `permit_number`.
   - This step reduced the number of records significantly and ensured that each permit is only counted once in the analysis.

3. **Aggregation**:
   - The cleaned dataset was grouped by `year` to count the number of building permits issued each year. This aggregation was done using the `groupby` method in pandas.
   - The resulting DataFrame, `predictor_clean`, contains two columns: `year` and `building_permit_count`.

### Merging Datasets

- The cleaned population and building permits datasets were merged on the `year` column using the `pd.merge` function. This combined the two datasets into a single DataFrame, `analysis_df`, which contains the columns `year`, `building_permit_count`, and `population`.
- The columns in `analysis_df` were converted to numeric types to ensure they are suitable for analysis.

### Modeling

1. **Correlation Analysis**:
   - The Pearson correlation coefficient between `building_permit_count` and `population` was calculated using the `corr` method. This coefficient measures the strength and direction of the linear relationship between the two variables. A correlation of 0.88 indicates a strong positive correlation.

2. **Linear Regression Models**:
   - **Partial Model**:
     - A simple linear regression model was created using the `ols` function from the `statsmodels` library. The model predicts `population` based on `building_permit_count`.
     - The model summary shows an R-squared value of 0.771, indicating that approximately 77.1% of the variability in population can be explained by the number of building permits.

   - **Full Model**:
     - Another linear regression model was created with two predictors: `building_permit_count` and `year`.
     - This model has an R-squared value of 0.965, indicating a much better fit, with 96.5% of the variability in population explained by the predictors.

   - **Interaction Model**:
     - An interaction term between `building_permit_count` and `year` was added to the model.
     - The interaction model showed an even higher R-squared value of 0.981, indicating a very good fit.
     - The significance of the interaction term suggests that the effect of building permits on population varies over time.

3. **Goodness of Fit**:
   - The AIC (Akaike Information Criterion) was used to compare the models. Lower AIC values indicate better model fit.
   - The ANOVA (Analysis of Variance) test was used to compare the models and test the significance of the predictors.

### Future Predictions

- The interaction model was used to predict the population for the years 2022, 2023, and 2024.
- The predicted values were rounded to the nearest whole number for reporting.

### Visualization

- Various plots were created using Plotly to visualize trends, correlations, and predictions:
  - **Trend Analysis**: Line plot showing the trend of building permits and population over the years.
  - **Correlation Analysis**: Scatter plot illustrating the relationship between building permits and population.
  - **Year-over-Year Growth Rate**: Bar plot comparing the year-over-year growth rates of building permits and population.
  - **Outlier Detection**: Box plot highlighting outliers in the building permits and population data.

## Conclusion

The notebook demonstrates a strong positive correlation (0.88) between building permits and population. The interaction model, which includes building permits, year, and their interaction, shows a high R-squared value (0.981), indicating a good fit.
