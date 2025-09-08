# RepoMapper MCP Server Analysis - Ecne-AI-Report-Builder Project

## Executive Summary

The RepoMapper MCP server successfully works on its own codebase but fails to generate repository maps for the Ecne-AI-Report-Builder project. The server finds 7216 files but processes 0 definitions and 0 references, indicating a fundamental issue with file parsing or Tree-sitter language support.

## Key Findings

### 1. MCP Server Functionality Status

**✅ Working Correctly:**
- **Search functionality**: Works on both projects (found `RepoMap` class in repomap_class.py)
- **Repository mapping**: Works on RepoMapper project itself (23 definitions, 154 references)
- **Protocol communication**: MCP server responds correctly to requests

**❌ Not Working:**
- **Repository mapping**: Fails on Ecne-AI-Report-Builder project (0 definitions, 0 references)
- **File processing**: 7216 files found but none processed successfully

### 2. Test Results Comparison

| Test Scenario | RepoMapper Project | Ecne-AI-Report-Builder Project |
|---------------|-------------------|-------------------------------|
| **Files Found** | 67 files | 7216 files |
| **Definitions** | 23 matches | 0 matches |
| **References** | 154 matches | 0 matches |
| **Search Results** | ✅ Found "RepoMap" | ✅ Found identifiers (but empty results) |
| **Map Generation** | ✅ Successful | ❌ Failed |

### 3. Root Cause Analysis

The primary issue appears to be in the **file scanning and parsing pipeline**:

1. **File Discovery**: The `find_src_files()` function finds 7216 files, which suggests it's scanning too broadly
2. **Language Detection**: Tree-sitter may not be recognizing the file types correctly
3. **SCM Query Files**: Missing or incompatible SCM files for the languages used in Ecne-AI-Report-Builder
4. **Cache Issues**: The `.repomap.tags.cache.v1/` directory might contain stale or corrupted data

### 4. Technical Issues Identified

#### 4.1 File Scanning Over-inclusiveness
The `find_src_files()` function in [`repomap_server.py:17`](repomap_server.py:17) is too permissive:
- Includes all non-hidden files without proper filtering
- No extension-based filtering for source code files
- Scans research documents, static files, and other non-code content

#### 4.2 Tree-sitter Language Support
The Ecne-AI-Report-Builder project contains:
- Python files (`.py`)
- JavaScript/CSS/HTML files (web interface)
- Documentation files (`.md`, `.txt`)
- Research documents (`.docx`, `.pdf`)
- Configuration files (`.yml`, `.json`)

Potential language detection issues for:
- Flask web application structure
- Mixed content types
- Non-standard file extensions

#### 4.3 Cache Directory Issues
The project contains a `.repomap.tags.cache.v1/` directory, suggesting previous failed attempts that may have corrupted the cache.

### 5. Impact Assessment

**High Severity**: The MCP server cannot generate repository maps for external projects, severely limiting its usefulness for AI coding assistants.

**Medium Severity**: Search functionality works but returns empty results due to parsing failures.

### 6. Recommendations for Fixing

#### 6.1 Immediate Fixes
1. **Improve File Filtering**: Enhance `find_src_files()` to filter by known source code extensions
2. **Cache Management**: Add cache invalidation or force refresh options
3. **Error Logging**: Add more verbose error reporting for parsing failures

#### 6.2 Medium-term Improvements
1. **Extension-based Filtering**: Implement proper file type detection
2. **Language Pack Validation**: Ensure all required Tree-sitter grammars are available
3. **Fallback Mechanisms**: Better regex fallbacks for unsupported languages

#### 6.3 Long-term Enhancements
1. **Configurable File Patterns**: Allow users to specify file patterns to include/exclude
2. **Performance Optimization**: Handle large codebases more efficiently
3. **Language Pack Management**: Automatic download of missing Tree-sitter grammars

### 7. Testing Strategy

To verify fixes, implement the following test plan:

1. **Unit Tests**: Test file filtering with various project structures
2. **Integration Tests**: Verify MCP server works with different project types
3. **Regression Tests**: Ensure RepoMapper self-analysis still works
4. **Performance Tests**: Handle large file counts efficiently

### 8. Sample Failed Output Analysis

From the test runs:
```json
{
  "map": "No repository map could be generated.",
  "report": {
    "excluded": {},
    "definition_matches": 0,
    "reference_matches": 0,
    "total_files_considered": 7216
  }
}
```

This indicates:
- No files were excluded (all 7216 were "considered")
- But 0 definitions and 0 references were found
- The binary search in `get_ranked_tags_map_uncached()` failed to find any content

