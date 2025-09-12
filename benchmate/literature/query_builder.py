


PUBMED_FIELD_MAP = {
    # Core Search Fields
    "all": "all",                  # All fields
    "title": "ti",                 # Title
    "title_abstract": "tiab",      # Title/Abstract
    "abstract": "ab",              # Abstract
    "text_words": "tw",            # Text Words
    "affiliation": "ad",           # Affiliation
    "journal": "ta",               # Journal abbreviation or full title
    "volume": "vi",                # Volume
    "pagination": "pg",            # First page number

    # Authors
    "author": "au",                # Author
    "first_author": "1au",         # First author
    "last_author": "lastau",       # Last author
    "full_author": "fau",          # Full author name
    "investigator": "fir",         # Full investigator/collaborator name

    # Identifiers & Grants
    "pmid": "pmid",                # PubMed ID
    "secondary_source_id": "si",   # Secondary Source ID (e.g., accession numbers)
    "grants": "gr",                # Grants and funding ID

    # Dates
    "publication_date": "dp",      # Date of Publication
    "create_date": "crdt",         # Create date (record first created)
    "entry_date": "edat",          # Entry date (Entrez date)
    "modification_date": "lr",     # Last Revision Date
    "mesh_date": "mhda",           # MeSH Date (indexed)

    # MeSH and Related
    "mesh": "mh",                  # MeSH Terms
    "mesh_major": "majr",          # MeSH Major Topic
    "mesh_subheading": "sh",       # MeSH Subheadings
    "pharmacological_action": "pa",# Pharmacological Action
    "supplementary_concept": "nm", # Supplementary Concept

    # Language, Place & Publisher
    "language": "la",              # Language
    "publication_type": "pt",      # Publication Type
    "publisher": "pubn",           # Publisher (Bookshelf)
    "place_of_publication": "pl",  # Place of publication

    # Other Fields
    "editor": "ed",                # Editor
    "conflict_of_interest": "cois",# Conflict of Interest Statement
    "owner": "owner",              # Data provider owner
    "personal_name_as_subject": "ps", # Personal Name as Subject

    # Filters / Subsets (use ...[sb])
    "free_full_text": "free full text[sb]",
    "full_text": "full text[sb]",
    "has_abstract": "hasabstract",
    "has_structured_abstract": "hasstructuredabstract",
    "systematic_review": "systematic[sb]",
    "publisher_subset": "publisher[sb]",
    "inprocess": "inprocess[sb]",
    "medline": "medline[sb]",
    "pubmed_not_medline": "pubmednotmedline[sb]",
    "all_subset": "all[sb]",
}

class PubMedQueryBuilder:
    def __init__(self, field_map):
        self.field_map = field_map

    def build_query(self, search_dict):
        """
        Build a PubMed query string from a structured dictionary.
        """
        # Handle main Boolean query
        query_parts = []
        for key, val in search_dict.items():
            if key.lower() == "flags":
                continue
            query_parts.append(self._parse_clause({key: val}))

        query_str = " AND ".join([p for p in query_parts if p])

        # Handle flags section
        if "flags" in search_dict:
            query_str = self._apply_flags(query_str, search_dict["flags"])

        return query_str.strip()

    def _parse_clause(self, clause):
        """
        Recursively parse Boolean operators and field clauses.
        """
        if isinstance(clause, dict):
            for op, terms in clause.items():
                op_upper = op.upper()

                # Boolean operators
                if op_upper in ["AND", "OR"]:
                    return f"({f' {op_upper} '.join(self._parse_clause(t) for t in terms)})"
                elif op_upper == "NOT":
                    return f"NOT ({' OR '.join(self._parse_clause(t) for t in terms)})"

                # Field-specific clause
                if op not in self.field_map:
                    raise ValueError(f"Unknown field: '{op}' (not in field_map)")
                field_tag = self.field_map[op]
                return self._format_field_clause(field_tag, terms)

        return ""

    def _format_field_clause(self, field_tag, terms):
        """
        Format a field clause with terms or as a flag.
        """
        # Direct filters like "review[PT]"
        if "[" in field_tag and "]" in field_tag and (not terms or terms == []):
            return field_tag

        # Field with terms
        if isinstance(terms, list) and terms:
            return " OR ".join([f'"{t}"[{field_tag}]' for t in terms])

        # Fallback if no terms
        return field_tag

    def _apply_flags(self, query_str, flags_dict):
        """
        Handle flags section: include/exclude filters.
        """
        include_flags = []
        exclude_flags = []

        if isinstance(flags_dict, dict):
            include_flags = flags_dict.get("include", [])
            exclude_flags = flags_dict.get("exclude", [])
        elif isinstance(flags_dict, list):
            include_flags = flags_dict

        # Validate and map include flags
        include_parts = []
        for f in include_flags:
            if f not in self.field_map:
                raise ValueError(f"Unknown flag in 'include': '{f}'")
            include_parts.append(self.field_map[f])

        # Validate and map exclude flags
        exclude_parts = []
        for f in exclude_flags:
            if f not in self.field_map:
                raise ValueError(f"Unknown flag in 'exclude': '{f}'")
            exclude_parts.append(self.field_map[f])

        # Attach to query
        if include_parts:
            query_str = f"{query_str} AND " + " AND ".join(include_parts) if query_str else " AND ".join(include_parts)
        if exclude_parts:
            query_str = f"{query_str} NOT " + " NOT ".join(exclude_parts) if query_str else " NOT ".join(exclude_parts)

        return query_str.strip()
