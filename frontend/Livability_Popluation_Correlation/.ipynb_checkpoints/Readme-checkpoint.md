# README: Correlation Analysis between Population and Livability Percentage in Melbourne

## Overview

This Jupyter notebook aims to understand and visualize the correlation between the livability percentage and the population of Melbourne. The analysis involves processing population-related data for Victoria and livability data for Melbourne, followed by statistical analysis and visualization.

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

2. **Livability Index Dataset**:
   - Contains information about the livability index in Melbourne.

## Data Processing Steps

### Loading Data from Elasticsearch

Both datasets are retrieved from Elasticsearch indices.

- **Regional Population Dataset**:
  - Index: `abs-regional_population_lga_2001-2021`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `response`.

- **Livability Index Dataset**:
  - Index: `liveability-index`
  - All documents are fetched using the `match_all` query.
  - Loaded into a pandas DataFrame named `liveability`.

### Data Cleaning

#### Regional Population Dataset

1. **Column Name Cleanup**:
   - Removed random spaces from column names.

2. **Key Columns Extraction**:
   - Extracted `erp_YYYY` columns for the years 2011 to 2021.
   - Created a cleaned DataFrame, `response_clean`, with columns `year` and `population`.

3. **Filter for Melbourne**:
   - Extracted the row corresponding to Melbourne from the population dataset.

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
   - Created a cleaned DataFrame, `liveability_clean`, with columns `year` and `livability_percentage`.

### Merging Datasets

- Merged the cleaned population and livability datasets on the `year` column, creating a single DataFrame, `analysis_df`, with columns `year`, `livability_percentage`, and `population`.

## Analysis and Visualization

1. **Correlation Analysis**:
   - Calculated the Pearson correlation coefficient between `livability_percentage` and `population`.

2. **Heatmap Visualization**:
   - Created an interactive heatmap using Plotly to visualize the correlation matrix.

## Conclusion

The analysis demonstrates the correlation between the livability percentage and population in Melbourne. The interactive heatmap provides a clear visualization of this relationship.

---

This README file provides a comprehensive overview of the data processing, cleaning, analysis, and visualization steps undertaken in the notebook.
