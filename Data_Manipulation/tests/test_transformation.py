from moto import mock_s3
import boto3
from Data_Manipulation.src.transformation import retrieve_csv_from_s3_bucket, convert_csv_to_parquet_data_frame, create_dim_counterparty, create_dim_transaction, create_dim_payment_type, delete_cols_from_df, create_dim_currency, create_lookup_from_json, create_dim_design, create_dim_date, create_dim_location, create_dim_staff
import pandas as pd
import filecmp
from datetime import datetime

@mock_s3
def test_retrieve_csv_from_s3_bucket():

    file = "test_csv.csv"
    bucket = "test_bucket"

    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=bucket)
    s3.upload_file(Filename=file, Bucket=bucket, Key=file)

    result = retrieve_csv_from_s3_bucket(s3, bucket, file)
    
    filecmp.cmp(result.name, file)


def test_convert_csv_to_parquet_data_frame():
    
    file = 'test_csv.csv'
    
    df = pd.DataFrame({
        'sales_order_id': [1, 2],
        'created_at': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.186'],
        'last_updated': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.186'],
        'design_id': [9, 3],
        'staff_id': [16, 19],
        'counterparty_id': [18, 8],
        'units_sold': [84754, 42972],
        'unit_price': [2.43, 3.94],
        'currency_id': [3, 2],
        'agreed_delivery_date': ['2022-11-10', '2022-11-07'],
        'agreed_payment_date': ['2022-11-03', '2022-11-08'],
        'agreed_delivery_location_id': [4, 8]
    })

    with open(file, 'r') as f:
        result = convert_csv_to_parquet_data_frame(f)
    
    pd.testing.assert_frame_equal(result, df)


def test_delete_cols_from_df():
    
    test_df = pd.DataFrame({
        'col_1': [1, 2],
        'col_2': [1, 2]
    })
    
    expected_df = pd.DataFrame({
        'col_2': [1, 2]
    })

    result = delete_cols_from_df(test_df, ['col_1'])

    pd.testing.assert_frame_equal(result, expected_df)


def test_create_lookup_from_json():
    
    test_json_file = 'lookup_test.json'
    
    expected_lookup = {
        "ALL": "Albania Lek",
        "AFN": "Afghanistan Afghani",
        "ARS": "Argentina Peso"
    }

    result = create_lookup_from_json(test_json_file, 'abbreviation', 'currency')

    assert result == expected_lookup


def test_modify_data_for_dim_counterparty_table():

    counterparty_df = pd.DataFrame({
        'counterparty_id': [1, 2],
        'counterparty_legal_name': ['Fahey and Sons', 'Leannon, Predovic and Morar'],
        'legal_address_id': [15, 28],
        'commercial_contact': ['Micheal Toy', 'Melba Sanford'],
        'delivery_contact': ['Mrs. Lucy Runolfsdottir', ' Jean Hane III'],
        'created_at': ['2022-11-03 14:20:51.563', '2022-11-03 14:20:51.563'],
        'last_updated': ['2022-11-03 14:20:51.563', '2022-11-03 14:20:51.563'],
    })

    address_df = pd.DataFrame({
        'address_id': [15, 28],
        'address_line_1': ['605 Haskell Trafficway', '079 Horacio Landing'],
        'address_line_2': ['Axel Freeway', None],
        'district': [None, None],
        'city': ['East Bobbie', 'Utica'],
        'postal_code': ['88253-4257', '93045'],
        'country':['Heard Island and McDonald Islands', 'Austria'],
        'phone':['9687 937447', '7772 084705'],
        'created_at': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
        'last_updated': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
    })
   
    dim_counterparty_df = pd.DataFrame({
        'counterparty_id': [1, 2],
        'counterparty_legal_name': ['Fahey and Sons', 'Leannon, Predovic and Morar'],
        'address_line_1': ['605 Haskell Trafficway', '079 Horacio Landing'],
        'address_line_2': ['Axel Freeway', None],
        'district': [None, None],
        'city': ['East Bobbie', 'Utica'],
        'postal_code': ['88253-4257', '93045'],
        'country':['Heard Island and McDonald Islands', 'Austria'],
        'phone':['9687 937447', '7772 084705']
    })

    result = create_dim_counterparty(counterparty_df, address_df)

    pd.testing.assert_frame_equal(result, dim_counterparty_df) 


