The TextLinearizationConfig class is designed to define how a document is converted into a linear text string, controlling various aspects of the text transformation process. Each parameter in this class serves a specific purpose and influences the final output of the linearized text. Below is a detailed explanation of each parameter along with examples to illustrate their impact.

Parameters and Their Impact
remove_new_lines_in_leaf_elements (bool): When set to True, this parameter removes new lines within leaf elements (like paragraphs), thereby reducing extra whitespace.

Example:
Input:
csharp
Copy code
This is a sentence.

This is another sentence.
Output: This is a sentence. This is another sentence.
max_number_of_consecutive_new_lines (int): Limits the maximum number of consecutive new lines. Extra new lines beyond this limit are removed.

Example:
Input:
mathematica
Copy code
Line 1



Line 2
Output with max_number_of_consecutive_new_lines=2:
mathematica
Copy code
Line 1

Line 2
max_number_of_consecutive_spaces (int): Limits the maximum number of consecutive spaces. If set to None, no spaces are removed.

Example:
Input: This is a sentence.
Output with max_number_of_consecutive_spaces=1: This is a sentence.
hide_header_layout (bool): When True, headers are hidden in the output.

Example:
Input:
vbnet
Copy code
Header: Document Title
Content: This is the content.
Output: Content: This is the content.
hide_footer_layout (bool): When True, footers are hidden in the output.

Example:
Input:
vbnet
Copy code
Content: This is the content.
Footer: Page 1
Output: Content: This is the content.
hide_figure_layout (bool): When True, figures are hidden in the output.

Example:
Input:
csharp
Copy code
Content: This is the content.
[Figure: Diagram]
Output: Content: This is the content.
hide_table_layout (bool): When True, tables are hidden in the output.

Example:
Input:
csharp
Copy code
Content: This is the content.
[Table: Data Table]
Output: Content: This is the content.
hide_key_value_layout (bool): When True, key-value pairs are hidden in the output.

Example:
Input:
makefile
Copy code
Key: Value
Output: (empty)
hide_page_num_layout (bool): When True, page numbers are hidden in the output.

Example:
Input:
vbnet
Copy code
Page 1
Content: This is the content.
Output: Content: This is the content.
page_num_prefix (str): Prefix for page numbers in the output.

Example:
Input:
vbnet
Copy code
Page 1
Content: This is the content.
Output with page_num_prefix='Pg. ': Pg. 1 Content: This is the content.
page_num_suffix (str): Suffix for page numbers in the output.

Example:
Input:
vbnet
Copy code
Page 1
Content: This is the content.
Output with page_num_suffix=' - end': Page 1 - end Content: This is the content.
same_paragraph_separator (str): Separator used when combining elements within a text block.

Example:
Input:
csharp
Copy code
This is a sentence.
This is another sentence.
Output with same_paragraph_separator=' ': This is a sentence. This is another sentence.
same_layout_element_separator (str): Separator used when two elements are in the same layout element.

Example:
Input:
css
Copy code
This is a header.
This is a subheader.
Output with same_layout_element_separator='\n':
css
Copy code
This is a header.
This is a subheader.
layout_element_separator (str): Separator used when combining linearized layout elements.

Example:
Input:
vbnet
Copy code
Header: This is the header.
Content: This is the content.
Output with layout_element_separator='\n\n':
vbnet
Copy code
Header: This is the header.

Content: This is the content.
list_element_separator (str): Separator for elements in a list layout.

Example:
Input:
diff
Copy code
- Item 1
- Item 2
Output with list_element_separator='\n':
diff
Copy code
- Item 1
- Item 2
list_layout_prefix (str): Prefix for list layout elements (parent).

Example:
Input:
diff
Copy code
- Item 1
- Item 2
Output with list_layout_prefix='List:': List:- Item 1 - Item 2
list_layout_suffix (str): Suffix for list layout elements (parent).

Example:
Input:
diff
Copy code
- Item 1
- Item 2
Output with list_layout_suffix=' End of List': - Item 1 - Item 2 End of List
list_element_prefix (str): Prefix for elements in a list layout (children).

Example:
Input:
diff
Copy code
- Item 1
- Item 2
Output with list_element_prefix='* ': * - Item 1 * - Item 2
list_element_suffix (str): Suffix for elements in a list layout (children).

