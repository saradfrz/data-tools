#!/usr/bin/env python3
import sys
import csv
import os
import re
from bs4 import BeautifulSoup

# Parameters and Constants
INPUT_FILE = "input.html"         # Default input file path
OUTPUT_FILE = "sections.tsv"      # Default output TSV file path
ENCODING = "utf-8"                # File encoding to use
DELIMITER = "\t"                  # Delimiter for TSV file

# HTML parsing constants
SECTION_HEADING_DATA_PURPOSE = "section-heading"
SECTION_DURATION_DATA_PURPOSE = "section-duration"
SECTION_DURATION_SR_ONLY_DATA_PURPOSE = "section-duration-sr-only"
TRUNCATE_CLASS = "truncate-with-tooltip--ellipsis--YJw4N"

class HTMLSectionExtractor:
    def __init__(self, file_path):
        """
        Initializes the extractor with the specified file path.
        
        Args:
            file_path (str): Path to the HTML file.
        """
        self.file_path = file_path
        self.html_content = ""
        self.sections = []  # List to store tuples of (section title, duration)

    def open_html(self):
        """
        Opens and reads the HTML file. Raises an error if the file does not exist.
        """
        full_path = os.path.join("udemy_section_name_extractor", self.file_path)
        if not self.file_path or not os.path.exists(full_path):
            raise FileNotFoundError(f"The file '{self.file_path}' does not exist.")
        
        with open(full_path, 'r', encoding=ENCODING) as file:
            self.html_content = file.read()

    def transform_spaces(self, text):
        """
        Transforms multiple whitespace characters in the given text into a single space.
        
        Args:
            text (str): The input string to be transformed.
        
        Returns:
            str: The transformed string with single spaces.
        """
        return re.sub(r'\s+', ' ', text)

    def extract_content(self):
        """
        Parses the HTML content and extracts section titles and durations.
        The extracted data is stored in the 'sections' attribute as a list of tuples.
        """
        soup = BeautifulSoup(self.html_content, 'html.parser')
        self.sections = []  # Reset the list to ensure fresh extraction

        # Locate all section heading containers based on the data-purpose attribute.
        section_headings = soup.find_all("div", {"data-purpose": SECTION_HEADING_DATA_PURPOSE})
        
        for heading in section_headings:
            # Extract the section title from the nested span with the specified class.
            title_span = heading.find("span", class_=TRUNCATE_CLASS)
            title = title_span.get_text(strip=True).replace('Section ','\n[ ] S.') if title_span else "N/A"
            # Transform multiple spaces into a single one.
            title = self.transform_spaces(title)
            
            # Locate the duration element.
            duration_div = heading.find_next("div", {"data-purpose": SECTION_DURATION_DATA_PURPOSE})
            duration = "N/A"
            
            if duration_div:
                # Attempt to extract duration from the screen-reader-only span.
                sr_span = duration_div.find("span", {"data-purpose": SECTION_DURATION_SR_ONLY_DATA_PURPOSE})
                if sr_span:
                    duration_spans = sr_span.find_all("span")
                    if duration_spans and len(duration_spans) >= 2:
                        duration = duration_spans[-1].get_text(strip=True)
                    else:
                        duration = duration_div.get_text(strip=True)
                else:
                    # Fallback: parse text from the aria-hidden span.
                    hidden_span = duration_div.find("span", {"aria-hidden": "true"})
                    if hidden_span:
                        text = hidden_span.get_text(strip=True)
                        if '|' in text:
                            duration = text.split('|')[-1].strip()
                        else:
                            duration = text
                # Transform multiple spaces in duration as well.
                duration = self.transform_spaces(duration)
            self.sections.append((title, duration))

    def save_as_tsv(self, output_file):
        """
        Saves the extracted sections as a TSV file.
        
        Args:
            output_file (str): The file path for the output TSV file.
        """
        full_output_path = os.path.join("udemy_section_name_extractor", output_file)
        with open(full_output_path, 'w', encoding=ENCODING, newline='') as file:
            writer = csv.writer(file, delimiter=DELIMITER)
            # Write header row.
            writer.writerow(["Section Title", "Duration"])
            for title, duration in self.sections:
                writer.writerow([title, duration])
    
    def save_as_txt(self, output_file):
        """
        Saves the extracted sections as a text file.
        
        Args:
            output_file (str): The file path for the output text file.
        """
        full_output_path = os.path.join("udemy_section_name_extractor", output_file)
        with open(full_output_path, 'w', encoding=ENCODING) as file:
            file.write("Extracted Sections:\n\n")
            for index, (title, duration) in enumerate(self.sections, start=1):
                file.write(f"{title} - {duration}\n\n")

if __name__ == "__main__":
    # Define parameters at the beginning.
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_file = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE

    # Instantiate the HTMLSectionExtractor with the specified input file.
    extractor = HTMLSectionExtractor(file_path=input_file)
    
    # Execute the methods in sequence.
    extractor.open_html()         # Open and read the HTML file.
    extractor.extract_content()   # Parse and extract the desired data.
    extractor.save_as_txt(output_file)  # Save the results as a TSV file.
    
    print(f"Extracted sections have been saved to '{output_file}'.")
