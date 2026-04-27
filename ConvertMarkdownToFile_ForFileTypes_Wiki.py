import re
import os
import json
from CodeAnaylisis import ollama_generate

# Define the file where we will save the parsed metadata
OUTPUT_FILENAME = "parsed_metadata.txt"

def parse_header(line: str) -> str | None:
    """
    Detects and extracts the content of a header line.
    
    Uses a regex to look for content enclosed by one or more '=' signs.
    Example matches:
    - ===Title=== -> "Title"
    - =My Header= -> "My Header"
    - ===== Test ===== -> " Test "
    
    Args:
        line: The string line potentially containing a header.
    
    Returns:
        The extracted header title string, or None if no header is found.
    """
    # Regex explanation:
    # ^       : start of the line
    # =+      : one or more '=' characters (the opening delimiter)
    # (.*?)   : Capture group 1: matches any character (.), zero or more times (*), non-greedily (?)
    # =+      : one or more '=' characters (the closing delimiter)
    # $       : end of the line
    
    # Note: We strip leading/trailing whitespace from the captured content
    match = re.search(r"^=+(.*?)=+$", line.strip())
    
    if match:
        # Group 1 holds the actual content between the delimiters
        header_value = match.group(1).strip()
        return header_value
    else:
        return None


def process_data_stream(file_extention: str, file_description: str, high_level_desc: str) -> str:
    """
    Iterates over lines of data, attempts to parse headers, and saves them.
    """
    prompt = f"""
# **The Role and Goal Setting**

    You are acting as a data entry System where you are to look over meta data and assumue what a given file contains based on the file type, 
    your answers should be exactly what is what expect as you are filling in entires in a database.

    # **Input Variables**

    The following three context variables define the scope of the given file:
    1. File Extension = **"{file_extention}"**
    2. Description = **"{file_description}"**
    3. High-Level Purpose = **"{high_level_desc}"**

    You will **NOT** recive the file contents, you are just to base your anlyisis on the above information:

    # **Content Analysis Guidelines**

    1. **Encoding:** State the input data explicitly. 
    2. **Human Readable:** Determine if the content is raw plaintext, or if it is deliberately encoded/obfuscated 
    (e.g., Base64, ROT13, hex dump, etc.). State this explicitly as a "Yes", "No" or "Maybe" Value
    3. **Human Generated:** Is it expected that this type of file is produced by a human (or a LLM) or if it is metadata which is machine written machine, answer as **Yes**, **No**, **Maybe**.
    4. **Suggested Role:** Based on the above, suggest a role that someone revewing this file would be best suited to have, for example if it is source code than a sinor software engineer would be fit.
    If it is a log file then a system administrator would be best, if it is a config file then a devops engineer would be best, if it is a data file then a data scientist would be best, 
    if it is a document then a technical writer would be best, if it is an image then a graphic designer would be best, if it is an audio file then an audio engineer would be best, 
    if it is a video file then a video editor would be best, if it is a tex file then a researcher would be best.
    If you are unsure of the role, you can say "Unknown" unless you do not recommend this file to be reviewed when say "None" but try to be specific when possible.


    # **The Final Output (Comma-Separated)**
    You must return a single line of text that adheres strictly to the following structure. four values represent your analysis.

    ## **Format:**
    
    ### Schema:
    "<encoding>", "<Yes|No|Maybe>",  "<Yes|No|Maybe>", "<role>"    
    ### Example Output:
    - `ASCII", "Maybe", "No", "System Administrator"`
    - `Binary", "No", "No", "Machine Metadata"`

    # **Rules**
    - The format must be used exactly
    - No text may be before or after the output
    - The field must be in the correct order
    - No new Feilds may be added
    - If you are unable to do perform this function you are to return "ERROR" at the start of the prompt followed by the issue in <3 sentances
    - Being returning error when you are unsure is better than being incorrect, if you are not sure send a ERROR.
    - Do not Talk to the user, do not explain your reasoning, do not give any information other than the output, 
    if you are unsure of the output return an error with a explanation of why you are unsure.

    # **Input Variables (Reminder)**

    The following three context variables define the scope of the given file:
    1. File Extension = **"{file_extention}"**
    2. Description = **"{file_description}"**
    3. High-Level Purpose = **"{high_level_desc}"**

    """

    #print(prompt)

    # Send to an ollma model for processing, the model will return a single line of text to be appened to the output, if it exists
    output = ollama_generate(model="gemma4:latest", prompt=prompt, host="http://localhost:11434")

    # Check the output to make sure it is not a error, if it is an error send the error string below
    ERROR_OUTPUT = ""","Error","Error","Error" """
    input_csv = f'"{file_extention}","{file_description}","{high_level_desc}",'

    if "ERROR" in output:
        # Try again:
        output = ollama_generate(model="gemma4:latest", prompt=prompt, host="http://localhost:11434")
        if "ERROR" in output:
            print(f"LLM returned an error for input: {input_csv}. Output: {output}")
            return input_csv + ERROR_OUTPUT
        return input_csv + output
    else:
        return input_csv + output