Example:
Input:
diff
Copy code
- Item 1
- Item 2
Output with list_element_suffix=';': - Item 1; - Item 2;
title_prefix (str): Prefix for title layout elements.

Example:
Input:
makefile
Copy code
Title: Document Title
Output with title_prefix='## ': ## Title: Document Title
title_suffix (str): Suffix for title layout elements.

Example:
Input:
makefile
Copy code
Title: Document Title
Output with title_suffix=' ##': Title: Document Title ##
table_layout_prefix (str): Prefix for table elements.

Example:
Input:
mathematica
Copy code
Table: Data Table
Output with table_layout_prefix='\n\n': \n\nTable: Data Table
table_layout_suffix (str): Suffix for table elements.

Example:
Input:
mathematica
Copy code
Table: Data Table
Output with table_layout_suffix='\n': Table: Data Table\n
table_remove_column_headers (bool): When True, removes pandas index column headers from tables.

Example:
Input:
sql
Copy code
Table with headers:
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
Output:
sql
Copy code
Table with headers:
| Value 1  | Value 2  |
table_column_header_threshold (float): Threshold for a row to be selected as a header when rendering as markdown. A value of 0.9 means 90% of the cells must have the is_header_cell flag.

Example:
If a row has 10 cells, at least 9 must be marked as headers for the row to be considered a header row.
table_linearization_format (str): How to represent tables in the linearized output. Choices are plaintext, markdown, or html.

Example:
If table_linearization_format='markdown', the table will be formatted as:
sql
Copy code
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
table_add_title_as_caption (bool): When using the HTML linearization format, adds the title inside the table as <caption></caption>.

Example:
Input:
sql
Copy code
Title: Data Table
<table>...</table>
Output:
css
Copy code
<table><caption>Data Table</caption>...</table>
table_add_footer_as_paragraph (bool): Adds footers as a paragraph when using the HTML linearization format.

Example:
Input:
less
Copy code
<table>...</table>
Footer: Table Footer
Output:
css
Copy code
<table>...</table>
<p>Table Footer</p>
table_tabulate_format (str): Markdown tabulate format to use when tables are linearized as markdown. Example: github.

Example:
Format: github will format tables as per GitHub markdown specifications.
table_tabulate_remove_extra_hyphens (bool): Reduces the number of hyphens in markdown tables to the minimum allowed by the GitHub Markdown spec.

Example:
Input:
sql
Copy code
| Column 1  | Column 2  |
|-----------|-----------|
| Value 1   | Value 2   |
Output:
sql
Copy code
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
table_duplicate_text_in_merged_cells (bool): Duplicates text in merged cells to preserve line alignment.

Example:
Input:
mathematica
Copy code
| Column 1  | Column 2  |
| Value 1   | Value 2   |
Output:
mathematica
Copy code
| Column 1  | Column 2  |
| Value 1   | Value 1   |
table_flatten_headers (bool): Flattens table headers into a single row, unmerging cells horizontally.

Example:
Input:
css
Copy code
| Header 1     | Header 2  |
| Subheader 1  | Subheader 2 |
| Value 1      | Value 2   |
Output:
css
Copy code
| Header 1 | Header 2 |
| Value 1  | Value 2  |
table_min_table_words (int): Threshold below which tables will be rendered as words instead of using a table layout.

Example:
If the table has fewer than the specified number of words, it will be rendered as plain text.
table_column_separator (str): Table column separator used when linearizing layout tables. Not used if AnalyzeDocument was called with the TABLES feature.

Example:
Separator: \t (tab)
table_flatten_semi_structured_as_plaintext (bool): Ignores table structure for semi-structured tables and returns them as text.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output: Column 1 Column 2 Value 1 Value 2
table_prefix (str): Prefix for tables.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_prefix='Table:': Table: | Column 1 | Column 2 |
table_suffix (str): Suffix for tables.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_suffix=' End of Table': | Column 1 | Column 2 | End of Table
table_row_separator (str): Table row separator.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_row_separator='\n':
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
table_row_prefix (str): Prefix for table rows.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_row_prefix='Row:': Row:| Column 1 | Column 2 |
table_row_suffix (str): Suffix for table rows.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_row_suffix=' End of Row': | Column 1 | Column 2 | End of Row
table_cell_prefix (str): Prefix for table cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_cell_prefix='Cell:': | Cell:Column 1 | Cell:Column 2 |
table_cell_suffix (str): Suffix for table cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_cell_suffix=' End of Cell': | Column 1 End of Cell | Column 2 End of Cell |
table_cell_header_prefix (str): Prefix for header cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_cell_header_prefix='Header:': | Header:Column 1 | Header:Column 2 |
table_cell_header_suffix (str): Suffix for header cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_cell_header_suffix=' End of Header': | Column 1 End of Header | Column 2 End of Header |
table_cell_empty_cell_placeholder (str): Placeholder for empty cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  |         |
Output with table_cell_empty_cell_placeholder='[empty]': | Column 1 | Column 2 | | Value 1 | [empty] |
table_cell_merge_cell_placeholder (str): Placeholder for merged cells.

