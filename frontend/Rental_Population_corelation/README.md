# README: Correlation Analysis between Population and Rental Affordability in Melbourne

## Overview

This Jupyter notebook aims to understand the correlation between the population of Melbourne and rental affordability, and the impact of COVID-19 on the rental affordability index in the Melbourne region. The analysis involves processing population-related data for Victoria and rental affordability data for Greater Melbourne, followed by statistical analysis and visualization.

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

1. **Regional Population Dataset**:
   - Contains population-related information in Victoria, ranging from births, deaths to migration.
   - Key feature: `erp_YYYY` columns, which hold the estimated regional population for Melbourne from 2011 to 2021.

2. **Greater Melbourne Rental Affordability Index**:
   - Contains information about the rental affordability in Greater Melbourne.

## Data Processing Steps

### Loading Data from Elasticsearch

Both datasets are retrieved from Elasticsearch indices.

- **Regional Population Dataset**:
  - Index: `abs-regional_population_lga_2001-2021`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `response`.

- **Rental Affordability Dataset**:
  - Index: `rental_affordability`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `rental_affordability`.

### Data Cleaning

#### Rental Affordability Dataset

1. **Column Name Cleanup**:
   - Removed random spaces from column names.

2. **Average RAI Calculation**:
   - Calculated the average Rental Affordability Index (RAI) for each year from 2011 to 2021.
   - Created a cleaned DataFrame, `rental_affordability_clean`, with columns `year` and `rental_affordability_index`.

#### Regional Population Dataset

1. **Column Name Cleanup**:
   - Removed random spaces from column names.

2. **Key Columns Extraction**:
   - Extracted `erp_YYYY` columns for the years 2011 to 2021.
   - Created a cleaned DataFrame, `response_clean`, with columns `year` and `population`.

3. **Filter for Melbourne**:
   - Extracted the row corresponding to Melbourne from the population dataset.

### Merging Datasets

- Merged the cleaned population and rental affordability datasets on the `year` column, creating a single DataFrame, `analysis_df`, with columns `year`, `rental_affordability_index`, and `population`.

## Analysis and Visualization

1. **Correlation Analysis**:
   - Calculated the Pearson correlation coefficient between `rental_affordability_index` and `population`.

2. **Heatmap Visualization**:
   - Created a heatmap to visualize the correlation matrix.

3. **Trend Analysis**:
   - Created a line plot to visualize the trend of the Rental Affordability Index over the years.

4. **Impact of COVID-19**:
   - Calculated the percentage increase in the Rental Affordability Index from 2019 to 2021 to understand the impact of COVID-19.
   - Annotated the trend plot to highlight the COVID-19 impact period.

## Conclusion

The analysis demonstrates a correlation between population and rental affordability in Melbourne. The Rental Affordability Index significantly increased during the COVID-19 period, indicating an impact on rental affordability.

---

This README file provides a comprehensive overview of the data processing, cleaning, analysis, and visualization steps undertaken in the notebook.
