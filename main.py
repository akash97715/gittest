# Sample data from the provided list of dictionaries (simulated based on the description)
extracted_tables = [
    {
        'document_name': 'tobeingest',
        'table_title': 'Table 1. Continued',
        'footers': [
            "Abbreviations: 5-ASAs, aminosalicylates; BEP; Baccalauréate Professionnel; CAD, Canadian dollars; CAP, Certificate d'Aptitude Professionelle; CEGEP, Collège d'enseignement général et professionnel; n, weighted number of patients with each characteristic; N, number of patients included in the analysis; SD, standard deviation; TNF, tumor necrosis factor; UC, ulcerative colitis; USD, United States dollars.",
            '"Diagnosed condition; Question: "Have you personally been told by a doctor that you have any of the following health conditions? Please select all that apply" (Patient Survey Questions, Supplementary Data Content 6).',
            'Patients with a "milder" form of the disease were defined as those who had ever taken a prescription medication for their UC...',
        ],
        'table_html': '<table><tr><th>Characteristics</th><th>Patients</th></tr><tr><td>Diagnosis of depression</td><td>147 (15%)</td></tr></table>'
    },
    {
        'document_name': 'tobeingest',
        'table_title': 'Table 1. Patient demographics',
        'footers': [
            "United States: job-specific training, some college but no degree...",
            "Education levels...",
            "Males were more likely to be employed than females..."
        ],
        'table_html': '<table><tr><th>Age</th><th>Patients</th></tr><tr><td>41</td><td>1000</td></tr></table>'
    },
    {
        'document_name': 'tobeingest',
        'table_title': 'B) Educational level',
        'footers': [],
        'table_html': '<table><tr><th>Not employed</th><th>Full time</th></tr><tr><td>Stopped treatment to start a family</td><td>0.11</td></tr></table>'
    }
]

# Create the lists
concatenated_list = []
html_content_list = []

for table in extracted_tables:
    # Document name
    doc_name = table['document_name']
    
    # Table title (if exists and not empty)
    title = table.get('table_title', '')
    title_str = title + " " if title else ""
    
    # Footers (concatenate all footers into a single string)
    footer_str = " ".join(table.get('footers', []))
    
    # Concatenate document name, table title, and footers
    concatenated_list.append(f"{doc_name} {title_str}{footer_str}")
    
    # HTML content
    html_content_list.append(table['table_html'])

concatenated_list, html_content_list
