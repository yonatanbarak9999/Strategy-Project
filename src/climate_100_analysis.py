# ------------- Imports ------------------ #

import numpy as np
import os
import pandas as pd
from pathlib import Path
from typing import List, Tuple

import statsmodels.api as sm

# ------------- Consts ------------------- #

INPUT_PATH = os.path.join(os.path.dirname(Path(__file__)), '..', 'assets', 'values.csv')
LN_INDICATOR = ' (ln)'

COMPANY_NAME = 'Company name'
STOCK_HOLDERS_EQUITY_22 = 'Stockholders Equity - Total  - 22'
STOCK_HOLDERS_EQUITY_DIFF = 'Difference in Total Equity'
ROA = 'ROA'
ROE = 'ROE'
TOTAL_ASSETS_21 = 'Total Assets - 21'
TOTAL_ASSETS_22 = 'Total Assets - 22'
TOTAL_ASSETS_21_LN = TOTAL_ASSETS_21 + LN_INDICATOR
TOTAL_ASSETS_22_LN = TOTAL_ASSETS_22 + LN_INDICATOR
TOTAL_ASSETS_DIFF = 'Difference in Total Assets'
OP_INCOME_21 = 'Operational Income 21'
OP_INCOME_22 = 'Operational Income 22'
SALES_21 = 'Sales - 21'
SALES_22 = 'Sales - 22'
SALES_DIFF = 'Difference in Sales'
OP_INCOME_TO_SALES_21 = 'Operational Income to Sales -21'
OP_INCOME_TO_SALES_22 = 'Operational Income to Sales - 22'
OP_INCOME_TO_SALES_DIFF = 'Difference in Op. In /Sales (Operational Income/Sales growth)'
EARNING_PER_SHARE = 'Earning per Share - 22'
SECTOR = 'Sector'
ORGANIZATION_SCORE = 'Organization Score'
ORGANIZATION_PROGRESS = 'Organization Progress'
RELATIONSHIP_SCORE = 'Relationship score'
RELATIONSHIP_PROGRESS = 'Relationship progress'
ENGAGEMENT_INTENSITY_SCORE = 'Engagement Intensity score'
HQ_REGION = 'HQ Region'
SCOPE_3 = 'Scope 3 category'

INDICATOR = lambda x: f'Indicator {x}'
INDICATOR_PROGRESS = lambda x: f'Indicator {x} - progress'

INDICATORS = list(range(1, 11))
INDICATORS.remove(9)

NOT_APPLICABLE = 'Not applicable'

HQ_REGIONS = [
    "Europe",
    "Australasia",
    "Asia",
    "Africa",
    "North America",
    "South America",
]

HQ_COLUMN_NAME = lambda location: HQ_REGION + "-" + location

Y_VARIABLES = [
    OP_INCOME_TO_SALES_DIFF,
    ROA,
    ROE,
    EARNING_PER_SHARE,
]

X_VARIABLES = [
                  STOCK_HOLDERS_EQUITY_22,
                  TOTAL_ASSETS_22_LN,
                  ORGANIZATION_SCORE,
                  RELATIONSHIP_SCORE,
                  ENGAGEMENT_INTENSITY_SCORE,
                  SCOPE_3,
              ] + [HQ_COLUMN_NAME(hq) for hq in HQ_REGIONS]


# ------------- Classes ---------------- #

class Progress:
    IMPROVED = 'Improved'
    NO_CHANGE = 'No Change'
    DECLINED = 'Declined'
    _PROGRESS_VALUES = {
        'No change in score': NO_CHANGE,
        'Decline in score': DECLINED,
        'Not applicable': NO_CHANGE,
        'Improvement in score': IMPROVED,
    }

    @classmethod
    def get_progress(cls, value):
        return cls._PROGRESS_VALUES[value]

    @classmethod
    def get_progress_labels(cls, label) -> Tuple[List[str], List[str]]:
        return [label + ' ' + cls.IMPROVED,
                label + ' ' + cls.NO_CHANGE,
                label + ' ' + cls.DECLINED], \
               [cls.IMPROVED,
                cls.NO_CHANGE,
                cls.DECLINED],


class Indicator:
    YES = 'Yes'
    NO = 'No'
    PARTIAL = 'Partial'
    _INDICATOR_VALUES = {
        'Y': YES,
        'N': NO,
        'Partial': PARTIAL,
    }

    @classmethod
    def get_indicator(cls, value):
        return cls._INDICATOR_VALUES[value]

    @classmethod
    def get_indicator_labels(cls, label) -> Tuple[List[str], List[str]]:
        return [label + ' ' + cls.YES,
                label + ' ' + cls.NO,
                label + ' ' + cls.PARTIAL], \
               [cls.YES,
                cls.NO,
                cls.PARTIAL],


