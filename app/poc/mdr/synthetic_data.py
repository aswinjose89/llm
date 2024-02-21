import pandas as pd

from DataSynthesizer.DataDescriber import DataDescriber
from DataSynthesizer.DataGenerator import DataGenerator
from DataSynthesizer.ModelInspector import ModelInspector
from DataSynthesizer.lib.utils import read_json_file, display_bayesian_network


def data_synthesizer():
    #user-defined parameteres
    input_data_path = "./dataset/adult_ssn.csv"
    description_file = f'./dataset/description.json'
    synthetic_data_path = f'./dataset/sythetic_data.csv'


    # An attribute is categorical if its domain size is less than this threshold.
    # Here modify the threshold to adapt to the domain size of "education" (which is 14 in input dataset).
    threshold_value = 20 

    # Number of tuples generated in synthetic dataset.
    num_tuples_to_generate = 52561


    import pdb;pdb.set_trace()
    #DataDescriber
    describer = DataDescriber(category_threshold=threshold_value)
    describer.describe_dataset_in_random_mode(input_data_path)
    describer.save_dataset_description_to_file(description_file)

    #generate synthetic dataset
    generator = DataGenerator()
    generator.generate_dataset_in_random_mode(num_tuples_to_generate, description_file)
    generator.save_synthetic_data(synthetic_data_path)


    # compare the statistics of input and sythetic data (optional)

    # Read both datasets using Pandas.
    input_df = pd.read_csv(input_data_path, skipinitialspace=True)
    synthetic_df = pd.read_csv(synthetic_data_path)
    # Read attribute description from the dataset description file.
    attribute_description = read_json_file(description_file)['attribute_description']

    inspector = ModelInspector(input_df, synthetic_df, attribute_description)


    for attribute in synthetic_df.columns:
        inspector.compare_histograms(attribute)



from sdv.datasets.demo import download_demo
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.lite import SingleTablePreset
def sdv():
    csv_file_path = "./dataset/from_matt_af_quantumventura.csv"
    real_data= pd.read_csv(csv_file_path)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)
    python_dict = metadata.to_dict()
    # metadata.visualize(
    #     show_table_details='summarized',
    #     output_filepath='my_metadata.png'
    # )

    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(real_data)


    synthetic_data = synthesizer.sample(num_rows=600)
    op_csv_path= './dataset/synthetic_data.csv'
    synthetic_data.to_csv(op_csv_path, index=False)
    print(f"Synthetic CSV file '{op_csv_path}' created successfully.")



sdv()