def estimate_File_Information(text: str) -> list[dict]:
    """
    Parses technical documentation text using regex to extract structured 
    file format information based on the 'Identifier - Description' pattern.

    Args:
        text: The raw text containing the format definitions.

    Returns:
        A list of dictionaries, each containing 'Identifier' and 'Description'.
    """
    lines = text.strip().split('\n')
    file_data = []
    
    # Regex pattern: Matches "Identifier" followed by " - " and then the "Description".
    # Group 1: Identifier (Alphanumeric characters)
    # Group 2: Description (Everything after the separator)
    pattern = re.compile(r'^([A-Z0-9]+)\s*-\s*(.*)$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        
        if match:
            identifier = match.group(1).strip()
            description = match.group(2).strip()
            file_data.append({
                'Identifier': identifier,
                'Description': description
            })

    return file_data

def parse_header(line: str) -> str | None:
    """
    Detects and extracts the content of a header line.
    
    Uses a regex to look for content enclosed by one or more '=' signs.
    Example matches:
    - ===Title=== -> "Title"
    - =My Header= -> "My Header"
    - ===== Test ===== -> " Test "
    
    Args:
        line: The string line potentially containing a header.
    
    Returns:
        The extracted header title string, or None if no header is found.
    """
    # Regex explanation:
    # ^       : start of the line
    # =+      : one or more '=' characters (the opening delimiter)
    # (.*?)   : Capture group 1: matches any character (.), zero or more times (*), non-greedily (?)
    # =+      : one or more '=' characters (the closing delimiter)
    # $       : end of the line
    
    # Note: We strip leading/trailing whitespace from the captured content
    match = re.search(r"^=+(.*?)=+$", line.strip())
    
    if match:
        # Group 1 holds the actual content between the delimiters
        header_value = match.group(1).strip()
        return header_value
    else:
        return None


def extract_file_info_revised(text: str) -> list[dict]:
    """
    Parses technical documentation text using regex to extract structured 
    file format information based on the 'Identifier - Description' pattern.

    Args:
        text: The raw text containing the format definitions.

    Returns:
        A list of dictionaries, each containing 'Identifier' and 'Description'.
    """
    lines = text.strip().split('\n')
    print(f"Total lines to process: {len(lines)}")
    file_data = []
    
    # Regex pattern: Matches "Identifier" followed by " - " and then the "Description".
    # Group 1: Identifier (Alphanumeric characters)
    # Group 2: Description (Everything after the separator)
    pattern = re.compile(r'^([^–-]+)\s*[–-]\s*(.*)$')#(r'^([A-Z0-9]+)\s*-\s*(.*)$')
    header = ""
    with open(OUTPUT_FILENAME, 'a') as output_file:
        for line in lines:
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.replace("*", '')
            line = line.strip()
            if not line:
                continue

            # Check if the line is a header and extract it
            header_title = parse_header(line)
            # Also try to match the line as one for data extraction
            match = pattern.match(line)
            
            if header_title:
                header = header_title  # Store the current header for context
                print(f"Detected header: {header}")

            if match:
                identifier = match.group(1).strip()

                print(identifier)

                extentions = identifier.split(",")

                # Get the description data out
                description = match.group(2).strip()

                for extention in extentions:
                    ext = extention.split("|")
                    for ex in ext:

                        ex = ex.strip()
                        
                        # Should output: Input + "[Encoding]", "[Human Generated]", "[Human-Readable]", "[Suggested Role]"`
                        llm_output = process_data_stream(ext, description, header)
                        print(f"LLM Output: \n{llm_output}")

                        # if the data returned is not valid
                        if (not llm_output) or llm_output.endswith('ERROR'):
                            file_data.append({
                                'Identifier': ex,
                                'Description': description,
                                'Type': header,
                                'Encoding': "ERROR",
                                'Human Generated': "ERROR",
                                'Human-Readable': "ERROR",
                                'Suggested Role': "ERROR"
                            })
                        else:
                            try:
                                # Append to the file data
                                output_file.write(llm_output + "\n")

                                llm_output_data = llm_output.split(",")
                                llm_output_data = [item.strip().strip('"') for item in llm_output_data]

                                # Remove the first three items which are the input data, we only want the analysis results
                                llm_output_data = llm_output_data[3:]

                                file_data.append({
                                    'Identifier': ex,
                                    'Description': description,
                                    'Type': header,
                                    'Encoding': llm_output_data[0],
                                    'Human Generated': llm_output_data[1],
                                    'Human-Readable': llm_output_data[2],
                                    'Suggested Role': llm_output_data[3]
                                })
                            except Exception as e:
                                print(f"Error processing line: {line}")
                                print(f"LLM Output: {llm_output}")
                                print(f"Exception: {e}")
                                file_data.append({
                                    'Identifier': ex,
                                    'Description': description,
                                    'Type': header,
                                    'Encoding': "ERROR",
                                    'Human Generated': "ERROR",
                                    'Human-Readable': "ERROR",
                                    'Suggested Role': "ERROR"
                                })

    return file_data


with open("ListOfFileFormats_Wikipedia.md", 'r') as file:
    text = file.read()
    print(text.__len__())
    data = extract_file_info_revised(text)
    object_dict = {obj['Identifier']: obj for obj in data}
    # Write to file
    with open('data.json', 'w') as f:
        json.dump(object_dict, f, indent=4)  # indent makes it pretty to look at