class DataSetParser:
    @classmethod
    def parse_file(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Parse the file to the relevant arguments.
        """
        labels = X_VARIABLES

        # Parse total assets parameters.
        df = cls._parse_total_assets(df)

        # Parse HQ parameter.
        df = cls._parse_hq(df)

        # Parse score parameters.
        df = cls._parse_climate_100_scores(df, RELATIONSHIP_SCORE)
        df = cls._parse_climate_100_scores(df, ORGANIZATION_SCORE)

        # Parse progress parameters.
        df, new_labels = cls._parse_progress_column(df, RELATIONSHIP_PROGRESS)
        labels += new_labels
        df, new_labels = cls._parse_progress_column(df, ORGANIZATION_PROGRESS)
        labels += new_labels

        # Parse scope 3 category.
        df = cls._parse_scope_3_category(df)

        # Parse indicators.
        for indicator in INDICATORS:
            df, new_labels = cls._parse_indicator_column(df, indicator)
            labels += new_labels
            df, new_labels = cls._parse_progress_column(df, INDICATOR_PROGRESS(indicator))
            labels += new_labels

        return df, labels

    @classmethod
    def _parse_indicator_column(cls, df: pd.DataFrame, indicator: int) -> Tuple[pd.DataFrame, List[str]]:
        """
        Create 3 new labels for 'Yes', 'No', 'Partial' and put the values in it.
        :param df: The given df.
        :param indicator: The indicator to handle.
        """
        column = INDICATOR(indicator)
        new_labels, label_values = Indicator.get_indicator_labels(column)
        labels_dict = {}
        for label in label_values:
            labels_dict[label] = np.zeros(df.shape[0])

        # Populate arrays with '1' based on the progress value.
        for index, value in enumerate(df[column]):
            matching_array = labels_dict[Indicator.get_indicator(value)]
            matching_array[index] = 1

        # Remove the column from the df.
        df.drop(column, axis='columns', inplace=True)

        # Add the new columns.
        for label, value in zip(new_labels, label_values):
            df[label] = labels_dict[value]

        return df, new_labels

    @classmethod
    def _parse_progress_column(cls, df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Handle the values in a progress column.
        :param df: The given df.
        :param column: The column holding progress values.
        """
        new_labels, label_values = Progress.get_progress_labels(column)
        labels_dict = {}
        for label in label_values:
            labels_dict[label] = np.zeros(df.shape[0])

        # Populate arrays with '1' based on the progress value.
        for index, value in enumerate(df[column]):
            matching_array = labels_dict[Progress.get_progress(value)]
            matching_array[index] = 1

        # Remove the column from the df.
        df.drop(column, axis='columns', inplace=True)

        # Add the new columns.
        for label, value in zip(new_labels, label_values):
            df[label] = labels_dict[value]

        return df, new_labels

    @classmethod
    def _parse_climate_100_scores(cls, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Handle the climate 100 scores
        :param df: The given df.
        :param column: The column holding score value.
        """

        def score_filter(value):
            return 0 if value == NOT_APPLICABLE else float(value)

        score_transformation = np.vectorize(score_filter)
        df[column] = score_transformation(np.array(df[column]))
        return df

    @classmethod
    def _parse_total_assets(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert total assets values to ln(values)
        :param df: The given df.
        """
        for total_assets, total_assets_ln in \
                zip([TOTAL_ASSETS_21, TOTAL_ASSETS_22], [TOTAL_ASSETS_21_LN, TOTAL_ASSETS_22_LN]):
            # Change values to ln(values).
            df[total_assets] = np.log(df[total_assets])

            # Rename the column name to show the ln was done on the values.
            df = df.rename(columns={total_assets: total_assets_ln})
        return df

    @classmethod
    def _parse_scope_3_category(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse Scope 3 category.
        :param df: The given df.
        """

        def scope_3_filter(value: str):
            return 1 if value.lower().find('yes') > -1 else 0

        scope_3_transformation = np.vectorize(scope_3_filter)
        df[SCOPE_3] = scope_3_transformation(df[SCOPE_3])

        return df

    @classmethod
    def _parse_hq(cls, df: pd.DataFrame) -> pd.DataFrame:
        for hq in HQ_REGIONS:
            label = HQ_COLUMN_NAME(hq)
            new_column = np.zeros(df.shape[0])
            for index in range(df.shape[0]):
                new_column[index] = 1 if df[HQ_REGION][index].find(hq) != -1 else 0

            df[label] = new_column

        df.drop(HQ_REGION, axis='columns', inplace=True)
        return df


# ------------- Functions ---------------- #

def load_df() -> pd.DataFrame:
    """
    :return: The df containing the analytic data.
    """
    return pd.read_csv(INPUT_PATH, sep=',')


def drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_drop = []
    for i in range(len(df.columns)):
        if sum(df[df.columns[i]]) == 0:
            columns_to_drop.append(df.columns[i])
    return df.drop(columns=columns_to_drop)


def linear_regression(df: pd.DataFrame, y_column: str, x_columns: List[str]):
    """
    Calculate linear regression on the parameters
    :param df: The given df.
    :param y_column: The y parameter of the regression.
    :param x_columns: The x parameters of the regression.
    """
    y_variable = df[y_column]
    x_variables = df[x_columns]

    x_variables = drop_irrelevant_columns(x_variables)

    model = sm.OLS(y_variable, x_variables).fit()
    print(model.summary())


# ------------- Entry Point -------------- #

def main():
    df: pd.DataFrame = load_df()

    # Parse df file.
    df, x_variables = DataSetParser.parse_file(df)

    # Models: choose the index from Y_VARIABLES
    linear_regression(df, Y_VARIABLES[0], x_variables)


if __name__ == '__main__':
    main()