Example:
Input:
sql
Copy code
| Column 1       | Column 2 |
| Value 1 (merge)| Value 2  |
Output with table_cell_merge_cell_placeholder='[merged]': | Column 1 | Column 2 | | Value 1 [merged]| Value 2 |
table_cell_left_merge_cell_placeholder (str): Placeholder for left merge cells.

Example:
Input:
mathematica
Copy code
| Column 1  | Column 2 |
| Value 1   |          |
Output with table_cell_left_merge_cell_placeholder='[L]': | Column 1 | Column 2 | | Value 1 | [L] |
table_cell_top_merge_cell_placeholder (str): Placeholder for top merge cells.

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  |          |
Output with table_cell_top_merge_cell_placeholder='[T]': | Column 1 | Column 2 | | Value 1 | [T] |
table_cell_cross_merge_cell_placeholder (str): Placeholder for cross merge cells.

Example:
Input:
mathematica
Copy code
| Column 1  | Column 2 |
| Value 1   | Value 2  |
Output with table_cell_cross_merge_cell_placeholder='[X]': | Column 1 | Column 2 | | Value 1 [X] | Value 2 |
table_title_prefix (str): Prefix for table titles if they are outside of the table (floating).

Example:
Input:
mathematica
Copy code
Table Title
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_title_prefix='Title:': Title: Table Title | Column 1 | Column 2 | | Value 1 | Value 2 |
table_title_suffix (str): Suffix for table titles if they are outside of the table (floating).

Example:
Input:
mathematica
Copy code
Table Title
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Output with table_title_suffix=' End of Title': Table Title End of Title | Column 1 | Column 2 | | Value 1 | Value 2 |
table_footers_prefix (str): Prefix for table footers if they are outside of the table (floating).

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Table Footer
Output with table_footers_prefix='Footer:': | Column 1 | Column 2 | | Value 1 | Value 2 | Footer: Table Footer
table_footers_suffix (str): Suffix for table footers if they are outside of the table (floating).

Example:
Input:
mathematica
Copy code
| Column 1 | Column 2 |
| Value 1  | Value 2  |
Table Footer
Output with table_footers_suffix=' End of Footer': | Column 1 | Column 2 | | Value 1 | Value 2 | Table Footer End of Footer
header_prefix (str): Prefix for header layout elements.

Example:
Input:
css
Copy code
Header: Document Title
Output with header_prefix='Header:': Header: Document Title
header_suffix (str): Suffix for header layout elements.

Example:
Input:
css
Copy code
Header: Document Title
Output with header_suffix=' End of Header': Header: Document Title End of Header
section_header_prefix (str): Prefix for section header layout elements.

Example:
Input:
css
Copy code
Section Header: Introduction
Output with section_header_prefix='Section:': Section: Section Header: Introduction
section_header_suffix (str): Suffix for section header layout elements.

Example:
Input:
css
Copy code
Section Header: Introduction
Output with section_header_suffix=' End of Section': Section Header: Introduction End of Section
text_prefix (str): Prefix for text layout elements.

Example:
Input:
vbnet
Copy code
Text: This is a paragraph.
Output with text_prefix='Text:': Text: This is a paragraph.
text_suffix (str): Suffix for text layout elements.

Example:
Input:
vbnet
Copy code
Text: This is a paragraph.
Output with text_suffix=' End of Text': Text: This is a paragraph. End of Text
key_value_layout_prefix (str): Prefix for key-value layout elements (not for individual key-value elements).

