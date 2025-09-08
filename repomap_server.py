import asyncio
import json
import os
import logging
import argparse
import fnmatch
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
import dataclasses

from fastmcp import FastMCP, settings
from repomap_class import RepoMap
from utils import count_tokens, read_text
from scm import get_scm_fname
from importance import filter_important_files

def parse_gitignore(directory: str) -> List[str]:
    """Parse .gitignore file and return list of patterns to exclude."""
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            log.warning(f"Error reading .gitignore file {gitignore_path}: {e}")
    
    return patterns

def should_exclude_from_gitignore(file_path: str, gitignore_patterns: List[str], root_dir: str) -> bool:
    """Check if a file should be excluded based on .gitignore patterns."""
    if not gitignore_patterns:
        return False
    
    # Get relative path from root directory
    try:
        rel_path = os.path.relpath(file_path, root_dir)
    except ValueError:
        return False
    
    for pattern in gitignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            dir_pattern = pattern.rstrip('/')
            if fnmatch.fnmatch(rel_path, dir_pattern) or fnmatch.fnmatch(rel_path, pattern + '*'):
                return True
        # Handle regular file patterns
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    
    return False

# Enhanced file filtering with configurable patterns and .gitignore support
def find_src_files(directory: str, file_patterns: Optional[List[str]] = None) -> List[str]:
    """Find source files in a directory with proper filtering, including .gitignore support.
    
    Args:
        directory: Directory to search
        file_patterns: List of file extensions to include (e.g., ['.py', '.js'])
                     If None, uses default source code extensions
    """
    if not os.path.isdir(directory):
        if os.path.isfile(directory) and is_source_file(directory, file_patterns):
            return [directory]
        return []
    
    # Default source code extensions
    default_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
                         '.go', '.rs', '.rb', '.php', '.swift', '.scala', '.kt'}
    
    # Use provided patterns or default to source extensions
    if file_patterns:
        extensions = {ext.lower() for ext in file_patterns if ext.startswith('.')}
    else:
        extensions = default_extensions
    
    # Parse .gitignore patterns
    gitignore_patterns = parse_gitignore(directory)
    if gitignore_patterns:
        log.debug(f"Found {len(gitignore_patterns)} .gitignore patterns: {gitignore_patterns}")
    
    src_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env', '.git',
            'dist', 'build', 'target', 'out', 'bin', 'obj',
            'static', 'templates', 'research', 'settings', 'test_example'
        }]
        
        # Also exclude directories based on .gitignore patterns
        dirs[:] = [d for d in dirs if not should_exclude_from_gitignore(
            os.path.join(root, d), gitignore_patterns, directory
        )]
        
        for file in files:
            if not file.startswith('.'):
                file_path = os.path.join(root, file)
                
                # Check .gitignore exclusion
                if should_exclude_from_gitignore(file_path, gitignore_patterns, directory):
                    continue
                
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in extensions:
                    src_files.append(file_path)
    
    # Debug logging
    log.debug(f"find_src_files in {directory}: found {len(src_files)} source files with patterns {file_patterns}")
    if src_files and len(src_files) > 0:
        log.debug(f"Sample files found: {src_files[:5]}")
    
    return src_files

def is_source_file(filepath: str, file_patterns: Optional[List[str]] = None) -> bool:
    """Check if a file is a source code file based on extensions."""
    # Default source code extensions
    default_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
                         '.go', '.rs', '.rb', '.php', '.swift', '.scala', '.kt'}
    
    # Use provided patterns or default to source extensions
    if file_patterns:
        extensions = {ext.lower() for ext in file_patterns if ext.startswith('.')}
    else:
        extensions = default_extensions
    
    file_ext = os.path.splitext(filepath)[1].lower()
    return file_ext in extensions

# Configure logging
log = logging.getLogger()


# Set global stateless_http setting
settings.stateless_http = True

# Create MCP server
mcp = FastMCP("RepoMapServer")

