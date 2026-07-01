
"""
Handle CSV and Excel file parsing
"""

from fileinput import filename

import pandas as pd
import io
import base64


class FileHandler:
    """Handle CSV and Excel file parsing"""

    ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}
    MAX_FILE_SIZE_MB = 50
    
    
    @staticmethod
    def parse_file(file_content, filename: str):
            """Parse uploaded file and return DataFrame"""

            #  Validate filename and extension
            if not filename or '.' not in filename:
                raise ValueError("Invalid file name — missing file extension")

            ext = filename.rsplit('.', 1)[1].lower()

            if ext not in FileHandler.ALLOWED_EXTENSIONS:
                allowed = ", ".join(FileHandler.ALLOWED_EXTENSIONS)
                raise ValueError(f"Unsupported format. Allowed: {allowed}")

            try:
                #  File size check (approx from base64)
                size_mb = len(file_content) * 0.75 / (1024 * 1024)
                if size_mb > FileHandler.MAX_FILE_SIZE_MB:
                    raise ValueError(f"File too large. Max size is {FileHandler.MAX_FILE_SIZE_MB} MB")

                #  Decode base64 content
                content = file_content.split(',')[1]
                decoded = io.BytesIO(base64.b64decode(content))

                #  Parse based on extension
                if ext == 'csv':
                    for encoding in ('utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1'):
                        try:
                            decoded.seek(0)
                            df = pd.read_csv(decoded, encoding=encoding)
                            print(f"[OK] CSV parsed using encoding: {encoding}")
                            break
                        except Exception:
                            continue
                    else:
                        raise ValueError("Could not decode file — try saving as UTF-8 CSV.")

                elif ext == 'xlsx':
                    df = pd.read_excel(decoded, engine='openpyxl')

                elif ext == 'xls':
                    df = pd.read_excel(decoded, engine='xlrd')

                else:
                    raise ValueError("Unsupported file type")

                #  Ensure clean column names
                df.columns = df.columns.astype(str)

                return df

            except Exception as e:
                # print(f"[ERROR] File parsing failed: {e}")
                # raise ValueError(f"Failed to parse {filename}. Please check file format.")
                import traceback
                print("=" * 80)
                print("ORIGINAL FILE PARSE ERROR")
                traceback.print_exc
                print("=" * 80)
                
                raise

    @staticmethod
    def validate_dataframe(df):
        """Validate DataFrame has required structure

        Returns: (is_valid, error_message)
        """
        if df.empty:
            return False, "File is empty"
        if len(df) < 2:
            return False, "File must have at least 2 rows"
        if len(df.columns) < 2:
            return False, "File must have at least 2 columns"
        return True, None
