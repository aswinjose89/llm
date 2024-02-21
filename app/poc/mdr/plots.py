
import numpy as np, json
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf


class PLOTS:
    def llama_model_loss_plot(self):        
        # Path to your TensorBoard log file
        llama7b_log_file = './llama_results/logs/llama7b/qa/events.out.tfevents.1706626447.saturn.2141365.0'
        llama13b_log_file = './llama_results/logs/llama13b/qa/events.out.tfevents.1706633232.saturn.2177620.0'

        # Extracting the data

        def loss_values(log_file_path):
            training_loss_values = []
            epoch_values = []
            for e in tf.compat.v1.train.summary_iterator(log_file_path):
                for v in e.summary.value:
                    if v.tag == 'train/loss' or v.tag == 'epoch_loss':  # Use your specific tag
                        training_loss_values.append(v.simple_value)
                    if v.tag == 'train/epoch':  # Use your specific tag
                        epoch_values.append(v.simple_value)
            return training_loss_values, epoch_values
        llama7b_training_loss_values, epoch_values= loss_values(llama7b_log_file)
        llama13b_training_loss_values, epoch_values= loss_values(llama13b_log_file)
        # Plotting the data
        # Plotting
        plt.figure(figsize=(18, 12))
        plt.plot(epoch_values[:len(llama7b_training_loss_values)], llama7b_training_loss_values, marker='o', linestyle='-', color='b', label='LLAMA2-7b Training Loss')
        plt.plot(epoch_values[:len(llama13b_training_loss_values)], llama13b_training_loss_values, marker='o', linestyle='-', color='g', label='LLAMA2-13b Training Loss')
        plt.title('Training Loss per Epoch - 0.0002 lr')
        plt.xlabel('Epoch')
        plt.ylabel('Training Loss')
        plt.xticks(epoch_values[:len(llama7b_training_loss_values)])  # Ensure that each epoch is marked on the x-axis
        plt.xticks(rotation=55)
        plt.legend(ncol=1)
        plt.grid(True)
        # Save the plot to a file
        plt.savefig('./llm_results/plots/llama_qa_training_loss_plot.png')  # Saves the plot as a PNG file
        plt.show()
    
    def tsne(self):
        from transformers import AutoTokenizer, AutoModel

        model_name = "llama_results/llama-2-7b-chat-mdr-qa"  # This is a placeholder; use the actual model name or path
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        entity_values= []
        data_entity_path= "./dataset/success/redacted_under_25_years_ner.jsonl"
        with open(data_entity_path, 'r') as data_entity:
            for line in data_entity: 
                json_object = json.loads(line)
                doc= json_object["body"]
                if json_object["id"] in [2007050101302]:
                    continue
                # if json_object["id"] in [2010090102536, 2010010100055]:
                for entities in doc:
                    if "entities" in entities and isinstance(entities["entities"], list):
                        for entity in entities["entities"]:
                            if "entity_value" in entity:
                                entity_values.append(entity["entity_value"])
        words= entity_values
        # words = ["American military personnel", "7 Light machine guns", "61 Rifles, cal. 6.5", "Ammunition: Caliber 6.5", "Sighting Equipment", "NATIONAL ARCHIVES"]
        inputs = tokenizer(words, return_tensors="pt", padding=True, truncation=True, return_attention_mask=False)
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.detach().numpy()  # Assuming you're working with PyTorch

        def tsne_plot():
            from sklearn.manifold import TSNE
            import matplotlib.pyplot as plt

            # Assuming embeddings is a (N, D) matrix where N is the number of words
            num_words = embeddings.shape[0]  # Number of words you're visualizing
            perplexity_value = min(30, num_words - 1)  # Adjust perplexity here, ensuring it's less than num_words


            # Assuming embeddings is a (N, D) matrix where N is the number of words and D is the embedding dimension
            tsne = TSNE(n_components=2, perplexity=perplexity_value, n_iter=2500, random_state=23)
            reduced_embeddings = tsne.fit_transform(embeddings.mean(axis=1))  # Assuming mean pooling or similar


            # Plot
            plt.figure(figsize=(18, 12))
            plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], alpha=0.5)
            # for i, word in enumerate(words):
            #     plt.annotate(word, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]))
            # Enhancements
            plt.title('t-SNE Visualization of Word Embeddings', fontsize=16, fontweight='bold')
            plt.xlabel('t-SNE Axis 1', fontsize=14)
            plt.ylabel('t-SNE Axis 2', fontsize=14)
            plt.grid(True, which='both', linestyle='--', linewidth=0.5)  # Grid helps in estimating position
            plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

            plt.savefig('./llm_results/plots/llama7b_tsne_plot2.png')  # Saves the plot as a PNG file
            plt.show()
        tsne_plot()
    
    def save_rough_plot(self, precision, recall, f1_score, thresholds, flag, model_name):
        plt.figure(figsize=(18, 12))
        # Plot precision
        plt.plot(thresholds, precision, label='Precision', marker='o')

        # # Plot recall
        plt.plot(thresholds, recall, label='Recall', marker='o')

        # # # Plot F1 score
        plt.plot(thresholds, f1_score, label='F1 Score', marker='o')

        plt.xlabel('Threshold')
        plt.ylabel('Score')
        plt.title('Rough1 Score - Precision, Recall, and F1 Score vs. Threshold', fontsize=16, fontweight='bold')
        # plt.title('Rough1 Score - Recall vs. Threshold', fontsize=16, fontweight='bold')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'./llm_results/plots/{model_name}_{flag}.png')
        plt.show()

    
    def rough_score_plot(self):

        llama7b_qv_df_matrix= pd.read_csv("./dataset_under_25_years_llama7b_qa_test_response.csv")
        # Example data
        thresholds = np.linspace(0, 1, llama7b_qv_df_matrix.shape[0])
        
        precision = llama7b_qv_df_matrix['rouge1_precision']
        recall = llama7b_qv_df_matrix['rouge1_recall']
        f1_score = llama7b_qv_df_matrix['rouge1_f1_score']
        self.save_rough_plot(precision, recall, f1_score, thresholds, "rough1", "llama7b_qa")

    def af_mdr_request_log_plot(self):
        file_path = './dataset/af_mdr_request_log/af_mdr_request_log_report.json'

        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Top 10 Requestors by Number of Requests Starts here
        requestors_data = data['total_request_by_requestors']
        # Sort and select top N requestors for readability, though the data is already prepared as top N.
        top_n_requestors = dict(sorted(requestors_data.items(), key=lambda item: item[1], reverse=True)[:10])
        # Creating the bar plot with counts displayed
        plt.figure(figsize=(10, 8))
        bars = plt.bar(top_n_requestors.keys(), top_n_requestors.values(), color='skyblue')
        plt.title('Top 10 Requestors by Number of Requests', fontweight='bold')
        plt.xlabel('Requestors', fontsize=14)
        plt.ylabel('Number of Requests', fontsize=14)
        plt.xticks(rotation=45, ha='right')

        # Adding the count above each bar
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

        plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
        plt.savefig(f'./llm_results/plots/af_mdr_request_log_requests.png')


        # MDR Request Distribution Plot Starts here
        mdr_stats = {
            'Appeals': data['total_mdr_appeals'],
            'Duplicates': data['total_mdr_duplicates'],    
            'Closed': data['total_closed_request'],
            'Pending': data['total_pending_request']
        }
        # Creating the pie chart with adjusted parameters to avoid overlapping
        plt.figure(figsize=(8, 8))
        plt.pie(mdr_stats.values(), labels=mdr_stats.keys(), autopct='%1.1f%%', startangle=140, 
                colors=['gold', 'lightblue', 'lightgreen', 'lavender', 'orange'], pctdistance=0.85)

        # Draw a circle at the center of pie to make it look like a donut
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.title('MDR Request Distribution')
        plt.tight_layout()
        plt.savefig(f'./llm_results/plots/af_mdr_request_log_requests_distribution.png')


        # Top 10 Category Entries Starts here
        category_entries_data = data['entity_details']['category_entries']
        # Sort and select top N categories for readability
        top_n_categories = dict(sorted(category_entries_data.items(), key=lambda item: item[1], reverse=True)[:10])

        # Creating the bar plot with counts displayed
        plt.figure(figsize=(10, 8))
        bars = plt.bar(top_n_categories.keys(), top_n_categories.values(), color='lightgreen')
        plt.title('Top 10 Category Entries', fontweight='bold')
        plt.xlabel('Categories', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        # Adding the count above each bar
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

        plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
        plt.savefig(f'./llm_results/plots/af_mdr_request_log_top_10_categories.png')
        plt.show()


        # Report Statistics Overview Starts here
        single_value_stats = {
            'Sample Size Before Cleaning': data['sample_size_before_cleaning'],
            'Total Requestors': data['total_requestors'],
            'Total MDR Appeals': data['total_mdr_appeals'],
            'Total MDR Duplicates': data['total_mdr_duplicates'],
            'Total MDR Reference': data['total_mdr_reference'],
            'Total Closed Request': data['total_closed_request'],
            'Total Pending Request': data['total_pending_request'],
            'Last 2 year Pending Request': data['last_2year_pending_requests'],
            'Sample Size After Cleaning': data['sample_size_after_cleaning']
        }
        # Plotting the single-value statistics
        fig, ax = plt.subplots(figsize=(10, 8))
        bars=ax.bar(single_value_stats.keys(), single_value_stats.values(), color='skyblue')
        plt.xticks(rotation=45, ha="right")
        plt.ylabel('Count', fontsize=14)
        plt.title('Report Statistics Overview', fontweight='bold')

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

        plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
        plt.savefig(f'./llm_results/plots/af_mdr_request_log_report_overview.png')
        plt.show()



    def run(self):
        self.rough_score_plot()
        self.af_mdr_request_log_plot()
