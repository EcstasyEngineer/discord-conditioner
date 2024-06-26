import re
import sys
import argparse

def load_verb_conjugations(filepath):
    verb_templates_1ps = {}
    verb_templates_1pp = {}
    verb_templates_2ps = {}
    verb_templates_3ps = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            conjugations = line.strip().split('|')
            if len(conjugations) == 2: # format is "go|goes"
                verb_templates_1ps[conjugations[0]] = line.strip() # I go
                verb_templates_1pp[conjugations[1]] = line.strip() # we go
                verb_templates_2ps[conjugations[0]] = line.strip() # you go
                verb_templates_3ps[conjugations[1]] = line.strip() # she goes
            elif len(conjugations) == 4:  #format is "am|are|is|is"
                verb_templates_1ps[conjugations[0]] = line.strip() # I am
                verb_templates_1pp[conjugations[1]] = line.strip() # we are
                verb_templates_2ps[conjugations[2]] = line.strip() # you are
                verb_templates_3ps[conjugations[3]] = line.strip() # she is
    return verb_templates_1ps, verb_templates_1pp, verb_templates_2ps, verb_templates_3ps

def process_file_to_template(input_file_path, output_file_path, subject_name, dominant_name):
    # mapping rules:
    # named subject  - 3ps -> 3ps (subject)
    # named dominant - 3ps -> 3ps (dominant)
    # 1ps -> 1ps (subject)
    # 1pp -> 1ps (subject)
    # 2ps -> 2ps (dominant)
    # 3ps -> 2ps (dominant)
    patterns = {
        re.compile(rf'\b{subject_name}\b', re.IGNORECASE): '{subject_name}',  # subject name (3rd person)
        re.compile(rf'\b{dominant_name}\b', re.IGNORECASE): '{dominant_name}', # dominant name (3nd person)
        re.compile(r'\bi(\'|\’)m\b', re.IGNORECASE): '{subject_subjective} am', # no conjunctions
        re.compile(r'\bwe(\'|\’)re\b', re.IGNORECASE): '{subject_subjective} am', # no conjunctions (also convert to 1ps)
        re.compile(r'\bi\b', re.IGNORECASE): '{subject_subjective}',  # "I" as subjective
        re.compile(r'\bwe\b', re.IGNORECASE): '{subject_subjective}',  # "we" as subject
        re.compile(r'\bmy|mine\b', re.IGNORECASE): '{subject_possessive}',
        re.compile(r'\bme\b', re.IGNORECASE): '{subject_objective}',
        re.compile(r'\bus\b', re.IGNORECASE): '{subject_objective}',  # "us" as objective
        re.compile(r'\byou\'re\b', re.IGNORECASE): '{dominant_subjective} are',  # no conjunctions
        re.compile(r'\bthey\'re\b', re.IGNORECASE): '{dominant_subjective} are',  # no conjunctions
        re.compile(r'\byou\b', re.IGNORECASE): '{dominant_subjective}',  # warning, "you" can be subjective as well
        re.compile(r'\bshe\b', re.IGNORECASE): '{dominant_subjective}',  # "she" as subjective
        re.compile(r'\bhe\b', re.IGNORECASE): '{dominant_subjective}',  # "he" as subjective
        re.compile(r'\bhim\b', re.IGNORECASE): '{dominant_objective}',
        re.compile(r'\bthem\b', re.IGNORECASE): '{dominant_objective}',  # "them" as objective
        re.compile(r'\byour|yours\b', re.IGNORECASE): '{dominant_possessive}',
        re.compile(r'\bhis\b', re.IGNORECASE): '{dominant_possessive}',
        re.compile(r'\bher|hers\b', re.IGNORECASE): '{dominant_possessive}', # warning, "her" can be objective as well
        re.compile(r'\btheir|theirs\b', re.IGNORECASE): '{dominant_possessive}',
    }

    try:
        
        verbs_1ps,verbs_1pp,verbs_2ps,verbs_3ps = load_verb_conjugations('utils/verb_conjugations.txt')

        with open(input_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                # search line for \byou\b or \bher\b
                has_ambiguous = False
                matches = re.findall(r'\b(you|her)\b', line, re.IGNORECASE)
                for match in matches:
                    if match[0].lower() == 'you':
                        print("Warning: 'you' is ambiguous. Please verify {dominant_subjective}")
                        print("original: ", line)
                        has_ambiguous = True
                    if match[0].lower() == 'her':
                        print("Warning: 'her' is ambiguous. Please verify {dominant_possessive}")
                        print("original: ", line)
                        has_ambiguous = True
                
                # Replace all patterns in the line {dominant}, {subject}, {subject_possessive}, etc.
                for pattern, replacement in patterns.items():
                    line = pattern.sub(replacement, line)

                matches = re.findall(r'\{subject_name\}\s+(\w+\b(?:\'\w+)?)', line, re.IGNORECASE)
                for match in matches:
                    if match[1].lower() in verbs_3ps:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_3ps[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                        
                matches = re.findall(r'\{dominant_name\}\s+(\w+\b(?:\'\w+)?)', line, re.IGNORECASE)
                for match in matches:
                    if match[1].lower() in verbs_3ps:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_2ps[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                        
                matches = re.findall(r'\{subject(_subjective)?\}\s+(\w+\b(?:\'\w+)?)', line, re.IGNORECASE)
                for match in matches:
                    if match[1].lower() in verbs_1ps:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_1ps[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                    if match[1].lower() in verbs_1pp:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_1pp[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                        
                matches = re.findall(r'\{dominant(_subjective)\}\s+(\w+\b(?:\'\w+)?)', line, re.IGNORECASE)
                for match in matches:
                    if match[1].lower() in verbs_2ps:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_2ps[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                    if match[1].lower() in verbs_3ps:
                        pattern = r'\b' + re.escape(match[1]) + r'\b'
                        replacement = "[" + verbs_3ps[match[1].lower()] + "]"
                        line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
                        
                if has_ambiguous:
                    print("converted: ", line)
                        
                file.write(line)
        
        print(f"File processed successfully. Output saved to {output_file_path}")
    
    except FileNotFoundError:
        print("Error: The file specified does not exist." + str(sys.exc_info()[1]))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    def main():
        parser = argparse.ArgumentParser(description='Convert lines in a file based on subject and dominant names.')
        parser.add_argument('-i', '--input', help='Input file path', default='utils/preconverted/broken.txt')
        parser.add_argument('-o', '--output', help='Output file path', default='utils/input_converted.txt')
        parser.add_argument('-sp', '--subject-perspective', help='Subject perspective (1ps, 1pp)', default='1ps')
        parser.add_argument('-sn', '--subject-name', help='Subject name (Bambi, Slave, Toy, Doll, etc)', default='Bambi')
        parser.add_argument('-dp', '--dominant-perspective', help='Dominant perspective (2ps, 3ps)', default='2ps')
        parser.add_argument('-dn', '--dominant-name', help='Dominant name (Master, Mistress, etc)', default='Master')
        args = parser.parse_args()

        if args.output != 'input_converted.txt':
            args.output = re.sub(r'\.\w+$', '_converted.txt', args.input)

        process_file_to_template(args.input, args.output, args.subject_name, args.dominant_name)

    if __name__ == "__main__":
        main()


# Example usage
# python convert_lines.py input.txt output.txt "Master" "Bambi"