def test_modify_data_for_dim_transaction_table():
        
    transaction_df = pd.DataFrame({
        'transaction_id': [1, 2],
        'transaction_type': ['PURCHASE', 'PURCHASE'],
        'sales_order_id': [None, None],
        'purchase_order_id': [2, 3],
        'created_at': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.187'],
        'last_updated': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.187']
    })

    dim_transaction_df = pd.DataFrame({
        'transaction_id': [1, 2],
        'transaction_type': ['PURCHASE', 'PURCHASE'],
        'sales_order_id': [None, None],
        'purchase_order_id': [2, 3]
    })

    result = create_dim_transaction(transaction_df)

    pd.testing.assert_frame_equal(result, dim_transaction_df)


def test_modify_data_for_dim_payment_type():

    payment_type_df = pd.DataFrame({
        'payment_type_id': [1, 2],
        'payment_type_name': ['SALES_RECEIPT', 'SALES_REFUND'],
        'created_at': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
        'last_updated': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962']
    })

    dim_payment_type = pd.DataFrame({
        'payment_type_id': [1, 2],
        'payment_type_name': ['SALES_RECEIPT', 'SALES_REFUND'],
    })

    result = create_dim_payment_type(payment_type_df)

    pd.testing.assert_frame_equal(result, dim_payment_type)


def test_modify_data_for_dim_currency():

    currency_df = pd.DataFrame({
        'currency_id': [1, 2],
        'currency_code': ['GBP', 'USD'],
        'created_at': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
        'last_updated': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962']
    })

    lookup = {
        "GBP": "British Pound Sterling",
        "ARS": "Argentina Peso",
        "USD": "United States Dollar"
    }

    dim_currency = pd.DataFrame({
        'currency_id': [1, 2],
        'currency_code': ['GBP', 'USD'],
        'currency_name': ['British Pound Sterling', 'United States Dollar']
    })

    result = create_dim_currency(currency_df, lookup)

    pd.testing.assert_frame_equal(result, dim_currency)


def test_modify_data_for_dim_design():

    design_df = pd.DataFrame({
        'design_id': [1, 2],
        'created_at': ['2022-11-03 14:20:49.962', ' 2022-11-03 14:20:49.962'],
        'design_name': ['Wooden', 'Steel'],
        'file_location': [' /home/user/dir', '/usr/ports'],
        'file_name': ['wooden-20201128-jdvi.json', 'steel-20210621-13gb.json'],
        'last_updated': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962']
    })

    dim_design = pd.DataFrame({
        'design_id': [1, 2],
        'design_name': ['Wooden', 'Steel'],
        'file_location': [' /home/user/dir', '/usr/ports'],
        'file_name': ['wooden-20201128-jdvi.json', 'steel-20210621-13gb.json']
    })

    result = create_dim_design(design_df)

    pd.testing.assert_frame_equal(result, dim_design)


def test_modify_data_for_dim_date_for_unique_dates_on_sales_and_purchase_orders():

    sales_order_df = pd.DataFrame({
        'sales_order_id': [1, 2],
        'created_at': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.186'],
        'last_updated': ['2022-11-03 14:20:52.186', '2022-11-03 14:20:52.186'],
        'design_id': [9, 3],
        'staff_id': [16, 19],
        'counterparty_id': [18, 8],
        'units_sold': [84754, 42972],
        'unit_price': [2.43, 3.94],
        'currency_id': [3, 2],
        'agreed_delivery_date': ['2022-11-10', '2022-11-07'],
        'agreed_payment_date': ['2022-11-03', '2022-11-08'],
        'agreed_delivery_location_id': [4, 8]
    })

    dim_date_from_transaction_df = pd.DataFrame({
        'date_id': [datetime.strptime('2022-11-03', '%Y-%m-%d'), datetime.strptime('2022-11-10', '%Y-%m-%d'), datetime.strptime('2022-11-07', '%Y-%m-%d'),  datetime.strptime('2022-11-08', '%Y-%m-%d')],
        'year': [2022, 2022, 2022, 2022],
        'month': [11, 11, 11, 11],
        'day': [3, 10, 7, 8],
        'day_of_week': [3, 3, 0, 1],
        'day_name': ['Thursday', 'Thursday', 'Monday', 'Tuesday'],
        'month_name': ['November', 'November', 'November', 'November'],
        'quarter': [4, 4, 4, 4]
    })

    result = create_dim_date(sales_order_df)

    pd.testing.assert_frame_equal(result, dim_date_from_transaction_df)