@mcp.tool()
async def repo_map(
    project_root: str,
    chat_files: Optional[List[str]] = None,
    other_files: Optional[List[str]] = None,
    token_limit: Any = 2048,  # Accept any type to handle empty strings
    exclude_unranked: bool = False,
    force_refresh: bool = False,
    mentioned_files: Optional[List[str]] = None,
    mentioned_idents: Optional[List[str]] = None,
    verbose: bool = False,
    max_context_window: Optional[int] = None,
    file_patterns: Optional[List[str]] = None,
    scan_directories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Generate a repository map for the specified files, providing a list of function prototypes and variables for files as well as relevant related
    files. Provide filenames relative to the project_root. In addition to the files provided, relevant related files will also be included with a
    very small ranking boost.

    :param project_root: Root directory of the project to search.  (must be an absolute path!)
    :param chat_files: A list of file paths that are currently in the chat context. These files will receive the highest ranking.
    :param other_files: A list of other relevant file paths in the repository to consider for the map. They receive a lower ranking boost than mentioned_files and chat_files.
    :param token_limit: The maximum number of tokens the generated repository map should occupy. Defaults to 2048.
    :param exclude_unranked: If True, files with a PageRank of 0.0 will be excluded from the map. Defaults to False.
    :param force_refresh: If True, forces a refresh of the repository map cache. Defaults to False.
    :param mentioned_files: Optional list of file paths explicitly mentioned in the conversation and receive a mid-level ranking boost.
    :param mentioned_idents: Optional list of identifiers explicitly mentioned in the conversation, to boost their ranking.
    :param verbose: If True, enables verbose logging for the RepoMap generation process. Defaults to False.
    :param max_context_window: Optional maximum context window size for token calculation, used to adjust map token limit when no chat files are provided.
    :returns: A dictionary containing:
        - 'map': the generated repository map string
        - 'report': a dictionary with file processing details including:
            - 'included': list of processed files
            - 'excluded': dictionary of excluded files with reasons
            - 'definition_matches': count of matched definitions
            - 'reference_matches': count of matched references
            - 'total_files_considered': total files processed
        Or an 'error' key if an error occurred.
    """
    if not os.path.isdir(project_root):
        return {"error": f"Project root directory not found: {project_root}"}

    # 1. Handle and validate parameters
    # Convert token_limit to integer with fallback
    try:
        token_limit = int(token_limit) if token_limit else 2048
    except (TypeError, ValueError):
        token_limit = 2048
    
    # Ensure token_limit is positive
    if token_limit <= 0:
        token_limit = 2048
    
    chat_files_list = chat_files or []
    mentioned_fnames_set = set(mentioned_files) if mentioned_files else None
    mentioned_idents_set = set(mentioned_idents) if mentioned_idents else None

    # 2. If a specific list of other_files isn't provided, scan specified directories or root
    effective_other_files = []
    if other_files:
        effective_other_files = other_files
    else:
        # Use specified directories or default to project root
        directories_to_scan = scan_directories or [project_root]
        log.info(f"No other_files provided, scanning directories: {directories_to_scan}")
        
        for directory in directories_to_scan:
            abs_directory = str(Path(project_root) / directory) if directory != project_root else project_root
            if os.path.exists(abs_directory):
                files_in_dir = find_src_files(abs_directory, file_patterns)
                effective_other_files.extend(files_in_dir)
                log.info(f"Found {len(files_in_dir)} source files in {directory}")
            else:
                log.warning(f"Directory not found: {abs_directory}")

    # Enhanced debugging information
    if verbose:
        log.info(f"Project root: {project_root}")
        log.info(f"Chat files: {chat_files_list}")
        log.info(f"File patterns: {file_patterns or 'default source extensions'}")
        log.info(f"Scan directories: {scan_directories or ['project root']}")
        log.info(f"Effective other_files count: {len(effective_other_files)}")
        if effective_other_files:
            log.info(f"Sample files found: {effective_other_files[:5]}")

    # If after all that we have no files, we can exit early.
    if not chat_files_list and not effective_other_files:
        log.info("No files to process.")
        return {"map": "No files found to generate a map."}

    # 3. Resolve paths relative to project root
    root_path = Path(project_root).resolve()
    abs_chat_files = [str(root_path / f) for f in chat_files_list]
    abs_other_files = [str(root_path / f) for f in effective_other_files]
    
    # Remove any chat files from the other_files list to avoid duplication
    abs_chat_files_set = set(abs_chat_files)
    abs_other_files = [f for f in abs_other_files if f not in abs_chat_files_set]

    # 4. Instantiate and run RepoMap
    try:
        repo_mapper = RepoMap(
            map_tokens=token_limit,
            root=str(root_path),
            token_counter_func=lambda text: count_tokens(text, "gpt-4"),
            file_reader_func=read_text,
            output_handler_funcs={'info': log.info, 'warning': log.warning, 'error': log.error, 'debug': log.debug},
            verbose=verbose,
            exclude_unranked=exclude_unranked,
            max_context_window=max_context_window
        )
    except Exception as e:
        log.exception(f"Failed to initialize RepoMap for project '{project_root}': {e}")
        return {"error": f"Failed to initialize RepoMap: {str(e)}"}

    try:
        map_content, file_report = await asyncio.to_thread(
            repo_mapper.get_repo_map,
            chat_files=abs_chat_files,
            other_files=abs_other_files,
            mentioned_fnames=mentioned_fnames_set,
            mentioned_idents=mentioned_idents_set,
            force_refresh=force_refresh
        )
        
        # Convert FileReport to dictionary for JSON serialization
        report_dict = {
            "excluded": file_report.excluded,
            "definition_matches": file_report.definition_matches,
            "reference_matches": file_report.reference_matches,
            "total_files_considered": file_report.total_files_considered
        }
        
        return {
            "map": map_content or "No repository map could be generated.",
            "report": report_dict
        }
    except Exception as e:
        log.exception(f"Error generating repository map for project '{project_root}': {e}")
        return {"error": f"Error generating repository map: {str(e)}"}
    
@mcp.tool()
async def search_identifiers(
    project_root: str,
    query: str,
    max_results: int = 50,
    context_lines: int = 2,
    include_definitions: bool = True,
    include_references: bool = True
) -> Dict[str, Any]:
    """Search for identifiers in code files. Get back a list of matching identifiers with their file, line number, and context.
       When searching, just use the identifier name without any special characters, prefixes or suffixes. The search is 
       case-insensitive.

    Args:
        project_root: Root directory of the project to search.  (must be an absolute path!)
        query: Search query (identifier name)
        max_results: Maximum number of results to return
        context_lines: Number of lines of context to show
        include_definitions: Whether to include definition occurrences
        include_references: Whether to include reference occurrences
    
    Returns:
        Dictionary containing search results or error message
    """
    if not os.path.isdir(project_root):
        return {"error": f"Project root directory not found: {project_root}"}

    try:
        # Initialize RepoMap with search-specific settings
        repo_map = RepoMap(
            root=project_root,
            token_counter_func=lambda text: count_tokens(text, "gpt-4"),
            file_reader_func=read_text,
            output_handler_funcs={'info': log.info, 'warning': log.warning, 'error': log.error, 'debug': log.debug},
            verbose=False,
            exclude_unranked=True
        )

        # Find all source files in the project with enhanced filtering
        all_files = find_src_files(project_root, ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb', '.php', '.swift', '.scala', '.kt'])
        
        # Get all tags (definitions and references) for all files
        all_tags = []
        for file_path in all_files:
            rel_path = str(Path(file_path).relative_to(project_root))
            tags = repo_map.get_tags(file_path, rel_path)
            all_tags.extend(tags)

        # Filter tags based on search query and options
        matching_tags = []
        query_lower = query.lower()
        
        for tag in all_tags:
            if query_lower in tag.name.lower():
                if (tag.kind == "def" and include_definitions) or \
                   (tag.kind == "ref" and include_references):
                    matching_tags.append(tag)

        # Sort by relevance (definitions first, then references)
        matching_tags.sort(key=lambda x: (x.kind != "def", x.name.lower().find(query_lower)))

        # Limit results
        matching_tags = matching_tags[:max_results]

        # Format results with context
        results = []
        for tag in matching_tags:
            file_path = str(Path(project_root) / tag.rel_fname)
            
            # Calculate context range based on context_lines parameter
            start_line = max(1, tag.line - context_lines)
            end_line = tag.line + context_lines
            context_range = list(range(start_line, end_line + 1))
            
            context = repo_map.render_tree(
                file_path,
                tag.rel_fname,
                context_range
            )
            
            if context:
                results.append({
                    "file": tag.rel_fname,
                    "line": tag.line,
                    "name": tag.name,
                    "kind": tag.kind,
                    "context": context
                })

        return {"results": results}

    except Exception as e:
        log.exception(f"Error searching identifiers in project '{project_root}': {e}")
        return {"error": f"Error searching identifiers: {str(e)}"}    

# --- Main Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="RepoMap MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5s %(asctime)-15s %(name)s:%(funcName)s:%(lineno)d - %(message)s')
        logging.getLogger('fastmcp').setLevel(logging.INFO)
        logging.getLogger('fastmcp.server').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('fastmcp').setLevel(logging.ERROR)
        logging.getLogger('fastmcp.server').setLevel(logging.ERROR)

    # Run the MCP server
    log.info("Starting FastMCP server...")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")

if __name__ == "__main__":
    main()
