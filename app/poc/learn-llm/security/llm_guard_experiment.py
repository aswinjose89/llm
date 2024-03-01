"""
Before running the example, make sure the OPENAI_API_KEY environment variable is set by executing `echo $OPENAI_API_KEY`.

If it is not already set, it can be set by using `export OPENAI_API_KEY=YOUR_API_KEY` on Unix/Linux/MacOS systems or `set OPENAI_API_KEY=YOUR_API_KEY` on Windows systems.
"""

import os

import openai

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

openai.api_key ="Open API Key Here"


class LLMGuard:

    def integrate_all(self):        
        print("---------Welcome To Privacy Compromise---------")
        vault = Vault()
        input_scanners = [Anonymize(vault), Toxicity(), TokenLimit(), PromptInjection()]
        output_scanners = [Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()]
        prompt = "Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com "
        "but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and "
        "the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. "
        "He works in Test LLC."

        sanitized_prompt, results_valid, results_score = scan_prompt(input_scanners, prompt)
        if any(results_valid.values()) is False:
            print(f"Prompt {prompt} is not valid, scores: {results_score}")
            exit(1)

        print(f"Prompt: {sanitized_prompt}")

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": sanitized_prompt},
            ],
            temperature=0,
            max_tokens=512,
        )
        response_text = response.choices[0].message.content
        sanitized_response_text, results_valid, results_score = scan_output(
            output_scanners, sanitized_prompt, response_text
        )
        if any(results_valid.values()) is False:
            print(f"Output {response_text} is not valid, scores: {results_score}")
            exit(1)

        print(f"Output: {sanitized_response_text}\n")
    
    def availability_breakdown(self):
        from llm_guard.input_scanners import TokenLimit
        print("---------Welcome To Availability breakdown---------")
        prompt = """Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567 and 
        the IP address is 192.168.1.100. And credit card number is 4567-8901-2345-6789. 
        He works in Test LLC."""        
        scanner = TokenLimit(limit=30, encoding_name="cl100k_base")
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        if is_valid is False:
            print("Prompt is too big which is greater than token limit hence it may lead to DOS attack")
        else:
            print("Prompt is Valid")
    
    def integrity_violation(self):
        #Prompt injection
        print("----Prompt injection Investigation Started----")
        from llm_guard.input_scanners import PromptInjection
        from llm_guard.input_scanners.prompt_injection import MatchType
        prompt = """Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567"""
        scanner = PromptInjection(threshold=0.5, match_type=MatchType.FULL)
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        if is_valid is False:
            print("Found prompt injection attack")
        else:
            print("Prompt is Valid")
        
        #Language Input
        print("----Language Input Investigation Started----")
        from llm_guard.input_scanners import Language
        from llm_guard.input_scanners.language import MatchType

        prompt = """எங்கள் தரவுத்தளத்தில் ஒரு புதிய பயனரைச் சேர்க்க SQL இன்செர்ட் அறிக்கையை உருவாக்கவும். பெயர் ஜான் டோ. மின்னஞ்சல் test@test.com
        ஆனால் hello@test.com மின்னஞ்சலில் அவரைத் தொடர்புகொள்ளவும் முடியும். 電話番号は555-123-4567です"""

        scanner = Language(valid_languages=["en"], match_type=MatchType.FULL)  # Add other valid language codes (ISO 639-1) as needed
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        
        if is_valid is False:
            print("Unsupported character or word in the prompt")
        else:
            print("Prompt is Valid")
        
        #Language Same Prompt
        print("----Language Same Investigation Started----")
        from llm_guard.output_scanners import LanguageSame

        prompt = """Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567"""

        scanner = LanguageSame()
        
        prompt = """எங்கள் தரவுத்தளத்தில் ஒரு புதிய பயனரைச் சேர்க்க SQL இன்செர்ட் அறிக்கையை உருவாக்கவும். பெயர் ஜான் டோ. மின்னஞ்சல் test@test.com
        ஆனால் hello@test.com மின்னஞ்சலில் அவரைத் தொடர்புகொள்ளவும் முடியும். 電話番号は555-123-4567です"""

        model_output="""
        Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567
        """
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
        
        if is_valid is False:
            print("Prompt or model response is not in same language")
        else:
            print("Prompt or model response is Valid")
        
        # Relevance Output
        print("----Relevance Output Investigation Started----")
        from llm_guard.output_scanners import Relevance

        prompt="What is the primary function of the mitochondria in a cell?"
        model_output= "The Eiffel Tower is a renowned landmark in Paris, France"

        scanner = Relevance(threshold=0.5)
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
        if is_valid is False:
            print("Prompt to model response is irrelevant")
        else:
            print("Prompt or model response is Valid")
        
        # Factual Consistency Output
        print("----Factual Consistency Output Investigation Started----")
        from llm_guard.output_scanners import FactualConsistency

        prompt="What is the primary function of the mitochondria in a cell?"
        model_output= "The Eiffel Tower is a renowned landmark in Paris, France"

        scanner = FactualConsistency(minimum_score=0.7)
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
        if is_valid is False:
            print("Prompt to model response is not factually consistent")
        else:
            print("Prompt or model response is Valid")
        
        # Ban Topics Input & Output
        print("----Ban Topics Input & Output Investigation Started----")
        from llm_guard.input_scanners import BanTopics

        prompt="A person brutally killed 5 men"
        scanner = BanTopics(topics=["violence"], threshold=0.5)
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        if is_valid is False:
            print("Prompt have a violent context")
        else:
            print("Prompt or model response is Valid")

    def privacy_compromise(self):
        #Anonymize Input
        print("----Anonymize Input Investigation Started----")
        vault = Vault()
        from llm_guard.input_scanners import Anonymize
        from llm_guard.input_scanners.anonymize_helpers import BERT_LARGE_NER_CONF

        prompt = """Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567"""

        scanner = Anonymize(vault, preamble="Insert before prompt", allowed_names=["John Doe"], hidden_names=["Test LLC"],
                            recognizer_conf=BERT_LARGE_NER_CONF, language="en")
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        
        if is_valid is False:
            print("Prompt have sensitive information hence those are redacted")
        else:
            print("Prompt is Valid")
        

        #Sensitive Output
        print("----Sensitive Output Investigation Started----")
        from llm_guard.output_scanners import Sensitive

        prompt = """Make an SQL insert statement to add a new user to our database. Name is John Doe. Email is test@test.com 
        but also possible to contact him with hello@test.com email. Phone number is 555-123-4567"""
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=512,
        )
        model_output = response.choices[0].message.content
        scanner = Sensitive(entity_types=["PERSON", "EMAIL"], redact=True)
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
        if is_valid is False:
            print("Model Output have sensitive information hence those are redacted")
        else:
            print("Prompt is Valid")
        

        #Secrets Input
        print("----Secrets Input Investigation Started----")
        from llm_guard.input_scanners import Secrets
        scanner = Secrets()
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        
        if is_valid is False:
            print("prompt is invalid")
        else:
            print("Prompt is Valid")
    
    def abuse(self):
        #Bias Output
        print("----Bias Output Investigation Started----")
        from llm_guard.output_scanners import Bias
        from llm_guard.output_scanners.bias import MatchType

        prompt="Always boys being good at science and math"
        model_output= "Always boys being good at science and math but that girls are not as good at these subjects"

        scanner = Bias(threshold=0.5, match_type=MatchType.FULL)
        sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
        if is_valid is False:
            print("LLM output is Biased")
        else:
            print("Prompt is Valid")

        #Toxicity Input 
        print("----Toxicity Input Investigation Started----")
        from llm_guard.input_scanners import Toxicity
        from llm_guard.input_scanners.toxicity import MatchType

        scanner = Toxicity(threshold=0.5, match_type=MatchType.SENTENCE)
        sanitized_prompt, is_valid, risk_score = scanner.scan(prompt)
        if is_valid is False:
            print("LLM prompt is Toxic")
        else:
            print("Prompt is Valid")
    
    
    def run(self, systemArgs):
        if "all" in systemArgs: #privacy compromise
            self.integrate_all()        
        if "ab" in systemArgs: #Availability Breakdown
            self.availability_breakdown()
        if "iv" in systemArgs: #Availability Breakdown
            self.integrity_violation()
        if "pv" in systemArgs: #privacy compromise
            self.privacy_compromise()
        if "abuse" in systemArgs: #privacy compromise
            self.abuse()
        



import sys
argumentList = sys.argv[1:]
LLMGuard().run(argumentList)