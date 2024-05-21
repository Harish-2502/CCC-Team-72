# README: Modeling Livability and Rental Affordability in Melbourne

## Overview

This Jupyter notebook is used for modeling the relationship between the livability score of Melbourne and the rental affordability index in Greater Melbourne. The analysis involves processing and cleaning the data, followed by statistical analysis and visualization to understand the correlation between these variables.

## Libraries Used

The following libraries are used in this notebook:

- pandas
- numpy
- seaborn
- matplotlib.pyplot
- statsmodels
- scipy
- plotly
- elasticsearch

## Data Sources

1. **Melbourne Livability Score Dataset**:
   - Contains multiple livability-related scores for different regions in Melbourne.
   - Key features: `numerator`, `denominator`, and `value` columns representing various livability scores.

2. **Greater Melbourne Rental Affordability Index Dataset**:
   - Contains information about rental affordability in Melbourne.
   - Key features: Columns representing the rental affordability index for various postcodes over different quarters from 2011 to 2021.

## Data Processing Steps

### Loading Data from Elasticsearch

Both datasets are retrieved from Elasticsearch indices.

- **Livability Index Dataset**:
  - Index: `liveability-index`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `liveability`.

- **Rental Affordability Index Dataset**:
  - Index: `rental_affordability`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `rental_affordability`.

### Data Cleaning

#### Livability Index Dataset

1. **Filter Data**:
   - Filtered rows where `type` is 'Liveability' and `value_type` is 'Percentage'.
   - Extracted the year from the `period` column.
   - Removed NaN values from `numerator` and `denominator`.

2. **Numerator and Denominator Cleanup**:
   - Converted `numerator` and `denominator` columns to integers after removing commas and converting to float.

3. **Remove Outliers**:
   - Removed rows where the `indicator` is 'Percentage of country GDP' to avoid skewing the data.

4. **Yearly Percentage Calculation**:
   - Calculated the yearly average percentage for the livability index.
   - Created a cleaned DataFrame, `liveability_final`, with columns `year` and `percentage`.

#### Rental Affordability Index Dataset

1. **Column Name Cleanup**:
   - Removed random spaces from column names.

2. **Key Columns Extraction**:
   - Extracted columns representing rental affordability for different years.
   - Calculated the yearly average rental affordability index.
   - Created a cleaned DataFrame, `rental_affordability_final`, with columns `year` and `rai`.

### Merging Datasets

- Merged the cleaned livability and rental affordability datasets on the `year` column, creating a single DataFrame, `analysis_df`, with columns `year`, `percentage`, and `rai`.

## Analysis and Visualization

### Correlation Analysis

- Calculated the Pearson correlation coefficient between `percentage` and `rai`.

### Regression Modeling

- Created several regression models to understand the impact of rental affordability on the livability percentage:
  1. **Full Model**: Includes interaction term (`rai * year`).
  2. **Nested Model 1**: Includes `rai` and `year` as predictors.
  3. **Nested Model 2**: Includes `year` and `rai` as predictors.
  4. **Simple Model**: Includes only `rai` as the predictor.

- The final selected model is **Nested Model 2** based on AIC comparison.

### Visualization

- Created an interactive heatmap using Plotly to visualize the correlation matrix.

## Conclusion

The analysis demonstrates the correlation between the livability percentage and rental affordability index in Melbourne. The final model indicates that both the year and rental affordability index are significant predictors of the livability percentage.

---

This README file provides a comprehensive overview of the data processing, cleaning, analysis, and visualization steps undertaken in the notebook.
