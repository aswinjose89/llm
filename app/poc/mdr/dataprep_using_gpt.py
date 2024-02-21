
from pathlib import Path
import openai, json, time
import pandas as pd, os
import nltk
import tiktoken, numpy as np
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from datetime import datetime, timedelta

openai.api_key ="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"

whitepaper_categories= """
1. Nuclear Operations and Safety:
    - Nuclear propulsion information.
    - Atomic Energy Detection System.
    - Safeguarding of nuclear materials or facilities.
    - Research on chemical and biological weapons.
    - Vulnerability to chemical or biological warfare.
2. Psychological Operations and Special Forces:
    - Psychological operations.
    - Escape, evasion, rescue, and recovery.
    - Insertion, infiltration, and exfiltration.
    - Deception and unconventional warfare.
3. Intelligence and Counterintelligence:
    - Sources and methods of intelligence.
    - Counterintelligence activities.
    - Clandestine human agents.
    - Analytical techniques for intelligence data.
4. Aerial Surveillance and Space Systems:
    - Airborne radar and intercept imagery.
    - Space system design and capabilities.
    - Orbital characteristics and network configurations.
5. Electronic Warfare and Communication Systems:
    - Operational communications equipment.
    - Electronic counter-countermeasures (ECCM).
    - Vulnerability to electronic warfare.
    - Electronic intelligence and telemetry intelligence.
6. Cryptologic Information:
    - COMSEC and SIGINT.
    - Cryptologic processes and techniques.
    - Recognition of cryptologic documents.
7. Ballistic Missile Defense (BMD) and Weapon Systems:
    - BMD missile information.
    - BMD systems data.
    - Radar-fuzing programs.
    - Guided projectiles technology.
    - Armor materials concepts and designs.
8. Naval Operations and Ship Information:
    - Conventional surface ship information.
    - Naval nuclear propulsion information.
    - Ship-silencing information.
    - Operational characteristics of surface ships and submarines.
9. Intelligence Operations and Foreign Policy:
    - Covert intelligence operations.
    - Diplomatic or economic activities affecting national security.
    - Foreign political, economic, or military actions against the United States.
    - International tension affecting U.S. foreign policy.
10. Defense Plans and Capabilities:
    - U.S. and allies' defense plans and capabilities.
    - Information disclosing U.S. systems and weapons capabilities.
    - U.S. nuclear programs, facilities, and intentions.
    - Research, development, and engineering for national security.
11. CIA Structure and Operations:
    - CIA structure, size, installations, security, objectives, and budget.
    - CIA personnel recruitment, training, and evaluation policies.
    - Training provided to or by the CIA.
12. Security and Confidential Information:
    - Special access programs.
    - Information identifying clandestine organizations, agents, sources, or methods.
    - Information divulging intelligence interests or assessment capabilities.
    - Information that could place individuals in jeopardy.
13. Foreign Intelligence Reports:
    - Reports from the Foreign Broadcast Information Service (FBIS).
    - Reports from the Foreign Documents Division (FDD).
    - Q information reports.
    - FDD translations.
14. Air Defense Systems:
    - Air Defense Command and Coordination System.
    - Airborne Target Acquisition and Fire Control System.
    - Chaparral Missile System.
    - Hawk Guided Missile System.
    - Patriot Air Defense Missile System.
15. Missile Systems and Munitions:
    - Honest John Missile System.
    - Pershing Guided Missile Systems.
    - Dragon Guided Missile System.
    - TOW Heavy Antitank Weapon System.
    - Terminally Guided Warhead for Multiple Launch Rocket System.
16. Military Equipment and Technology:
    - Electromagnetic propulsion technology.
    - Ground laser designators.
    - Space weapons concepts.
    - Armor materials concepts and designs.
17. Naval Submarine Operations:
    - Diesel submarine operations and technology.
    - Nuclear-powered submarines.
    - Sound Surveillance System (SOSUS) data.
    - Mine warfare and countermeasures.
18. Special Access Programs and Covert Operations:
    - Special access programs.
    - Covert intelligence operations and activities.
19. Intelligence Collection and Assessment:
    - U.S. intelligence collection and assessment capabilities.
    - Information on technical systems for intelligence collection.
20. Nuclear Programs and Facilities:
    - U.S. nuclear programs and facilities.
    - Foreign nuclear programs, facilities, and intentions.
21. CIA Contracts and Relationships:
    - Contractual relationships revealing CIA interests and expertise.
22. Technical Intelligence:
    - Information on research, development, and engineering for national security.
    - Technical systems for collection and production of intelligence.
23. Intelligence Training and Policies:
    - CIA personnel training, hiring, and evaluation policies.
    - Training provided to or by the CIA.
24. Diplomatic and Economic Intelligence:
    - Diplomatic or economic activities affecting national security.
    - Information affecting U.S. plans to meet diplomatic contingencies.
25. Counterintelligence and Espionage:
    - Counterintelligence activities and special operations.
    - Information revealing covert relationships with foreign governments.
26. Military Operations and Special Activities:
    - Information concerning military operations, including plans, tactics, and techniques.
    - Special activities, such as covert operations and clandestine missions.
    - Tactical information related to psychological operations, unconventional warfare, and special forces.
    - Personnel assigned to or engaged in these activities.
27. Military Operations and Special Activities:
    - Information concerning military operations, including plans, tactics, and techniques.
    - Special activities, such as covert operations and clandestine missions.
    - Tactical information related to psychological operations, unconventional warfare, and special forces.
    - Personnel assigned to or engaged in these activities.
28. Chemical and Biological Warfare:
    - Research, development, test, and evaluation (RDT&E) of chemical and biological weapons.
    - Specific identification of chemical and biological agents and munitions.
    - Plans and strategies related to chemical and biological warfare.
    - Information regarding defensive systems against chemical and biological attacks.
    - Vulnerability assessments related to chemical or biological warfare.
29. Surveillance and Reconnaissance:
    - Capabilities, limitations, and technologies used in surveillance and reconnaissance.
    - Data collection methods, including aerial reconnaissance and ground surveillance.
    - Analysis techniques for interpreting surveillance data.
    - Intelligence gathering activities, including electronic surveillance and imagery analysis.
    - Information pertaining to surveillance operations and reconnaissance missions.
"""
class RedactLabelling:

    def __init__(self, systemArgs) -> None:
        if "ner" in systemArgs:
            self.already_redaction_dataset = f'./dataset/success/redacted_under_25_years_ner.jsonl'
        elif "whitepaper" in systemArgs:
            self.already_redaction_dataset = f'./dataset/success/redacted_under_25_years_whitepaper.jsonl'
        else:
            self.already_redaction_dataset = f'./dataset/success/redacted_under_25_years.jsonl'

    def get_gpt_schema(self, systemArgs):
        if "ner" in systemArgs:
            json_schema= {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "ChatGPT Document Analysis Response",
                "description": "A schema to validate the response format for analyzing document sentences related to sensitive categories.",
                "type": "object",
                "properties": {
                    "document": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sentence": {
                                "type": "string",
                                "description": "The original sentence or text segment."
                            },
                            "entities": {
                                "type": "array",
                                "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "A unique identifier for the entity."
                                    },
                                    "entity_value": {
                                        "type": "string",
                                        "description": "The word or phrase identified as an entity from the sentence."
                                    },
                                    "category": {
                                        "type": "string",
                                        "description": "The category to which the entity has been assigned."
                                    }
                                },
                                "required": [
                                    "id",
                                    "entity_value",
                                    "category"
                                ],
                                "additionalProperties": False
                                },
                                "description": "An array of entities identified in the sentence."
                            },
                            "entity_relationship": {
                                "type": "object",
                                "properties": {
                                    "source": {
                                        "type": "string",
                                        "description": "The ID of the source entity in the relationship."
                                    },
                                    "target": {
                                        "type": "string",
                                        "description": "The ID of the target entity in the relationship."
                                    },
                                    "label": {
                                        "type": "string",
                                        "description": "A descriptive label of the relationship between the source and target entities."
                                    }
                                },
                                "required": ["source", "target", "label"],
                                "additionalProperties": False,
                                "description": "An object describing the relationship between two entities within the context of the sentence, including a descriptive label."
                            }                        
                        },
                        "required": [
                            "sentence",
                            "entities",
                            "entity_relationship"
                        ],
                        "additionalProperties": False
                    }
                    }
                }
            }
        else:
            json_schema= {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Document Redaction",
                "description": "A schema for representing a document with sentences that need to be redacted based on specific categories.",
                "type": "object",
                "properties": {
                    "document": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                            "sentence": { "type": "string" },
                            "redacted": { "type": "boolean" },
                            "redactionCategory": { 
                                    "type": "array",
                                    "items": { "type": "string" }
                                }
                            },
                            "required": ["sentence", "redacted"],
                            "additionalProperties": False
                        },
                        "description": "The document with redactions applied. Each sentence is flagged if it's redacted and includes the category of redaction."
                    },
                    "user_role": {
                        "type": "string",
                        "description": "Role of the user making the request."
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "The maximum number of tokens to generate in the completion."
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Controls randomness in generation. Higher is more random."
                    }
                },
                "required": ["redactedDocument", "user_role", "max_tokens", "temperature"],
                "additionalProperties": False
                }
        return json_schema
    
    def general_template_under_25_years(self, input, systemArgs):
        if "ner" in systemArgs:
            instruction= f"""
            Given a document containing several sentences with specific information related to categories such as Military Plans, Weapons Systems, Military Operations, Date, Military Organisation, Destination, Location, Military Affairs, Foreign Government Data, Intelligence Operations, U.S. Foreign Relations, National Security Science and Technology, Nuclear Security Programs, Security Infrastructure Vulnerabilities, and Weapons of Mass Destruction, perform the following tasks:

            Analyze the Sentences: Carefully read through the provided text and identify words or phrases that pertain to the specified sensitive categories. Focus on extracting these entities without altering the original text.

            Categorize the Entities: For each identified entity, assign it to the appropriate category or categories from the list provided (Military Affairs, Foreign Government Data, etc.). Make sure to accurately reflect the context and significance of each entity.

            Describe Entity Relationships: For sentences that contain multiple entities, describe the relationship between these entities, analyze how these entities are related within the context of the sentence.
            Clearly define the relationship by specifying a source entity and a target entity, and provide a descriptive label that encapsulates the nature of their relationship.

            Generate JSON Response: Structure your findings in a JSON format with the following properties for each sentence or relevant text segment:

            sentence: The original sentence or text segment.
            entities: An array of objects, each representing an identified entity. Each object should include:
                - id: A unique identifier for the entity (you can generate a UUID or a simple incremental ID).
                - entity_value: The exact word or phrase identified as an entity from the sentence.
                - category: The category to which the entity has been assigned.
            entity_relationship: An entity_relationship object with source, target, and label properties to describe the relationship between entities.
            Your output should be a JSON format, where each object represents a sentence or text segment analyzed according to these instructions

            The sentence is:
            `
            {input}
            `
            """
        elif "whitepaper" in systemArgs:
            instruction= f"""
            I have a document divided into an array of sentences, which contains sensitive information. I need to identify and redact confidential information based on specific classification categories. The categories include
            {whitepaper_categories}
            
            Please review each sentence in the document and apply redaction where necessary. The document is as follows:
            `
            {input}
            `

            Please rewrite the document, with redactions appropriately applied to sentences that fall under these categories
            """
        else:
            instruction= f"""
            I have a document divided into an array of sentences, which contains sensitive information. I need to identify and redact confidential information based on specific classification categories. The categories include
            Military Affairs: Includes any information on military strategies, weapon systems, or operational tactics.
            Foreign Government Data: Pertains to any sensitive information regarding foreign governments.
            Intelligence Operations: Encompasses details of intelligence activities (covert or otherwise), sources, methods, and cryptology.
            U.S. Foreign Relations: Relates to the United States' foreign affairs, including activities and confidential sources.
            National Security Science and Technology: Covers scientific, technological, or economic information that is crucial for national security.
            Nuclear Security Programs: Involves information about U.S. Government initiatives for protecting nuclear materials and facilities.
            Security Infrastructure Vulnerabilities: Addresses potential weaknesses or strengths of systems, structures, projects, or services critical for national security.
            Weapons of Mass Destruction: Concerns any details related to the development, production, or deployment of weapons of mass destruction.
            
            Please review each sentence in the document and apply redaction where necessary. The document is as follows:
            `
            {input}
            `

            Please rewrite the document, with redactions appropriately applied to sentences that fall under these categories
            """
        return instruction
    
    def general_template_over_25_years(self, input, systemArgs):
        if "ner" in systemArgs:
            pass
        else:
            instruction= f"""
            Below i have a top secret document in an array of sentences. I need to redact some of the confidential information from the document based on the classification categories. The categories are 
            Confidential Sources and Methods: Protects the identity of confidential human or nonhuman intelligence sources, relationships with foreign intelligence services, and the effectiveness of current or developing intelligence methods.
            WMD Development Information: Safeguards details that could aid in creating, producing, or utilizing weapons of mass destruction.
            Cryptologic Security: Preserves the secrecy of U.S. cryptologic systems and activities to prevent their compromise.
            Advanced Technology in Weapon Systems: Ensures that state-of-the-art technology in U.S. weaponry remains undisclosed to safeguard its strategic advantage.
            U.S. Military War Plans: Conceals active U.S. military war plans, including operational and tactical elements from prior plans still in effect.
            Diplomatic Relations and Foreign Government Data: Prevents the disclosure of information that could severely damage U.S.-foreign relations or impede U.S. diplomatic efforts.
            Protection of National Leaders: Ensures the security and effectiveness of measures to protect the President, Vice President, and other key individuals in the interest of national security.
            National Security Emergency Preparedness: Protects current plans and vulnerabilities in systems or infrastructures crucial for national security and emergency response.
            Legal and International Compliance: Adheres to statutes, treaties, and international agreements that restrict the declassification of certain information, even after 25 years.
            
            The document is 
            `
            {input}
            `

            Rewrite the same document in array format by Highlighting the same sentences to redact by adding [redact] to the begining and [/redact] to the end. 
            Please provide the response in JSON format and assign sentences in a property called document
            """
        return instruction

    def gpt4_response(self, instruction, systemArgs):        
        response= None
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "system", "content": 'You are a text redaction finder for a document'},
                            {"role": "user", "content": instruction}              
                ],
                    functions=[{"name": "getSentenceWithTextRedaction", "parameters": self.get_gpt_schema(systemArgs)}],
                    function_call={"name": "getSentenceWithTextRedaction"},
                max_tokens=4096)     
            # content= response.choices[0].message.content
        except openai.error.APIError as e:
            if e.code != 502:
                time.sleep(5)
                # If the error is not a 502, re-raise it as it might be a different issue
                self.gpt4_response(instruction, systemArgs)
        except Exception as e:
            time.sleep(5)
            print(f"An unexpected error occurred: {e}")
            self.gpt4_response(instruction, systemArgs)

            # time.sleep(5)  # Wait before retrying
        return response
    
    def gpt4_response_ner(self, instruction, systemArgs):        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "user", "content": instruction}            
                ],
                    functions=[{"name": "getNer", "parameters": self.get_gpt_schema(systemArgs)}],
                    function_call={"name": "getNer"},
                max_tokens=4096) 
            # content= response.choices[0].message.content
        except openai.error.APIError as e:
            if e.code != 502:
                time.sleep(5)
                # If the error is not a 502, re-raise it as it might be a different issue
                self.gpt4_response(instruction, systemArgs)
        except Exception as e:
            time.sleep(5)
            print(f"An unexpected error occurred: {e}")
            self.gpt4_response(instruction, systemArgs)

            # time.sleep(5)  # Wait before retrying
        return response
    
    def num_tokens_from_messages(messages, model="gpt-4-1106-preview"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-4-1106-preview":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def save_to_jsonl(self, dataset, file_path):
        with open(file_path, 'w') as file:
            for sample in dataset:
                json_line = json.dumps(sample)
                file.write(json_line + '\n')
        print("Dataset created successfully!!")
    
    def get_last_25_years_doc(self, df):
        df['pubdate'] = pd.to_datetime(df['pubdate'])
        cutoff_date = datetime.now() - timedelta(days=25*365)
        cutoff_date= cutoff_date.strftime("%Y-%m-%d")
        filtered_df = df[df['pubdate'] >= cutoff_date]
        return filtered_df

    def get_over_25_years_doc(self, df):
        df['pubdate'] = pd.to_datetime(df['pubdate'])
        cutoff_date = datetime.now() - timedelta(days=25*365)
        cutoff_date= cutoff_date.strftime("%Y-%m-%d")
        filtered_df = df[df['pubdate'] < cutoff_date]
        return filtered_df

    def redact_labelling(self, systemArgs):
        if "<25" in systemArgs or len(argumentList)==0:
            if "ner" in systemArgs:
                redacted_dataset_file= "./dataset/redacted_under_25_years_ner.jsonl"
            elif "whitepaper" in systemArgs:
                redacted_dataset_file= "./dataset/redacted_under_25_years_whitepaper.jsonl"
            else:
                redacted_dataset_file= "./dataset/redacted_under_25_years.jsonl"
        if ">25" in systemArgs:
            if "ner" in systemArgs:
                redacted_dataset_file= "./dataset/redacted_over_25_years_ner.jsonl"
            elif "whitepaper" in systemArgs:
                redacted_dataset_file= "./dataset/redacted_over_25_years_whitepaper.jsonl"
            else:
                redacted_dataset_file= "./dataset/redacted_over_25_years.jsonl"

        csv_file_path = "./dataset/from_matt_af_quantumventura.csv"
        raw_df= pd.read_csv(csv_file_path)   
        df= raw_df.drop("sanitized", axis=1)
        
        if "<25" in systemArgs or len(argumentList)==0:         
            df= self.get_last_25_years_doc(df)
        if ">25" in systemArgs:
            df= self.get_over_25_years_doc(df)
            # 2010090102536
        # df= df[df['id']== 2009030100726]
        dataset= []
        skipped_records= [2000070101892, 2006070101929, 2010030100744, 
                          2010070101914, 2005030100677, 2009050101359, 
                          2010030100730, 2011070101949, 2007030100690, 
                          2007030100688, 2005070101905,2001030100621,
                          2006010100101,1999070101903,1999070101898]
        already_redacted_ids= skipped_records
        with open(self.already_redaction_dataset, 'r') as already_redacted_file:
            for line in already_redacted_file:  
                json_object = json.loads(line)
                already_redacted_ids.append(json_object['id'])
        with open(redacted_dataset_file, 'w') as redacted_file:
            # try:
            for index, row in df.iterrows():                
                ignore_records= already_redacted_ids
                if row["id"] not in ignore_records:
                    print("Processing the record id ", row["id"])
                    document= row["body"]
                    sentences = sent_tokenize(document) #convert documents into sentences   
                    if "<25" in systemArgs or len(argumentList)==0:         
                        instruction= self.general_template_under_25_years(sentences, systemArgs)
                    if ">25" in systemArgs:
                        instruction= self.general_template_over_25_years(sentences, systemArgs)
                    
                    if "ner" in systemArgs:
                        response= self.gpt4_response_ner(instruction, systemArgs)
                    else:
                        response= self.gpt4_response(instruction, systemArgs)
                    if response is None:
                        print(f"Skipping {row['id']} due to gpt error")
                        continue
                    if response['choices'][0]['finish_reason'] == 'length':
                        print(f"Record id {row['id']} is skipped due to token limit, Input prompt token size is {response['usage']['prompt_tokens']}")
                        continue
                    response= response.choices[0].message.function_call.arguments
                    # response= response.strip()     
                    response= json.loads(response)
                    redacted_sample= {
                        "id": row["id"],
                        "date": row["date"] if row["date"] is np.nan or row["date"] is None else datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S%z").strftime("%Y-%m-%d"),
                        "title": row["title"],
                        "classification": row["classification"],
                        "handling": row["handling"],
                        "pubdate": row["pubdate"].strftime("%Y-%m-%d"),
                        "publisher": row["publisher"],
                        "body": response["document"]
                    }
                    # dataset.append(redacted_sample)
                    json_line = json.dumps(redacted_sample)
                    redacted_file.write(json_line + '\n')    
    
    def get_gpt4_entity_schema(self):
        json_schema= {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Entity and Categories Response",
            "description": "A schema to validate the response containing entities with their types and categories.",
            "type": "object",
            "properties": {
                "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                    "text": {
                        "type": "string"
                    },
                    "type": {
                        "type": "string"
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                        "type": "string"
                        },
                        "minItems": 1
                    }
                    },
                    "required": ["text", "type", "categories"],
                    "additionalProperties": False
                }
                }
            },
            "required": ["entities"],
            "additionalProperties": False
        }
        return json_schema
    
    def gpt4_entity_log_analysis_response(self, instruction):
        response= None
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[
                            {"role": "user", "content": instruction}              
                        ],
                    functions=[{"name": "getNer", "parameters": self.get_gpt4_entity_schema()}],
                    function_call={"name": "getNer"},
                max_tokens=4096)
            # content= response.choices[0].message.content
        except openai.error.APIError as e:
            if e.code != 502:
                time.sleep(5)
                # If the error is not a 502, re-raise it as it might be a different issue
                self.gpt4_entity_log_analysis_response(instruction)
        except Exception as e:
            time.sleep(5)
            print(f"An unexpected error occurred: {e}")
            self.gpt4_entity_log_analysis_response(instruction)
        return response

    def af_mdf_log_analysis(self, systemArgs):
        # sheet_names = ['Table 1', 'Table 2', 'Table 3', 'Table 6', 'Table 8','Table 10']
        sheet_names = ['Table 11']
        # sheet_names = ['Table 1']
        df_raw= pd.read_excel("./dataset/af_mdr_request_log/MDRlogsUSAF_2006-2016.xlsx", sheet_name=sheet_names)
        request_log_path= "./dataset/af_mdr_request_log/"
        dat_col_labels= ["DATE\nRECEIVED", "DATE RECEIVED", "FY 13 DATE RECEIVED"]
        remove_na_columns= ["SUBJECT"]
        os.makedirs(request_log_path, exist_ok=True)
        # Iterate over the entities
        for sheet in sheet_names:
            df = df_raw[sheet]
            matching_date_strings = set(dat_col_labels).intersection(set(df.columns)) 
            date_column_label= None
            if list(matching_date_strings):
                date_column_label = list(matching_date_strings)[0]
                remove_na_columns.append(date_column_label)
            # df[date_column_label] = pd.to_datetime(df[date_column_label], format='%d-%b-%y', errors='coerce') #Temp
            df = df.dropna(subset= remove_na_columns)
            # today = pd.to_datetime('today') #Temp
            # Calculate the date for 2 years ago from today
            # two_years_ago = today - timedelta(days=365*2) #Temp
            # Filter rows where the date is within the last 2 years
            # df = df[df[date_column_label] > two_years_ago] #Temp
            # Initialize new column
            df['entities'] = None
            dataset= []
            for index, row in df.iterrows():
                print(f"Prcessing the subject {row['SUBJECT']} at {sheet}")
                instruction=f"""           
                Given the sentence '{row['SUBJECT']}', 
                identify all entities and categorize them according to the following categories: 
                Military Plans, Weapons Systems, Military Operations, Date, Military Organisation, Destination, 
                Location, Military Affairs, Foreign Government Data, Intelligence Operations, U.S. Foreign Relations, 
                National Security Science and Technology, Nuclear Security Programs, Security Infrastructure Vulnerabilities, and Weapons of Mass Destruction. 
                Provide the output in JSON format, listing each entity with its type and matched categories         
                """
                response= self.gpt4_entity_log_analysis_response(instruction)
                if response is None:
                    print(f"Skipping {row['SUBJECT']} at {sheet}")
                    continue
                if response['choices'][0]['finish_reason'] == 'length':
                    print(f"Subject {row['SUBJECT']} is skipped due to token limit, Input prompt token size is {response['usage']['prompt_tokens']}")
                    continue
                response= response.choices[0].message.function_call.arguments
                # response= response.strip()     
                response= json.loads(response)
                df.at[index, 'entities'] = response["entities"]
                row["entities"]= response["entities"]
                dataset.append(row)
            # df.to_csv(os.path.join(request_log_path, sheet+".csv"))
            df.to_excel(os.path.join(request_log_path, "MDRlogsUSAF_"+sheet+".xlsx"), index=False, engine='openpyxl')
            # self.save_to_jsonl(dataset, os.path.join(request_log_path, "af_mdr_request_log_"+sheet+".jsonl"))
        print("All data processed and saved in jsonl and csv file")

            # print(f"{sheet+".csv"} Processed")
    

    def run(self, systemArgs):
        if "sentence_redacting" in systemArgs:
            self.redact_labelling(systemArgs)
        elif "mdf_log_analysis" in systemArgs:
            self.af_mdf_log_analysis(systemArgs)
        # self.save_to_jsonl(dataset, redacted_dataset_file)
        # except Exception as ex:
        #     self.save_to_jsonl(dataset, redacted_dataset_error_file)

import sys
argumentList = sys.argv[1:]
RedactLabelling(argumentList).run(argumentList)


#time python dataprep_using_gpt.py sentence_redacting "<25" whitepaper