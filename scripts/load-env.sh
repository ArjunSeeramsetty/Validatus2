#!/bin/bash
# Safe environment variable loading utility

# Function to safely load environment variables from .env file
load_env_file() {
    local env_file="$1"
    
    if [ ! -f "$env_file" ]; then
        echo "❌ Environment file not found: $env_file" >&2
        return 1
    fi
    
    echo "📝 Loading environment variables from $env_file..."
    
    # Use set -a to automatically export all variables
    set -a
    source "$env_file" || {
        set +a
        echo "❌ Failed to source environment file" >&2
        return 1
    }
    set +a
    
    echo "✅ Environment variables loaded successfully"
    return 0
}

# Alternative robust approach for parsing .env files with special characters
load_env_file_robust() {
    local env_file="$1"
    
    if [ ! -f "$env_file" ]; then
        echo "❌ Environment file not found: $env_file" >&2
        return 1
    fi
    
    echo "📝 Loading environment variables from $env_file (robust mode)..."
    
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^#.*$ ]] && continue
        [[ -z $key ]] && continue
        
        # Remove any leading/trailing whitespace
        key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Handle quoted values
        if [[ $value =~ ^\".*\"$ ]] || [[ $value =~ ^\'.*\'$ ]]; then
            value="${value:1:-1}"  # Remove first and last character (quotes)
        fi
        
        # Export the variable
        export "$key=$value"
    done < "$env_file"
    
    echo "✅ Environment variables loaded successfully (robust mode)"
    return 0
}

# Main function - can be called directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    # Script is being run directly
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <env_file> [robust]"
        echo "  env_file: Path to .env file"
        echo "  robust: Use robust parsing mode (optional)"
        exit 1
    fi
    
    env_file="$1"
    mode="${2:-normal}"
    
    if [ "$mode" == "robust" ]; then
        load_env_file_robust "$env_file"
    else
        load_env_file "$env_file"
    fi
fi
