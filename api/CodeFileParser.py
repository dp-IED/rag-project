from pathlib import Path
import re
from typing import Dict, List, Optional
import tokenize
import io
import ast

class CodeFileParser:
    """Parser system for code files that extracts meaningful content for analysis"""
    
    def __init__(self):
        self.supported_extensions = {
            '.py': self.parse_python,
            '.js': self.parse_javascript,
            '.tsx': self.parse_typescript,
            '.ts': self.parse_typescript,
            '.jsx': self.parse_javascript,
            '.java': self.parse_java,
            '.cpp': self.parse_cpp,
            '.h': self.parse_cpp,
            '.txt': self.parse_text,
            '.md': self.parse_markdown
        }
        
    async def parse_file(self, file_path: Path) -> Optional[Dict[str, str]]:
        """Main entry point for parsing any supported file"""
        if not file_path.suffix.lower() in self.supported_extensions:
            return None
            
        parser = self.supported_extensions[file_path.suffix.lower()]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return await parser(content)
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return await parser(content)

    async def parse_python(self, content: str) -> Dict[str, str]:
        """Parse Python files, extracting docstrings, comments, and function signatures"""
        result = {
            'docstrings': [],
            'comments': [],
            'functions': [],
            'classes': []
        }
        
        # Parse docstrings and function definitions
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result['functions'].append(f"def {node.name}({self._get_func_args(node)})")
                    if ast.get_docstring(node):
                        result['docstrings'].append(ast.get_docstring(node))
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append(f"class {node.name}")
                    if ast.get_docstring(node):
                        result['docstrings'].append(ast.get_docstring(node))
        except:
            pass  # If AST parsing fails, continue with other extraction methods
        
        # Extract comments
        try:
            tokens = tokenize.generate_tokens(io.StringIO(content).readline)
            for token in tokens:
                if token.type == tokenize.COMMENT:
                    comment = token.string.strip('# ')
                    if comment:
                        result['comments'].append(comment)
        except:
            pass
            
        return result

    async def parse_typescript(self, content: str) -> Dict[str, str]:
        """Parse TypeScript/TSX files"""
        result = {
            'interfaces': [],
            'types': [],
            'components': [],
            'functions': [],
            'comments': []
        }
        
        # Extract TypeScript interfaces and types
        interface_pattern = r'interface\s+(\w+)\s*{'
        type_pattern = r'type\s+(\w+)\s*='
        component_pattern = r'function\s+(\w+)\s*\(.*?\).*?{|const\s+(\w+)\s*=\s*\(.*?\)\s*=>'
        
        result['interfaces'].extend(re.findall(interface_pattern, content))
        result['types'].extend(re.findall(type_pattern, content))
        
        # Extract React components
        for match in re.finditer(component_pattern, content, re.MULTILINE | re.DOTALL):
            component_name = match.group(1) or match.group(2)
            if component_name:
                result['components'].append(component_name)
        
        # Extract comments (both single-line and multi-line)
        comment_pattern = r'//.*?$|/\*.*?\*/'
        result['comments'].extend(re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL))
        
        return result

    async def parse_javascript(self, content: str) -> Dict[str, str]:
        """Parse JavaScript/JSX files"""
        result = {
            'functions': [],
            'components': [],
            'comments': []
        }
        
        # Similar to TypeScript but without type information
        component_pattern = r'function\s+(\w+)\s*\(.*?\).*?{|const\s+(\w+)\s*=\s*\(.*?\)\s*=>'
        comment_pattern = r'//.*?$|/\*.*?\*/'
        
        for match in re.finditer(component_pattern, content, re.MULTILINE | re.DOTALL):
            component_name = match.group(1) or match.group(2)
            if component_name:
                result['components'].append(component_name)
                
        result['comments'].extend(re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL))
        
        return result

    async def parse_java(self, content: str) -> Dict[str, str]:
        """Parse Java files"""
        result = {
            'classes': [],
            'methods': [],
            'comments': []
        }
        
        class_pattern = r'class\s+(\w+)'
        method_pattern = r'(?:public|private|protected)?\s+(?:static\s+)?[\w<>[\],\s]+\s+(\w+)\s*\([^)]*\)'
        comment_pattern = r'//.*?$|/\*.*?\*/'
        
        result['classes'].extend(re.findall(class_pattern, content))
        result['methods'].extend(re.findall(method_pattern, content))
        result['comments'].extend(re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL))
        
        return result

    async def parse_cpp(self, content: str) -> Dict[str, str]:
        """Parse C++ files"""
        result = {
            'classes': [],
            'functions': [],
            'comments': []
        }
        
        class_pattern = r'class\s+(\w+)'
        function_pattern = r'(?:[\w:*&]+\s+)+(\w+)\s*\([^)]*\)'
        comment_pattern = r'//.*?$|/\*.*?\*/'
        
        result['classes'].extend(re.findall(class_pattern, content))
        result['functions'].extend(re.findall(function_pattern, content))
        result['comments'].extend(re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL))
        
        return result

    async def parse_text(self, content: str) -> Dict[str, str]:
        """Parse plain text files"""
        return {'content': content}

    async def parse_markdown(self, content: str) -> Dict[str, str]:
        """Parse Markdown files"""
        result = {
            'headers': [],
            'code_blocks': [],
            'content': content
        }
        
        header_pattern = r'^#+\s+(.+)$'
        code_block_pattern = r'```[\w]*\n(.*?)```'
        
        result['headers'].extend(re.findall(header_pattern, content, re.MULTILINE))
        result['code_blocks'].extend(re.findall(code_block_pattern, content, re.MULTILINE | re.DOTALL))
        
        return result

    def _get_func_args(self, node: ast.FunctionDef) -> str:
        """Helper method to extract function arguments from AST node"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return ', '.join(args)

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if a file type is supported"""
        return file_path.suffix.lower() in self.supported_extensions