Example:
Input:
mathematica
Copy code
Key-Value Layout
Key: Value
Output with key_value_layout_prefix='KV:': KV: Key-Value Layout Key: Value
key_value_layout_suffix (str): Suffix for key-value layout elements (not for individual key-value elements).

Example:
Input:
mathematica
Copy code
Key-Value Layout
Key: Value
Output with key_value_layout_suffix=' End of KV': Key-Value Layout Key: Value End of KV
key_value_prefix (str): Prefix for key-value elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with key_value_prefix='KV:': KV: Key: Value
key_value_suffix (str): Suffix for key-value elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with key_value_suffix=' End of KV': Key: Value End of KV
key_prefix (str): Prefix for key elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with key_prefix='K:': K: Key: Value
key_suffix (str): Suffix for key elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with key_suffix=' End of Key': Key: End of Key Value
value_prefix (str): Prefix for value elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with value_prefix='V:': Key: V: Value
value_suffix (str): Suffix for value elements.

Example:
Input:
makefile
Copy code
Key: Value
Output with value_suffix=' End of Value': Key: Value End of Value
entity_layout_prefix (str): Prefix for LAYOUT_ENTITY elements (layout elements without a predicted layout type).

Example:
Input:
mathematica
Copy code
Entity Layout: Unknown
Output with entity_layout_prefix='Entity:': Entity: Entity Layout: Unknown
entity_layout_suffix (str): Suffix for LAYOUT_ENTITY elements (layout elements without a predicted layout type).

Example:
Input:
mathematica
Copy code
Entity Layout: Unknown
Output with entity_layout_suffix=' End of Entity': Entity Layout: Unknown End of Entity
figure_layout_prefix (str): Prefix for figure layout elements.

Example:
Input:
css
Copy code
Figure: Diagram
Output with figure_layout_prefix='Figure:': Figure: Figure: Diagram
figure_layout_suffix (str): Suffix for figure layout elements.

Example:
Input:
css
Copy code
Figure: Diagram
Output with figure_layout_suffix=' End of Figure': Figure: Diagram End of Figure
footer_layout_prefix (str): Prefix for footer layout elements.

Example:
Input:
css
Copy code
Footer: Page 1
Output with footer_layout_prefix='Footer:': Footer: Footer: Page 1
footer_layout_suffix (str): Suffix for footer layout elements.

Example:
Input:
css
Copy code
Footer: Page 1
Output with footer_layout_suffix=' End of Footer': Footer: Page 1 End of Footer
selection_element_selected (str): Representation for a selection element when selected.

Example:
Input:
csharp
Copy code
[X] Selected Option
Output: [X] Selected Option
selection_element_not_selected (str): Representation for a selection element when not selected.

Example:
Input:
css
Copy code
[ ] Unselected Option
Output: [ ] Unselected Option
heuristic_h_tolerance (float): Determines how much the line below and above the current line should differ in width to be separated.

Example:
If the width difference between two lines is greater than 30% (0.3), they will be separated.
heuristic_line_break_threshold (float): Determines the acceptable space between two lines before splitting them. Expressed as a multiple of minimum heights.

Example:
If the space between two lines is greater than 90% (0.9) of the minimum height, they will be split.
heuristic_overlap_ratio (float): Determines how much vertical overlap is tolerated between two subsequent lines before merging them into a single line.

Example:
If the vertical overlap between lines is greater than 50% (0.5), they will be merged.
signature_token (str): Representation for a signature in the linearized text.

Example:
Input:
csharp
Copy code
[SIGNATURE]
Output: [SIGNATURE]
add_prefixes_and_suffixes_as_words (bool): Controls if prefixes/suffixes will be inserted into the words returned by get_text_and_words.

Example:
Input:
vbnet
Copy code
Text: This is a paragraph.
Output: Text: This is a paragraph. (with prefixes/suffixes as words)
add_prefixes_and_suffixes_in_text (bool): Controls if prefixes/suffixes will be added to the linearized text.

Example:
Input:
vbnet
Copy code
Text: This is a paragraph.
Output: Text: This is a paragraph. (with prefixes/suffixes in text)
Conclusion
The TextLinearizationConfig class provides comprehensive control over how a document is transformed into a linear text string. By adjusting these parameters, you can customize the output to meet specific requirements, such as removing extra whitespace, hiding certain layout elements, or adding prefixes and suffixes to different parts of the text. This flexibility ensures that the linearized text is formatted precisely as needed for various applications.






