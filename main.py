citations = placeholder['content'].get('citations')
if citations:
    # Add the citations with a smaller font size, as plain text
    p = document.add_paragraph("Citations:\n")
    for citation in citations:
        source = citation['source'] if citation['source'].strip() else "N/A"
        page = str(citation['page']) if str(citation['page']).strip() else "N/A"
        citation_text = f"Source: {source}, Page: {page}\n"
        p.add_run(citation_text).font.size = Pt(8)
