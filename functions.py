import json
import tarfile
import pandas
import os

"""The tarfile module makes it possible to read and write tar archives"""


def load_dataset(dataset_path):
    """Function to Read data from the Massive Dataset."""
    data = []

    with tarfile.open(dataset_path, mode="r:gz") as data_archive:
        for member in data_archive.getmembers():
            if member.isfile() and member.name.endswith(".jsonl"):
                with data_archive.extractfile(member) as jsonl_data:
                    for line_bytes in jsonl_data:
                        line = line_bytes.decode("utf-8").strip()
                        if line:
                            data.append(json.loads(line))

    data_frame = pandas.DataFrame(data)

    return data_frame


def generate_translation_jsonl(dataframe, output_dir):
    """Combines translations from a DataFrame and saves them as (.jsonl) file.
     Args:
    dataframe (pandas.DataFrame): DataFrame containing translation data. output_dir (str): Directory to save the combined file.
    """

    locales = dataframe["locale"].unique()

    combined_data_list = []

    for locale in locales:
        if locale == "en-US":
            continue
        en_data = dataframe[dataframe["locale"] == "en-US"][["id", "utt", "annot_utt"]]
        locale_data = dataframe[dataframe["locale"] == locale]
        combined_data = pandas.merge(en_data, locale_data, on="id", how="inner")
        combined_data_list.extend(combined_data.to_dict("records"))

    jsonl_file_path = os.path.join(output_dir, "combined_translation.jsonl")

    with open(jsonl_file_path, "w", encoding="utf-8") as jsonl_file:
        for record in combined_data_list:
            jsonl_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def generate_language_excel_files(data_frame, output_dir):
    """Combines data from 'en-US' and other locales and saves as Excel files.
    Args:
        data_frame (pd.DataFrame): DataFrame containing data for various locales.
        output_dir (str): Directory to save the generated Excel files."""

    locales = data_frame["locale"].unique()

    if "en-US" in locales:
        en_data = data_frame[data_frame["locale"] == "en-US"]
        output_file_path = os.path.join(output_dir, "en-en.xlsx")
        en_data.to_excel(output_file_path, index=False)

        for locale in locales:
            if locale == "en-US":
                continue

            locale_data = data_frame[data_frame["locale"] == locale]
            en_us_data = data_frame[data_frame["locale"] == "en-US"][
                ["id", "utt", "annot_utt"]
            ]
            combined_data = pandas.merge(en_us_data, locale_data, on="id", how="inner")

            output_file_path = os.path.join(output_dir, f"en-{locale}.xlsx")
            combined_data.to_excel(output_file_path, index=False)


def filter_into_jsonl(xlsx_file_path, output_dir, filter_column, filter_value):
    """Reads data from Excel file, filters it based on a specified column and value and saves as jsonl file
    Args:
        xlsx_file_path (str): Input Excel file path, output_dir (str): Output directory for JSON Lines file, filter_column (str): Column to filter
        filter_value (str): Value to filter by"""

    data_f = pandas.read_excel(xlsx_file_path)
    filtered_data = data_f[data_f[filter_column] == filter_value]
    filtered_data_dict = filtered_data.to_dict(orient="records")

    jsonl_file_path = os.path.join(output_dir, f"{filter_value}.jsonl")
    with open(jsonl_file_path, "w", encoding="utf-8") as jsonl_file:
        for record in filtered_data_dict:
            jsonl_file.write(json.dumps(record, ensure_ascii=False) + "\n")
