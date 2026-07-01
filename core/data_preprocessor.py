"""Data preprocessing based on confirmed data types"""
import pandas as pd
from typing import Dict, Optional

from pandas import col

class DataPreprocessor:
    """Apply preprocessing to columns based on confirmed data types"""

    @staticmethod
    def preprocess_column(col: str, dtype: str, series: pd.Series) -> pd.Series:
        if dtype == 'numeric':
            if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
                cleaned = (
                    series.astype(str)
                    .str.strip()
                    .str.replace(r'[^\d.\-+eE]', '', regex=True)
                )
                return pd.to_numeric(cleaned, errors='coerce')
            else:
                return pd.to_numeric(series, errors='coerce')

        elif dtype == 'temporal':
            return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)

        elif dtype == 'categorical':
            return series.astype(str).where(series.notna(), None)

        elif dtype == 'boolean':
            return series.astype(str).str.lower().map({
                'true': True,
                'false': False,
                '1': True,
                '0': False
            }).fillna(False)

        else:
            return series

    @staticmethod
    def preprocess_dataframe(
        df: pd.DataFrame,
        confirmed_dtypes: Dict[str, str]
    ) -> pd.DataFrame:
        """Apply preprocessing to dataframe based on confirmed types"""
        df_processed = df.copy()

        for col, dtype in confirmed_dtypes.items():
            if col in df_processed.columns and dtype != 'ignore':
                df_processed[col] = DataPreprocessor.preprocess_column(
                    col, dtype, df_processed[col]
                )

        return df_processed

    @staticmethod
    def get_preprocessing_report(
        df: pd.DataFrame,
        confirmed_dtypes: Dict[str, str]
    ) -> Dict:
        """Generate a report of what preprocessing will be applied"""
        report = {}

        for col, dtype in confirmed_dtypes.items():
            if col not in df.columns:
                continue

            original = df[col]
            
        try:
            processed = DataPreprocessor.preprocess_column(col, dtype, original)
        except Exception as e:
            print(f"[WARN] Preprocessing failed for column {col}: {e}")
            processed = original

            report[col] = {
                'original_dtype': str(original.dtype),
                'confirmed_dtype': dtype,
                'original_sample': original.head(3).tolist(),
                'processed_sample': processed.head(3).tolist(),
                'original_null_count': original.isna().sum(),
                'processed_null_count': processed.isna().sum(),
                'will_change': not original.equals(processed),
            }

        return report
