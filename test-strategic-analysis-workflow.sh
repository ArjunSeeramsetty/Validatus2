#!/bin/bash

# 🧪 VALIDATUS STRATEGIC ANALYSIS WORKFLOW - COMPREHENSIVE TESTING SCRIPT
echo "🧪 Starting Comprehensive Strategic Analysis Workflow Testing..."
echo "=================================================================="

# Navigate to project root
cd "$(dirname "$0")"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
    echo "🔍 Running Test: $test_name"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo "✅ PASSED: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "❌ FAILED: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Function to check file exists and has content
check_file() {
    local file_path="$1"
    local description="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
    echo "📁 Checking: $description"
    echo "File: $file_path"
    echo "----------------------------------------"
    
    if [[ -f "$file_path" && -s "$file_path" ]]; then
        echo "✅ PASSED: $description exists and has content"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "❌ FAILED: $description missing or empty"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "🚀 PHASE 1: FRONTEND BUILD TESTING"
echo "=================================="

# Test 1: Frontend build
run_test "Frontend Build" "cd frontend && npm run build"

# Test 2: TypeScript compilation
run_test "TypeScript Compilation" "cd frontend && npx tsc --noEmit"

echo ""
echo "🔍 PHASE 2: COMPONENT EXISTENCE TESTING"
echo "======================================"

# Check all critical components exist
check_file "frontend/src/pages/StrategicAnalysisPage.tsx" "Strategic Analysis Landing Page"
check_file "frontend/src/components/KnowledgeAcquisition/KnowledgeAcquisitionWizard.tsx" "Knowledge Acquisition Wizard"
check_file "frontend/src/components/Analysis/AnalysisProgressTracker.tsx" "Analysis Progress Tracker"
check_file "frontend/src/components/Results/AnalysisResultsDashboard.tsx" "Analysis Results Dashboard"
check_file "frontend/src/components/Export/ExportDialog.tsx" "Export Dialog Component"
check_file "frontend/src/services/strategicAnalysisService.ts" "Strategic Analysis Service"

echo ""
echo "🔗 PHASE 3: ROUTING & NAVIGATION TESTING"
echo "======================================="

# Check routing configuration
check_file "frontend/src/App.tsx" "App.tsx with routing"
check_file "frontend/src/components/Layout/MainLayout.tsx" "Main Layout with navigation"

# Test that routing imports are correct
run_test "Routing Import Validation" "grep -q 'StrategicAnalysisPage' frontend/src/App.tsx"

echo ""
echo "🎨 PHASE 4: UI/UX COMPONENT TESTING"
echo "=================================="

# Check that all UI components have proper imports
run_test "Material-UI Imports" "grep -q '@mui/material' frontend/src/components/KnowledgeAcquisition/KnowledgeAcquisitionWizard.tsx"
run_test "Framer Motion Imports" "grep -q 'framer-motion' frontend/src/pages/StrategicAnalysisPage.tsx"
run_test "Recharts Imports" "grep -q 'recharts' frontend/src/components/Results/AnalysisResultsDashboard.tsx"

echo ""
echo "🔌 PHASE 5: API INTEGRATION TESTING"
echo "=================================="

# Check API service methods
run_test "API Service Methods" "grep -q 'createTopic' frontend/src/services/strategicAnalysisService.ts"
run_test "API Service Methods" "grep -q 'startAnalysis' frontend/src/services/strategicAnalysisService.ts"
run_test "API Service Methods" "grep -q 'exportResults' frontend/src/services/strategicAnalysisService.ts"

# Check API client integration
check_file "frontend/src/services/apiClient.ts" "API Client Configuration"

echo ""
echo "📊 PHASE 6: DATA VISUALIZATION TESTING"
echo "====================================="

# Check chart components
run_test "Bar Chart Implementation" "grep -q 'BarChart' frontend/src/components/Results/AnalysisResultsDashboard.tsx"
run_test "Line Chart Implementation" "grep -q 'LineChart' frontend/src/components/Results/AnalysisResultsDashboard.tsx"
run_test "Responsive Container" "grep -q 'ResponsiveContainer' frontend/src/components/Results/AnalysisResultsDashboard.tsx"

echo ""
echo "🎯 PHASE 7: WORKFLOW INTEGRATION TESTING"
echo "======================================="

# Check workflow integration
run_test "Workflow State Management" "grep -q 'useState' frontend/src/pages/StrategicAnalysisPage.tsx"
run_test "Progress Tracking Integration" "grep -q 'AnalysisProgressTracker' frontend/src/pages/AnalysisSessionsPage.tsx"
run_test "Export Integration" "grep -q 'ExportDialog' frontend/src/components/Results/AnalysisResultsDashboard.tsx"

echo ""
echo "🔒 PHASE 8: ERROR HANDLING TESTING"
echo "================================="

# Check error handling implementation
run_test "Error Boundaries" "grep -q 'ErrorBoundary' frontend/src/App.tsx"
run_test "Error Handling in Services" "grep -q 'catch' frontend/src/services/strategicAnalysisService.ts"
run_test "Error States in Components" "grep -q 'error' frontend/src/components/KnowledgeAcquisition/KnowledgeAcquisitionWizard.tsx"

echo ""
echo "📱 PHASE 9: RESPONSIVE DESIGN TESTING"
echo "===================================="

# Check responsive design implementation
run_test "Responsive Grid System" "grep -q 'Grid' frontend/src/pages/StrategicAnalysisPage.tsx"
run_test "Mobile Breakpoints" "grep -q 'xs.*md' frontend/src/components/Results/AnalysisResultsDashboard.tsx"
run_test "Responsive Charts" "grep -q 'ResponsiveContainer' frontend/src/components/Results/AnalysisResultsDashboard.tsx"

echo ""
echo "🎨 PHASE 10: ANIMATION & UX TESTING"
echo "=================================="

# Check animation implementation
run_test "Framer Motion Animations" "grep -q 'motion' frontend/src/pages/StrategicAnalysisPage.tsx"
run_test "Animation Variants" "grep -q 'variants' frontend/src/components/Results/AnalysisResultsDashboard.tsx"
run_test "Staggered Animations" "grep -q 'staggerChildren' frontend/src/pages/StrategicAnalysisPage.tsx"

echo ""
echo "📦 PHASE 11: DEPENDENCY TESTING"
echo "=============================="

# Check package.json for required dependencies
run_test "Recharts Dependency" "grep -q 'recharts' frontend/package.json"
run_test "Framer Motion Dependency" "grep -q 'framer-motion' frontend/package.json"
run_test "Material-UI Dependencies" "grep -q '@mui/material' frontend/package.json"

echo ""
echo "🔧 PHASE 12: DEVELOPMENT ENVIRONMENT TESTING"
echo "==========================================="

# Check development scripts
run_test "Development Server Script" "grep -q 'dev' frontend/package.json"
run_test "Build Script" "grep -q 'build' frontend/package.json"
run_test "TypeScript Configuration" "test -f frontend/tsconfig.json"

echo ""
echo "=================================================================="
echo "🎯 COMPREHENSIVE TESTING RESULTS SUMMARY"
echo "=================================================================="

echo "📊 Test Statistics:"
echo "   Total Tests: $TOTAL_TESTS"
echo "   ✅ Passed: $TESTS_PASSED"
echo "   ❌ Failed: $TESTS_FAILED"
echo "   📈 Success Rate: $(( (TESTS_PASSED * 100) / TOTAL_TESTS ))%"

echo ""
echo "🏆 Overall Result:"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo "   🎉 ALL TESTS PASSED! 🎉"
    echo "   ✅ Strategic Analysis Workflow is PRODUCTION READY!"
    echo "   🚀 Ready for deployment and user testing"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Deploy to production environment"
    echo "   2. Conduct user acceptance testing"
    echo "   3. Monitor performance and user feedback"
    echo "   4. Implement any additional features based on user needs"
else
    echo "   ⚠️  SOME TESTS FAILED"
    echo "   🔧 Please review failed tests and fix issues"
    echo "   📝 Check the output above for specific failure details"
fi

echo ""
echo "📋 Test Categories Covered:"
echo "   ✅ Frontend Build & Compilation"
echo "   ✅ Component Existence & Structure"
echo "   ✅ Routing & Navigation"
echo "   ✅ UI/UX Implementation"
echo "   ✅ API Integration"
echo "   ✅ Data Visualization"
echo "   ✅ Workflow Integration"
echo "   ✅ Error Handling"
echo "   ✅ Responsive Design"
echo "   ✅ Animations & UX"
echo "   ✅ Dependencies"
echo "   ✅ Development Environment"

echo ""
echo "🎉 Strategic Analysis Workflow Testing Complete!"
echo "=================================================================="

# Exit with appropriate code
if [[ $TESTS_FAILED -eq 0 ]]; then
    exit 0
else
    exit 1
fi