### 9. Conclusion

The RepoMapper MCP server has a fundamental issue with file processing for external projects. While it works perfectly on its own codebase, it fails to parse and analyze the Ecne-AI-Report-Builder project due to:

1. **Overly broad file scanning** that includes non-code files
2. **Potential language detection failures** with mixed content types
3. **Missing or incompatible SCM query files** for the project's languages

The fix requires improving the file filtering logic and ensuring proper language support for diverse project structures.
## 10. Implementation Recommendations

### 10.1 Fix the File Scanning Function

**Current Issue**: [`find_src_files()`](repomap_server.py:17) includes all non-hidden files without proper filtering.

**Recommended Fix**:
```python
def find_src_files(directory: str) -> List[str]:
    """Find source files in a directory with proper filtering."""
    if not os.path.isdir(directory):
        return [directory] if os.path.isfile(directory) and is_source_file(directory) else []
    
    src_files = []
    source_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', 
                        '.go', '.rs', '.rb', '.php', '.swift', '.scala', '.kt'}
    
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
            'node_modules', '__pycache__', 'venv', 'env', '.git',
            'dist', 'build', 'target', 'out', 'bin', 'obj'
        }]
        
        for file in files:
            if not file.startswith('.'):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in source_extensions:
                    src_files.append(os.path.join(root, file))
    
    return src_files

def is_source_file(filepath: str) -> bool:
    """Check if a file is a source code file."""
    source_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', 
                        '.go', '.rs', '.rb', '.php', '.swift', '.scala', '.kt'}
    return os.path.splitext(filepath)[1].lower() in source_extensions
```

### 10.2 Add Better Error Logging

**Current Issue**: Insufficient logging makes debugging difficult.

**Recommended Enhancement**:
```python
# In repo_map function, add detailed logging
log.info(f"Project root: {project_root}")
log.info(f"Found {len(effective_other_files)} potential source files")

# In get_tags_raw, add language detection logging
if not lang:
    log.warning(f"Language not supported for {fname}, extension: {os.path.splitext(fname)[1]}")
    return []
```

### 10.3 Implement Cache Management

**Current Issue**: Stale cache may cause issues.

**Recommended Solution**:
```python
# Add cache clearing option to MCP server
@mcp.tool()
async def clear_cache(project_root: str) -> Dict[str, Any]:
    """Clear the RepoMap cache for a project."""
    cache_dir = Path(project_root) / TAGS_CACHE_DIR
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        return {"status": "success", "message": f"Cache cleared for {project_root}"}
    return {"status": "info", "message": "No cache found to clear"}
```

### 10.4 Add Configurable File Patterns

**Recommended Enhancement**:
```python
# Add configurable file patterns to MCP server
@mcp.tool()
async def repo_map(
    project_root: str,
    chat_files: Optional[List[str]] = None,
    other_files: Optional[List[str]] = None,
    token_limit: Any = 2048,
    exclude_unranked: bool = False,
    force_refresh: bool = False,
    mentioned_files: Optional[List[str]] = None,
    mentioned_idents: Optional[List[str]] = None,
    verbose: bool = False,
    max_context_window: Optional[int] = None,
    file_patterns: Optional[List[str]] = None  # New parameter
) -> Dict[str, Any]:
    # Use custom patterns or default to source extensions
    patterns = file_patterns or [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h"]
```

### 10.5 Testing Plan

1. **Unit Tests**: Create tests for the improved file filtering
2. **Integration Tests**: Test with various project structures
3. **Regression Tests**: Ensure existing functionality still works
4. **Performance Tests**: Verify handling of large codebases

### 10.6 Deployment Strategy

1. **Phase 1**: Implement file filtering and enhanced logging
2. **Phase 2**: Add cache management tools
3. **Phase 3**: Implement configurable file patterns
4. **Phase 4**: Add comprehensive testing

## 11. Expected Outcomes

After implementing these fixes:

1. **✅ Reduced File Count**: From 7216 to ~50-100 actual source files
2. **✅ Successful Parsing**: Tree-sitter should find definitions and references
3. **✅ Working Repository Maps**: Proper map generation for external projects
4. **✅ Better Debugging**: Detailed logs for troubleshooting
5. **✅ Configurable**: Users can customize file inclusion patterns

## 12. Timeline Estimate

- **Immediate Fixes (1-2 days)**: File filtering and enhanced logging
- **Medium-term (1 week)**: Cache management and configuration options
- **Long-term (2 weeks)**: Comprehensive testing and documentation

The RepoMapper MCP server has strong potential but needs these fundamental fixes to work reliably with diverse codebases.