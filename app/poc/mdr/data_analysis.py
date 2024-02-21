
import pandas as pd, os, json
from datetime import datetime, timedelta
import glob

class DataAnalysis:

    def af_mdf_log_prcessing(self):        
        sheet_names = ['Table 1', 'Table 2', 'Table 6', 'Table 8','Table 10']
        df_raw= pd.read_excel("./dataset/af_mdr_request_log/MDRlogsUSAF_2006-2016.xlsx", sheet_name=sheet_names)
        request_log_path= "./dataset/af_mdr_request_log/"
        dat_col_labels= ["DATE\nRECEIVED", "DATE RECEIVED", "FY 13 DATE RECEIVED"]
        remove_na_columns= ["SUBJECT"]
        os.makedirs(request_log_path, exist_ok=True)
        # Iterate over the entities
        for sheet in sheet_names:
            df = df_raw[sheet]
            matching_date_strings = set(dat_col_labels).intersection(set(df.columns))
            date_column_label = list(matching_date_strings)[0]
            df[date_column_label] = pd.to_datetime(df[date_column_label], format='%d-%b-%y', errors='coerce')
            df = df.dropna(subset=[date_column_label]+ remove_na_columns)
            today = pd.to_datetime('today')
            # Calculate the date for 2 years ago from today
            two_years_ago = today - timedelta(days=365*2)
            # Filter rows where the date is within the last 2 years
            import pdb;pdb.set_trace()
            # df = df[df[date_column_label] > two_years_ago]            
            df.to_excel(os.path.join(request_log_path, "MDRlogsUSAF_"+sheet+".xlsx"), index=False, engine='openpyxl')
            print(f"{sheet}.xlsx Processed")
        print("All processing completed")
    
    def af_mdf_log_analysis(self):
        directory="./dataset/af_mdr_request_log/"
        sheet_names = ['Table 1', 'Table 2', 'Table 3', 'Table 6', 'Table 8','Table 10', 'Table 11']
        df_raw= pd.read_excel("./dataset/af_mdr_request_log/MDRlogsUSAF_2006-2016.xlsx", sheet_name=sheet_names)
        # df_table_1= df_raw['Table 1']        
        df_table_11= df_raw['Table 11']
        report= {}
        excel_files = glob.glob(os.path.join(directory, '*.xlsx'))
        dataframes= []
        for file in excel_files:
            if "MDRlogsUSAF_Table" in file:
                file_name= file.split('/')[-1].split('.xlsx')[0]
                df_raw_entities= pd.read_excel(file)
                df_raw_entities["table_name"]= file_name
                dataframes.append(df_raw_entities)    
        all_df_dataset = pd.concat(dataframes, ignore_index=True)
        all_df_dataset= all_df_dataset.drop(columns=[1])
        report["sample_size_before_cleaning"]= all_df_dataset.shape[0]   

        #Setting closure date from raw excel file for Table11 to processed dataframe from gpt
        for index, row in df_table_11[df_table_11['Closure Date'].notna()].iterrows():
            filtered_rows= all_df_dataset[(all_df_dataset['table_name']=='MDRlogsUSAF_Table 11') & 
                                      (all_df_dataset['AF MDR']==row['AF Case #'])]
            if len(filtered_rows) == 1:
                row_index= filtered_rows.index[0]                
                all_df_dataset.loc[row_index, 'CLOSURE DATE']= row['Closure Date']
            else:
                print(f"More than 1 row or no row found. Sample size is {len(filtered_rows)}")

        # If the 'DATE RECEIVED' is null then setting "1-Jan-year", This year is decided by begining number of MDR
        date_received_na_index= all_df_dataset[all_df_dataset['DATE RECEIVED'].isna()].index
        all_df_dataset.loc[date_received_na_index, 'DATE RECEIVED']= "1-Jan-"+all_df_dataset.loc[date_received_na_index,'AF MDR'].str.split('-MDR').str[0].str.split('‐MDR').str[0]\
                                                                    .str.split('Congressional').str[-1].str.split('APPEAL').str[-1].str.strip() # Their is a special character in the MDR split
        
        report["total_requestors"]= len(all_df_dataset['RECEIVED FROM'].unique())
        total_request_by_requestors= all_df_dataset['RECEIVED FROM'].value_counts().to_dict()
        report["total_request_by_requestors"]={}
        for key, value in total_request_by_requestors.items():            
            if not isinstance(key, datetime):                
                report["total_request_by_requestors"][key]= value
        report["total_mdr_appeals"]= all_df_dataset[all_df_dataset['AF MDR'].str.lower().str.contains("appeal")].shape[0]
        report["total_mdr_duplicates"]= all_df_dataset[all_df_dataset['AF MDR'].str.lower().str.contains("duplicate")].shape[0]
        report["total_mdr_reference"]= all_df_dataset[all_df_dataset['AF MDR'].str.lower().str.contains("reference")].shape[0]
        report["total_closed_request"]= all_df_dataset[all_df_dataset['CLOSURE DATE'].notna()].shape[0]
        report["total_pending_request"]= all_df_dataset.shape[0] - all_df_dataset[all_df_dataset['CLOSURE DATE'].notna()].shape[0]        

        # Finding Pending Requests from last 2 years
        report["pending_requests"]={}
        all_df_dataset['DATE RECEIVED'] = pd.to_datetime(all_df_dataset['DATE RECEIVED'], format='%d-%b-%y', errors='coerce')
        all_df_dataset = all_df_dataset.dropna(subset=['DATE RECEIVED'])
        today = pd.to_datetime('today')
        # Calculate the date for 2 years ago from today
        eight_years_ago = today - timedelta(days=365*8)
        twelve_years_ago = today - timedelta(days=365*12)
        sixteen_years_ago = today - timedelta(days=365*16)
        # Filter rows where the date is within the last 2 years
        last_8year_pending_requests = all_df_dataset[(all_df_dataset['CLOSURE DATE'].isna()) & (all_df_dataset['DATE RECEIVED'] > eight_years_ago)]
        between_last_8_and_12_years_pending_requests = all_df_dataset[(all_df_dataset['CLOSURE DATE'].isna()) & (all_df_dataset['DATE RECEIVED'] <= eight_years_ago) & (all_df_dataset['DATE RECEIVED'] >= twelve_years_ago)]
        between_last_12_and_16_years_pending_requests = all_df_dataset[(all_df_dataset['CLOSURE DATE'].isna()) & (all_df_dataset['DATE RECEIVED'] <= twelve_years_ago) & (all_df_dataset['DATE RECEIVED'] >= sixteen_years_ago)]
        more_than_16years_pending_requests = all_df_dataset[(all_df_dataset['CLOSURE DATE'].isna()) & (all_df_dataset['DATE RECEIVED'] < sixteen_years_ago)]
        # report["last_2year_pending_requests"]= last_2year_pending_requests.shape[0]

        report["pending_requests"]["last_8year"]= {
            "label":"<8",
            "value":last_8year_pending_requests.shape[0]
        }
        report["pending_requests"]["between_8_and_12"]= {
            "label":"8<= years =<12",
            "value":between_last_8_and_12_years_pending_requests.shape[0]
        }
        report["pending_requests"]["between_12_and_16"]= {
            "label":"12<= years =<16",
            "value":between_last_12_and_16_years_pending_requests.shape[0]
        }
        report["pending_requests"]["above_16"]= {
            "label":">16",
            "value":more_than_16years_pending_requests.shape[0]
        }

        report["sample_size_after_cleaning"]= all_df_dataset.shape[0]


        entities_temp= {}
        #Entities manipulation
        for entities in all_df_dataset[all_df_dataset["entities"].notna()]["entities"]:            
            if 'categories' in entities:
                entities= eval(entities)
                for entity in entities:
                    if 'categories' in entity:
                        for category in entity['categories']:
                            category= category.upper()
                            if category in entities_temp:                                
                                entities_temp[category]= entities_temp[category] + 1
                            else:
                                entities_temp[category]= 1
        report["entity_details"]= {
            "category_entries": entities_temp
        }
        #Save report to json file
        file_name = os.path.join(directory, 'af_mdr_request_log_report.json')
        with open(file_name, 'w') as file:
            json.dump(report, file)        
        print("Report Generated.")
        

    def run(self):
        # self.af_mdf_log_prcessing()
        self.af_mdf_log_analysis()

DataAnalysis().run()



"""
Note:
Unformatted date formats are "8/11/2010,9/27/11", "#REF!" for 13-MDR-028 at Table8, 
21-Dec for 08-MDR-051 at Table2, ]\] for 10-MDR-114 at Table 6

Fount unsupported characters like a box in a string for MDR column especially on hyphen
"""

# all_df_dataset[all_df_dataset['DATE RECEIVED'].str.contains('\\\\', na=False)]