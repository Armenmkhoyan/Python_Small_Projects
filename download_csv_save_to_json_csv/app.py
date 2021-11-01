import csv
import itertools
import json
import logging
import os
import requests
import yaml

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s ')

logging.info(" Getting all configurations from yaml file ")
YAML_PATH = "config.yaml"
with open(YAML_PATH, "r") as fl:
    data = yaml.safe_load(fl)

use_cache = data["use_cache"]
rows_count = int(data["rows_count"])
column_count = int(data["column_count"])
temp_folder = data["temp_folder"]
path_to_save = os.path.join(data["temp_folder"], data["output_file"])
path_to_temp = os.path.join(data["temp_folder"], data["temp_file"])


def get_request():
    """
    Function Sending request and returns response

    """
    url = data["url"]
    logging.info("Sending request to url ")
    try:
        req = requests.get(url)

    except Exception as e:
        logging.error(f"Wrong URL , file does not exist, error: {e} ")
    else:
        file_content = req.text
        logging.info("Response have gotten successful ")
        return file_content


def save_cache_to_csv(content):
    """
    Function getting response and saving all date to cache csv file
    :param content: response as text  earlier received

    """
    logging.info("Saving response to .csv file")
    with open(f"{path_to_temp}", "w") as fl:
        fl.write(content)


def write_to_json(opened_file):
    """
    Function getting earlier opened  cache file and path to safe all N_rows and N_columns to .json file
    :param opened_file: cache file type (class '_io.TextIOWrapper')

    """
    logging.info(" Starting to write the result to json file ")
    row_count = 0
    reader_json = csv.DictReader(opened_file)
    json_list = []
    for row in reader_json:
        if row_count == rows_count:
            break
        json_line = dict(itertools.islice(row.items(), column_count))
        json_list.append(json_line)
        row_count += 1

    with open(f"{path_to_save}.json", "w") as js:
        json.dump(json_list, js, indent=4, ensure_ascii=False)
    logging.info(" json file have wrote succeed ")


def write_to_csv(opened_file):
    """
    Function getting earlier opened  cache file and path to safe all N_rows and N_columns to .csv file
    :param opened_file: cache file type (class '_io.TextIOWrapper')

    """

    logging.info(" Starting to write the result to csv file ")
    reader_csv = csv.reader(opened_file)
    count = 0
    for row in reader_csv:
        if count == rows_count:
            break
        csv_line = row[0: column_count]
        with open(f"{path_to_save}.csv", "a") as fl:
            writer = csv.writer(fl)
            writer.writerow(csv_line)
            count += 1
    logging.info("csv file have wrote succeed ")


def open_file_and_save():
    """
    Function opens cache file and gives opened file as parameter

    """
    logging.info(" Opening the temp file from cache to read ")
    with open(path_to_temp, "r") as file:
        write_to_json(file)
        write_to_csv(file)


def main():
    """
    Main function.
    in first  case checking if cash empty and  use_cache param is True
    in second case checking if cache is full and use_cache param is True
    in third case  checking if  use_cache is False no need save temp in cache
    """
    os.makedirs(temp_folder, exist_ok=True)

    logging.info(" Checks if cache empty and use_cache is True")
    is_file_exist = os.path.exists(path_to_temp)

    if use_cache and not is_file_exist:
        content = get_request()
        save_cache_to_csv(content)
        open_file_and_save()

    elif use_cache and is_file_exist:
        logging.info(" Checks if cache not empty and use_cache is True ")
        open_file_and_save()

    else:
        logging.info(" Checks if cache empty and use_cache is False ")
        content = get_request()
        write_to_csv(content.splitlines())
        write_to_json(content.splitlines())


if __name__ == "__main__":
    main()
