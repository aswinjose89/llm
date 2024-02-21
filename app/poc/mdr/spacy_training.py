
import spacy, json
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans

def test():
    
    nlp = spacy.load("en_core_web_lg")

    doc = nlp("Donad Trump was President of USA")

    import json
    # https://www.kaggle.com/datasets/finalepoch/medical-ner 
    with open('./dataset/corona2.json', 'r') as f:
        data = json.load(f)
        

    training_data = []
    for example in data['examples']:
        temp_dict = {}
        temp_dict['text'] = example['content']
        temp_dict['entities'] = []
        for annotation in example['annotations']:
            start = annotation['start']
            end = annotation['end']
            label = annotation['tag_name'].upper()
            temp_dict['entities'].append((start, end, label))
        training_data.append(temp_dict)
    
    print(training_data[0])

    import pdb;pdb.set_trace()



    nlp = spacy.blank("en") # load a new spacy model
    doc_bin = DocBin()


    for training_example in tqdm(training_data): 
        text = training_example['text']
        labels = training_example['entities']
        doc = nlp.make_doc(text) 
        ents = []
        for start, end, label in labels:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        filtered_ents = filter_spans(ents)
        doc.ents = filtered_ents 
        doc_bin.add(doc)
    import pdb;pdb.set_trace()
    doc_bin.to_disk("train.spacy") 


class SpacyTraining:

    def find_word_indices(self, sentence, word):
        start_index = sentence.find(word)
        if start_index != -1:  # Word found
            end_index = start_index + len(word) - 1
            return start_index, end_index
        else:
            return -1, -1  # Word not found

    def data_prep(self):
        # dataset= [
        #      {
        #           "sentence":"",
        #           "entities": [
        #                {
        #                     "entity_value":"",
        #                     "relation": "",
        #                     "start":"",
        #                     "end": ""
        #                }
        #           ]
        #      }
        # ]
        dataset= []
        entity_file_path = f'./dataset/manual_ner_gpt.json'
        with open(entity_file_path, 'r') as entity_file:                
                json_string = entity_file.read()                
                json_object = json.loads(json_string)
                for sentences in json_object:
                    for sentence in sentences["sentences"]:                        
                        sentence_obj={}
                        sentence_obj["sentence"]= sentence["sentence"]
                        sentence_obj["entities"]= []
                        for entity in sentence["entities"]:
                            entity_obj= {
                                "entity_value":entity["entity"],
                                "relation": entity["relation"]                                
                            }
                            start_index, end_index= self.find_word_indices(sentence["sentence"], entity["entity"])
                            if start_index>0 and end_index>0:
                                entity_obj["start_index"]= start_index
                                entity_obj["end_index"]= end_index+1
                                sentence_obj["entities"].append(entity_obj)
                            else:
                                print(f"Index not found for entity {entity['entity']} at {sentence['sentence']}")
                        dataset.append(sentence_obj)
        # Specify the file name
        file_name = './dataset/spacy_dataset.json'
        # Write to file
        with open(file_name, 'w') as file:
            json.dump(dataset, file, indent=4)

    def train(self):
        spacy_dataset_path = f'./dataset/spacy_dataset.json'
        with open(spacy_dataset_path, 'r') as file: 
            json_string = file.read()                
            spacy_dataset = json.loads(json_string)

        nlp = spacy.blank("en") # load a new spacy model
        doc_bin = DocBin()
        for data in tqdm(spacy_dataset): 
            text = data['sentence']
            entities = data['entities']
            doc = nlp.make_doc(text) 
            ents = []
            for obj in entities:
                span = doc.char_span(obj["start_index"], obj["end_index"], label=obj["relation"], alignment_mode="contract")
                if span is None:
                    print("Skipping entity")
                else:
                    ents.append(span)
            filtered_ents = filter_spans(ents)
            doc.ents = filtered_ents 
            doc_bin.add(doc)
        doc_bin.to_disk("train.spacy")
    
    def inference(self):        
        nlp_ner = spacy.load("model-best")
        doc = nlp_ner("e. Arrangements for the trip by Army Rescue Boat 403 were made by\r\n\nCommander MaoCollum, E, ACV.")
        colors = {"VEHICLE": "#F67DE3", "COORDINATOR": "#7DF6D9", "UNIT":"#a6e22d"}
        options = {"colors": colors}
        spacy.displacy.render(doc, style="ent", options= options)

SpacyTraining().inference()