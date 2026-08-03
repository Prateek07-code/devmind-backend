import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# 1. Initialize the parser globally so it doesn't reload for every single file (saves memory)
PY_LANGUAGE = Language(tspython.language())
parser = Parser()
parser.language = PY_LANGUAGE

def extract_ast_chunks(code_content: str, file_path: str) -> list:
    """
    Takes raw Python code, parses it into an AST, and returns a list of 
    structured dictionaries containing whole functions and classes.
    """
    if not code_content.strip():
        return []

    code_bytes = bytes(code_content, "utf8")
    tree = parser.parse(code_bytes)
    
    chunks = []
    
    # A recursive function to walk through the branches of the AST
    def walk_tree(node):
        # We want to extract both standalone functions AND entire classes
        if node.type in ['function_definition', 'class_definition']:
            chunk_text = code_bytes[node.start_byte:node.end_byte].decode('utf-8')
            chunks.append({
                "type": node.type,
                "text": chunk_text,
                "start_line": node.start_point[0],
                "end_line": node.end_point[0],
                "file_path": file_path  # <--- WE ADDED THIS LINE!
            })
            
        # Continue checking all children nodes inside this node
        for child in node.children:
            walk_tree(child)
            
    # Start the recursive walk at the very root of the file
    walk_tree(tree.root_node)
    
    return chunks