#!/usr/bin/env python3
import os
import pyodbc
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import List, Dict
import re

# Step 0: Load environment variables from .env file
load_dotenv()

# ===========================================
# 1. SERVER INITIALIZATION - Create the MCP server
# ===========================================
# Create server with name but consider adding instructions parameter
# Best practice: Add server instructions to help clients understand usage
mcp = FastMCP("pocket-dba-mcp-server")
# Could improve: mcp = FastMCP("pocket-dba-mcp-server", instructions="SQL database access tools")

# Step 1.1: Configure database connection parameters from environment variables
DB_CONFIG = {
    "server": os.getenv("MSSQL_SERVER"),
    "database": os.getenv("MSSQL_DATABASE"),
    "user": os.getenv("MSSQL_USER"),
    "password": os.getenv("MSSQL_PASSWORD"),
    "driver": os.getenv("MSSQL_DRIVER")
}

# Step 1.2: Define database connection function
def get_connection():
    """Create database connection"""
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']};"
        "TrustServerCertificate=yes"
    )
    return pyodbc.connect(conn_str, readonly=True)

# Step 1.3: Implement security validation for SQL queries
def is_read_only_query(query: str) -> bool:
    """Validate query is read-only"""
    clean_query = query.strip().upper()
    
    allowed_statements = ['SELECT', 'WITH', 'DECLARE']
    forbidden_statements = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 
        'ALTER', 'TRUNCATE', 'MERGE', 'UPSERT', 'REPLACE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'SP_'
    ]
    
    starts_with_allowed = any(clean_query.startswith(stmt) for stmt in allowed_statements)
    if not starts_with_allowed:
        return False
        
    contains_forbidden = any(stmt in clean_query for stmt in forbidden_statements)
    if contains_forbidden:
        return False
        
    # Check for SQL injection patterns
    has_dangerous_chars = re.search(r';\s*\w+', clean_query)
    if has_dangerous_chars:
        return False
        
    return True

