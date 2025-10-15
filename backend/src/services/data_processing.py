import zipfile
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from src.utils.exceptions import WrongFileTypeError

df: pd.DataFrame | None = None


def get_dataframe():
    """Returns the global pandas DataFrame used."""
    return df


class DataHandler:
    """
    Handles data loading and dataframe population.
    An instance of this class can be used to load a dataset from a CSV or zip file.
    """

    def __init__(self):
        pass

    async def load_csv(
        self,
        data: UploadFile,
        separator: str = ',',
        header: int = 0,
    ) -> bool:
        """Loads data from an uploaded file (CSV or a ZIP containing a CSV)
        into a pandas DataFrame. Inject data into a global df variable.

        Args:
            data (UploadFile): file to be read.
            separator (str, optional): csv separator. Defaults to ','.
            header (int, optional): headers line. Defaults to 0.

        Raises:
            WrongFileTypeError: When the file received is not supported.

        Returns:
            bool: True if read was successful.
        """
        global df
        file = await data.read()
        file_bytes = BytesIO(file)

        if data.content_type == 'application/zip':
            df = await self._load_zip(file_bytes, separator, header)

        elif data.content_type in ['text/csv', 'application/vnd.ms-excel']:
            df = pd.read_csv(file_bytes, sep=separator, header=header)

        else:
            raise WrongFileTypeError(
                f'Unsupported file type: {data.content_type}. '
                'Please upload a CSV or a ZIP file containing a CSV.'
            )

        return df.head().to_json()

    async def _load_zip(self, file: BytesIO, sep: str, header: int):
        """Function for reading zip files, decompressing and returning the resulting DataFrame.

        Args:
            file (BytesIO): zip file
            sep (str): csv separator
            header (int): headers line

        Raises:
            FileNotFoundError: When no CSV file is found after unzipping.

        Returns:
            DataFrame: Resulting dataframe read.
        """
        with zipfile.ZipFile(file) as zip_file:
            csv_filename = next(
                (name for name in zip_file.namelist() if name.endswith('.csv')),
                None,
            )

            if not csv_filename:
                raise FileNotFoundError('No CSV file found in the zip archive.')

            with zip_file.open(csv_filename) as csv_file:
                return pd.read_csv(csv_file, sep=sep, header=header)