def test_modify_data_for_dim_date_for_unique_dates_on_payment():
    payment_df = pd.DataFrame({
        'payment_id': [2, 3],
        'created_at': ['2022-11-03 14:20:52.187', '2022-11-03 14:20:52.186'],
        'last_updated': ['2022-11-03 14:20:52.187', '2022-11-03 14:20:52.186'],
        'transaction_id': [2, 3],
        'counterparty_id': [15, 18],
        'payment_amount': [552548.62, 205952.22],
        'currency_id': [2, 3],
        'payment_type_id': [3, 1],
        'paid': [False, False],
        'payment_date': ['2022-11-04', '2022-11-03'],
        'company_ac_number': ['67305075', '81718079'],
        'counterparty_ac_number': ['31622269', '47839086'],
    })

    dim_date_from_payment = pd.DataFrame({
        'date_id': [datetime.strptime('2022-11-03', '%Y-%m-%d'), datetime.strptime('2022-11-4', '%Y-%m-%d')],
        'year': [2022, 2022],
        'month': [11, 11],
        'day': [3, 4],
        'day_of_week': [3, 4],
        'day_name': ['Thursday', 'Friday'],
        'month_name': ['November', 'November'],
        'quarter': [4, 4]
    })

    result = create_dim_date(payment_df)

    pd.testing.assert_frame_equal(result, dim_date_from_payment)

def test_modify_data_for_dim_location():
    address_df = pd.DataFrame({
        'address_id': [15, 28],
        'address_line_1': ['605 Haskell Trafficway', '079 Horacio Landing'],
        'address_line_2': ['Axel Freeway', None],
        'district': [None, None],
        'city': ['East Bobbie', 'Utica'],
        'postal_code': ['88253-4257', '93045'],
        'country':['Heard Island and McDonald Islands', 'Austria'],
        'phone':['9687 937447', '7772 084705'],
        'created_at': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
        'last_updated': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
    })

    dim_location_df = pd.DataFrame({
        'address_id': [15, 28],
        'address_line_1': ['605 Haskell Trafficway', '079 Horacio Landing'],
        'address_line_2': ['Axel Freeway', None],
        'district': [None, None],
        'city': ['East Bobbie', 'Utica'],
        'postal_code': ['88253-4257', '93045'],
        'country':['Heard Island and McDonald Islands', 'Austria'],
        'phone':['9687 937447', '7772 084705'],
    })

    result = create_dim_location(address_df)

    pd.testing.assert_frame_equal(result, dim_location_df)


def test_modify_data_for_dim_staff():
    staff_df = pd.DataFrame({
        'staff_id': [1, 2],
        'first_name': ['Jeremie', 'Deron'],
        'last_name': ['Franey', 'Beier'],
        'department_id': [2, 6],
        'email_address': ['jeremie.franey@terrifictotes.com', 'deron.beier@terrifictotes.com'],
        'created_at': ['2022-11-03 14:20:51.563', '2022-11-03 14:20:51.563'],
        'last_updated':['2022-11-03 14:20:51.563', '2022-11-03 14:20:51.563'],
    })

    department_df = pd.DataFrame({
        'department_id': [6, 2],
        'department_name': ['Facilities', 'Purchasing'],
        'location': ['Manchester', 'Manchester'],
        'manager': ['Shelley Levene', 'Naomi Lapaglia'],
        'created_at': ['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
        'last_updated':['2022-11-03 14:20:49.962', '2022-11-03 14:20:49.962'],
    })

    dim_staff = pd.DataFrame({
        'staff_id': [1, 2],
        'first_name': ['Jeremie', 'Deron'],
        'last_name': ['Franey', 'Beier'],
        'department_name': ['Purchasing', 'Facilities'],
        'location': ['Manchester', 'Manchester'],
        'email_address': ['jeremie.franey@terrifictotes.com', 'deron.beier@terrifictotes.com'],
    })

    result = create_dim_staff(staff_df, department_df)

    pd.testing.assert_frame_equal(result, dim_staff)


def test_modify_data_for_fact_sales_order():
    pass


def test_modify_data_for_fact_payment():
    pass


def test_modify_data_for_fact_purchase_orders():
    pass


# ensure that we can read the file in the landing zone bucket
# convert the parquet file into readable python format
# prepare that data to be used for the processed bucket
# convert back to parquet
# store data in processed bucket
# upload processed bucket data into warehouse