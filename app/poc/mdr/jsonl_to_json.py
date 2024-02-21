
import json


ner_redaction_dataset="./dataset/success/redacted_under_25_years_ner.jsonl"
op_ner_redaction_dataset="./dataset/success/redacted_under_25_years_ner.json"
dataset=[]
with open(ner_redaction_dataset, 'r') as data_entity:
    for line in data_entity: 
        json_object = json.loads(line)
        temp= {
            "id": json_object["id"],
            "date": json_object["date"],
            "title": json_object["title"],
            "publisher": json_object["publisher"],
            "body": json_object["body"]
        }
        dataset.append(temp)

# Write the list of dictionaries to a .json file
with open(op_ner_redaction_dataset, 'w') as json_file:
    json.dump(dataset, json_file, indent=4)