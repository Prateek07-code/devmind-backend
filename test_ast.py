import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# 1. Load the Python grammar language
PY_LANGUAGE = Language(tspython.language())
parser = Parser()
parser.language = PY_LANGUAGE

# 2. Read our dummy code file
with open("dummy_code.py", "r", encoding="utf-8") as f:
    code_content = f.read()

# Tree-sitter requires the text to be converted to bytes first
code_bytes = bytes(code_content, "utf8")
tree = parser.parse(code_bytes)

# ----------------- NEW EXTRACTION LOGIC -----------------

def extract_functions(node, source_bytes):
    """Recursively walks the AST to find and extract standalone functions."""
    chunks = []
    
    # If the parser finds a node specifically labeled as a function...
    if node.type == 'function_definition':
        # Slice the exact bytes of code where this function starts and ends
        function_text = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
        
        chunks.append({
            "type": "function",
            "text": function_text,
            "start_line": node.start_point[0],
            "end_line": node.end_point[0]
        })
        
    # Recursively check all children (in case functions are inside classes)
    for child in node.children:
        chunks.extend(extract_functions(child, source_bytes))
        
    return chunks

# Run the extraction
extracted_chunks = extract_functions(tree.root_node, code_bytes)

# Print the results beautifully
print(f"\n>>> FOUND {len(extracted_chunks)} LOGICAL CHUNKS!")
for i, chunk in enumerate(extracted_chunks):
    print(f"\n--- CHUNK {i+1} (Lines {chunk['start_line']} to {chunk['end_line']}) ---")
    print(chunk['text'])