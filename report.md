# RepoMap Project Report

## 1. Project Overview

RepoMap is a command-line tool and MCP server designed to help AI Language Models (LLMs) understand and navigate complex codebases. It generates a "map" of a software repository, highlighting important files, code definitions (classes, functions, etc.), and their relationships.

### Key Features:

*   **Code Analysis**: Uses Tree-sitter to accurately parse source code and extract definitions and references.
*   **Relevance Ranking**: Employs the PageRank algorithm to rank files and code elements by importance, ensuring the most relevant information is prioritized.
*   **Token-Aware**: The output is optimized to fit within the token limits of LLMs.
*   **Caching**: Uses persistent caching for fast subsequent analysis of unchanged files.
*   **Multi-Language Support**: Supports a wide range of programming languages.
*   **MCP Server**: Can run as a server, allowing other applications (like Roo) to access its functionality.

## 2. How It Works

RepoMap performs the following steps to generate a repository map:

1.  **File Discovery**: It scans the specified directory for source code files.
2.  **Code Parsing**: It uses Tree-sitter to parse the code in each file and identify code definitions (e.g., functions, classes) and references between them.
3.  **Graph Building**: It constructs a graph where each file is a node, and a reference from code in one file to a definition in another file is a directed edge.
4.  **Ranking**: It applies the PageRank algorithm to this graph. Files that are frequently referenced by other important files will have a higher rank.
5.  **Output Generation**: It generates a text-based map that shows the most important files and their key definitions, ordered by rank. The amount of information is tailored to fit within a specified token limit.

## 3. Running the MCP Server

The project includes a `run_server.sh` script to simplify the setup and execution process.

### How to Run

1.  **Make the script executable** (if you haven't already):
    ```bash
    chmod +x run_server.sh
    ```

2.  **Run the script from your terminal**:
    ```bash
    ./run_server.sh
    ```

The script will automatically:
*   Create a Python virtual environment (`venv`) if it doesn't exist.
*   Install or update the required dependencies from `requirements.txt`.
*   Launch the MCP server.

Any arguments passed to `run_server.sh` will be forwarded to the underlying `repomap_server.py` script.

### Integrating with RooCode

To add RepoMap as an MCP server in RooCode, you need to update your MCP settings file.

1.  **Find the absolute path** to the `run_server.sh` script. You can get this by running the following command in your terminal from the project directory:
    ```bash
    readlink -f run_server.sh
    ```

2.  **Update your MCP settings file** with the following configuration:

    ```json
    {
      "mcpServers": {
        "RepoMapper": {
          "disabled": false,
          "timeout": 60,
          "type": "stdio",
          "command": "/absolute/path/to/run_server.sh"
        }
      }
    }
    ```

    **Important**: Replace `/absolute/path/to/run_server.sh` with the actual path you obtained in the previous step.

    Using `run_server.sh` as the command ensures that the virtual environment and dependencies are correctly managed every time RooCode starts the server.

### Available Tools

The MCP server exposes two main tools:

#### a. `repo_map`

This tool generates a repository map.

**Parameters:**

*   `project_root` (str): The absolute path to the root directory of the project you want to map.
*   `chat_files` (List[str], optional): A list of files that are currently the focus of the conversation. These files are given the highest priority in the ranking.
*   `other_files` (List[str], optional): A list of other files to consider. If not provided, RepoMap will scan the entire `project_root`.
*   `token_limit` (int, optional): The maximum number of tokens for the generated map. Defaults to 8192.
*   `mentioned_files` (List[str], optional): Files that have been explicitly mentioned, which get a ranking boost.
*   `mentioned_idents` (List[str], optional): Identifiers (function/class names) that have been explicitly mentioned, also getting a boost.
*   `exclude_unranked` (bool, optional): If `true`, files with a rank of 0 are excluded. Defaults to `false`.
*   `force_refresh` (bool, optional): If `true`, the cache is ignored. Defaults to `false`.

**Example MCP Request:**

```json
{
  "tool": "repo_map",
  "project_root": "/path/to/your/project",
  "chat_files": ["src/main.py"],
  "token_limit": 4096
}
```

#### b. `search_identifiers`

This tool searches for specific identifiers (functions, classes, variables) within the codebase.

**Parameters:**

*   `project_root` (str): The absolute path to the project directory.
*   `query` (str): The identifier name to search for.
*   `max_results` (int, optional): The maximum number of matches to return. Defaults to 50.
*   `context_lines` (int, optional): The number of lines of code to show around each match. Defaults to 2.
*   `include_definitions` (bool, optional): Whether to include definition sites. Defaults to `true`.
*   `include_references` (bool, optional): Whether to include reference sites. Defaults to `true`.

**Example MCP Request:**

```json
{
  "tool": "search_identifiers",
  "project_root": "/path/to/your/project",
  "query": "calculate_total"
}
```

## 4. How an AI LLM Should Use It

As an AI LLM, you should use the RepoMap server to build a mental model of a codebase before you start making changes.

### Strategy for Using RepoMap

1.  **Initial Exploration (`repo_map`)**: When you are first introduced to a new project, your first step should be to get a high-level overview.
    *   Call the `repo_map` tool with the `project_root`. Don't specify any `chat_files` or `other_files` at this stage. This will give you a map of the most important files in the entire repository.
    *   **Example**: `repo_map(project_root="/path/to/project")`

2.  **Focusing on Specific Areas (`repo_map` with `chat_files`)**: Once you have a general idea of the project structure, or if the user's request points to a specific file, use the `chat_files` parameter to get a more detailed and focused map.
    *   This will re-run the PageRank algorithm, giving a high priority to the files you're currently interested in and showing you what other files are most relevant to them.
    *   **Example**: `repo_map(project_root="/path/to/project", chat_files=["src/api/routes.py"])`

3.  **Finding Specific Code (`search_identifiers`)**: When you need to find where a specific function or class is defined or used, use the `search_identifiers` tool.
    *   This is much more efficient than manually reading through files.
    *   The results will show you the exact location (file and line number) and provide context.
    *   **Example**: `search_identifiers(project_root="/path/to/project", query="DatabaseConnection")`

### Interpreting the Output

*   **`repo_map` Output**: The map shows you which files are central to the project's architecture. Files with a high "Rank value" are likely to be important. The listed definitions give you a quick summary of what each file does.
*   **`search_identifiers` Output**: The `kind` field in the results tells you if the match is a `def` (definition) or a `ref` (reference). This is crucial for understanding the code's structure.

By following this strategy, you can efficiently understand a new codebase, identify the most relevant files for a given task, and locate specific pieces of code, leading to more accurate and effective code generation and modification.