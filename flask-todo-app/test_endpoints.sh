#!/bin/bash

# Test script for In-Memory Todo App endpoints
# This script tests all available endpoints to verify the application is working

set -e

BASE_URL="http://localhost:5000"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}📝 Testing In-Memory Todo App Endpoints${NC}"
echo "========================================"
echo ""

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testing:${NC} $description"
    echo -e "  ${BOLD}$method${NC} $BASE_URL$path"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$path")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$path")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✅ Success${NC} (HTTP $http_code)"
        echo "  Response: $body" | head -c 150
        if [ ${#body} -gt 150 ]; then
            echo "..."
        else
            echo ""
        fi
    else
        echo -e "  ${RED}❌ Failed${NC} (HTTP $http_code)"
        echo "  Response: $body"
    fi
    echo ""
}

# Check if the server is running
echo "Checking if server is running..."
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Server is not running at $BASE_URL${NC}"
    echo ""
    echo "Please start the server first:"
    echo "  python app.py"
    echo ""
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test all endpoints
echo -e "${BLUE}=== Basic Endpoints ===${NC}"
test_endpoint "GET" "/health" "" "Health Check"
test_endpoint "GET" "/api/info" "" "API Information"
test_endpoint "GET" "/api/stats" "" "Todo Statistics (Empty)"

echo -e "${BLUE}=== Creating Todos ===${NC}"
test_endpoint "POST" "/api/todos" '{"title":"Buy groceries","description":"Milk, eggs, bread"}' "Create Todo #1"
test_endpoint "POST" "/api/todos" '{"title":"Write report","description":"Q4 financial report"}' "Create Todo #2"
test_endpoint "POST" "/api/todos" '{"title":"Call dentist","description":"Schedule appointment"}' "Create Todo #3"

echo -e "${BLUE}=== Reading Todos ===${NC}"
test_endpoint "GET" "/api/todos" "" "List All Todos"
test_endpoint "GET" "/api/todos/1" "" "Get Todo #1"
test_endpoint "GET" "/api/todos/2" "" "Get Todo #2"

echo -e "${BLUE}=== Updating Todos ===${NC}"
test_endpoint "PUT" "/api/todos/1" '{"title":"Buy groceries","description":"Milk, eggs, bread, butter","completed":false}' "Update Todo #1"
test_endpoint "PATCH" "/api/todos/2" "" "Toggle Todo #2 Completion"
test_endpoint "PATCH" "/api/todos/2" "" "Toggle Todo #2 Again"

echo -e "${BLUE}=== Statistics ===${NC}"
test_endpoint "GET" "/api/stats" "" "Todo Statistics (With Data)"

echo -e "${BLUE}=== Deleting Todos ===${NC}"
test_endpoint "DELETE" "/api/todos/3" "" "Delete Todo #3"
test_endpoint "GET" "/api/todos" "" "List Todos After Deletion"

echo "========================================"
echo -e "${BOLD}✅ All tests completed!${NC}"
echo ""
echo -e "${YELLOW}⏱️  Note: Todos will expire after 5 minutes${NC}"
echo ""
echo "To test with chaos injection:"
echo "  1. Configure your emissary service"
echo "  2. Add fault configurations (e.g., app.getTodos, app.createTodo)"
echo "  3. Run this script again to see the effects"
echo ""
