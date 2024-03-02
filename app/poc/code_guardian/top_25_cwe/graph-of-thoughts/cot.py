from sorting.sorting_032 import SortingPrompter, SortingParser, utils
from graph_of_thoughts import controller, operations

# Problem input

to_be_sorted = "[0, 2, 6, 3, 8, 7, 1, 1, 6, 7, 7, 7, 7, 9, 3, 0, 1, 7, 9, 1, 3, 5, 1, 3, 6, 4, 5, 4, 7, 3, 5, 7]"

# Create the Graph of Operations
gop = operations.GraphOfOperations()
gop.append_operation(operations.Generate())
gop.append_operation(operations.Score(scoring_function=utils.num_errors))
gop.append_operation(operations.GroundTruth(utils.test_sorting))

# Configure the Language Model (Assumes config.json is in the current directory with OpenAI API key)
lm = controller.ChatGPT("config.json", model_name="chatgpt")

# Create the Controller
ctrl = controller.Controller(
  lm, 
  gop, 
  SortingPrompter(), 
  SortingParser(),
  # The following dictionary is used to configure the initial thought state
  {
    "original": to_be_sorted,
    "current": "",
    "method": "cot"
  }
)

# Run the Controller and generate the output graph
ctrl.run()
ctrl.output_graph("output_cot.json")