# Step 1.4: Helper function to list database tables
def list_tables_raw() -> str:
    """Raw function for listing all database tables"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME"
        )
        tables = cursor.fetchall()
        return "\n".join([f"{schema}.{table}" for schema, table in tables])

# Step 1.5: Helper function to get data from a table
def get_table_data_raw(table_name: str) -> str:
    """Raw function for getting top 100 rows from a table"""
    query = f"SELECT TOP 100 * FROM {table_name}"
    
    if not is_read_only_query(query):
        return "Error: Invalid table name"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        result = [",".join(columns)]
        result.extend([",".join(map(str, row)) for row in rows])
        return "\n".join(result)

# ===========================================
# 2. RESOURCES - Read-only data sources
# ===========================================
# Step 2.1: Define static resource for listing tables
# Best practice: Using clear URI patterns with namespaces
@mcp.resource("mssql://tables")
def list_tables() -> str:
    """List all database tables"""
    return list_tables_raw()

# Step 2.2: Define parameterized resource for table data
# Best practice: Using URI templates with parameters
@mcp.resource("mssql://table/{table_name}")
def get_table_data(table_name: str) -> str:
    """Get top 100 rows from a table"""
    return get_table_data_raw(table_name)

# Step 2.3: Helper function for relationship data
def get_relationships_raw(table_name: str) -> str:
    """Raw function for getting table relationships (foreign keys)"""
    # Validate table name format (schema.table or just table)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$', table_name):
        return "Error: Invalid table name format"
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Split table name if it contains schema
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
                where_clause = "AND fk.TABLE_SCHEMA = ? AND fk.TABLE_NAME = ?"
                params = (schema, table)
            else:
                where_clause = "AND fk.TABLE_NAME = ?"
                params = (table_name,)
            
            # Check if table exists first
            table_check_query = """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE 1=1 """ + where_clause.replace("fk.", "") + """
            """
            cursor.execute(table_check_query, params)
            if cursor.fetchone()[0] == 0:
                return f"Error: Table '{table_name}' not found"
            
            # Get foreign key relationships
            query = """
            SELECT 
                fk.CONSTRAINT_NAME,
                fk.COLUMN_NAME,
                pk.TABLE_SCHEMA + '.' + pk.TABLE_NAME as REFERENCED_TABLE,
                pk.COLUMN_NAME as REFERENCED_COLUMN
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE fk
                ON rc.CONSTRAINT_NAME = fk.CONSTRAINT_NAME
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE pk
                ON rc.UNIQUE_CONSTRAINT_NAME = pk.CONSTRAINT_NAME
            WHERE 1=1 """ + where_clause + """
            ORDER BY fk.CONSTRAINT_NAME, fk.ORDINAL_POSITION
            """
            
            cursor.execute(query, params)
            relationships = cursor.fetchall()
            
            # Format results
            result = ["CONSTRAINT_NAME,COLUMN_NAME,REFERENCED_TABLE,REFERENCED_COLUMN"]
            for rel in relationships:
                constraint_name, column_name, referenced_table, referenced_column = rel
                result.append(f"{constraint_name},{column_name},{referenced_table},{referenced_column}")
            
            return "\n".join(result)
            
    except Exception as e:
        return f"Error: {str(e)}"

# Step 2.4: Helper function for table structure
def describe_table_raw(table_name: str) -> str:
    """Raw function for describing table structure"""
    # Validate table name format (schema.table or just table)
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$', table_name):
        return "Error: Invalid table name format"
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Split table name if it contains schema
            if '.' in table_name:
                schema, table = table_name.split('.', 1)
                where_clause = "AND TABLE_SCHEMA = ? AND TABLE_NAME = ?"
                params = (schema, table)
            else:
                where_clause = "AND TABLE_NAME = ?"
                params = (table_name,)
            
            # Get column information
            query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH,
                NUMERIC_PRECISION,
                NUMERIC_SCALE,
                ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE 1=1 """ + where_clause + """
            ORDER BY ORDINAL_POSITION
            """
            
            cursor.execute(query, params)
            columns = cursor.fetchall()
            
            if not columns:
                return f"Error: Table '{table_name}' not found"
            
            # Format results
            result = ["COLUMN_NAME,DATA_TYPE,IS_NULLABLE,COLUMN_DEFAULT,MAX_LENGTH,PRECISION,SCALE"]
            for col in columns:
                col_name, data_type, is_nullable, default, max_len, precision, scale, _ = col
                max_len = str(max_len) if max_len else ""
                precision = str(precision) if precision else ""
                scale = str(scale) if scale else ""
                default = str(default) if default else ""
                
                result.append(f"{col_name},{data_type},{is_nullable},{default},{max_len},{precision},{scale}")
            
            return "\n".join(result)
            
    except Exception as e:
        return f"Error: {str(e)}"

# Step 2.5: Helper function for SQL execution
def execute_sql_raw(query: str) -> str:
    """Raw function for executing SQL queries"""
    if not is_read_only_query(query):
        return "Error: Only SELECT queries are allowed"
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            result = [",".join(columns)]
            result.extend([",".join(map(str, row)) for row in rows])
            return "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"

# ===========================================
# 3. TOOLS - Executable functions for actions
# ===========================================
# Step 3.1: Define tool for relationship data
# Could improve: Add type annotations with Pydantic Field for better schema generation
@mcp.tool()
def get_relationships(table_name: str) -> str:
    """Get foreign key relationships for a table"""
    return get_relationships_raw(table_name)

# Step 3.2: Define tool for table structure
# Could improve: Return structured data (dict) instead of string for better client usage
@mcp.tool()
def describe_table(table_name: str) -> str:
    """Describe table structure (columns, data types, constraints)"""
    return describe_table_raw(table_name)

# Step 3.3: Define tool for SQL execution
# Best practice: Using readOnlyHint=True would be ideal but not implemented here
@mcp.tool()
def execute_sql(query: str) -> str:
    """Execute a READ-ONLY SQL query (SELECT only)"""
    return execute_sql_raw(query)

# ===========================================
# 4. TRANSPORT HANDLER - Run the server
# ===========================================
# Step 4: Start the server with default stdio transport
# Could improve: Specify transport explicitly for clarity: mcp.run(transport="stdio")
if __name__ == "__main__":
    mcp.run()