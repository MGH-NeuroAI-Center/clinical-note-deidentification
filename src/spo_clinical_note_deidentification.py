import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
from presidio_analyzer import PatternRecognizer
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer import Pattern
import regex as re



class MRNRecognizer(PatternRecognizer):
    def __init__(self):
        pattern = Pattern(name="MRN (optional colon and space) followed by 5-10 digits", 
                          regex= "\\bMRN:?\\s?\\d{5,10}\\b", 
                          score=0.8)
        super().__init__(supported_entity="MRN_NUMBER", patterns=[pattern])
        

class DateRecognizer(PatternRecognizer):
    def __init__(self):
        pattern = Pattern(name="Date in the format MM/DD/YYYY", 
                          regex= "\\b(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/([0-9]{2}([0-9]{2})?)\\b", 
                          score=0.8)
        super().__init__(supported_entity="DATE_VAL", patterns=[pattern])


blacklist = ['Minimum','Mininimum', 'Muscle Tone', 'Max', 'Maximum', 'Toileting Independent Number of Staff', 'Toileting', 
            'Toileting Hygiene', 'Cues']


def analyze_and_anonymize(text):
    analyzer = AnalyzerEngine()
    analyzer.registry.add_recognizer(MRNRecognizer())
    analyzer.registry.add_recognizer(DateRecognizer())
    anonymizer = AnonymizerEngine()
    blacklist = ['Minimum','Mininimum', 'Muscle Tone', 'Max', 'Maximum', 'Toileting Independent  Number of Staff', 
                 'Toileting Close', 
            'Toileting Hygiene', 'Cues', 'Toileting',
                'Toileting Toileting Hygiene Level of Assistance', 
                'Cues Max', 'Grooming Dependent  X 1', 'Max = Maximal Assist','Intelligible Verbalization  Communication Scale'
                ]
    analyzer_results = analyzer.analyze(text=text, language="en",allow_list = blacklist)
    filtered_results = []

    for result in analyzer_results:
        if result.entity_type == 'PERSON' and result.score >= 0.85:
            filtered_results.append(result)
            print(result.score, text[result.start:result.end])
        elif result.entity_type != 'PERSON' and result.score >= 0.8:
            filtered_results.append(result)
    
#     for result in filtered_results:
#         if result.entity_type == 'PERSON':
#             print(f"Entity type: {result.entity_type}, Start: {result.start}, End: {result.end}, Score: {result.score}")
#             print(f"Text: {text[result.start:result.end]}")


    final_result = anonymizer.anonymize(text=text, analyzer_results=filtered_results)
    return final_result.text


def process_notes_in_csv(csv_file, column_name, function):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Check if the column exists in the DataFrame
    if column_name in df.columns:
        # Apply the function to the column and replace the original column
        df[column_name] = df[column_name].apply(function)
        
        # Save the DataFrame back to the CSV file
        df.to_csv(csv_file, index=False)
        
        print(f"The column '{column_name}' has been successfully anonymized and the CSV file has been updated.")
    else:
        print(f"The column '{column_name}' does not exist in the CSV file.")

# Example to run function:
# process_notes_in_csv(filename, "NOTETXT", analyze_and_anonymize)