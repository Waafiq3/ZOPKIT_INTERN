"""
Test Query Examples for Invoice Management
Shows how to properly query the invoice that was created
"""

# Based on your logs, here are the correct query formats:

print("🔍 Correct Query Examples for Your Invoice:")
print("="*80)

document_id = "68e1144110cd4c5bcaa12efd"  # From your logs

print(f"✅ Option 1: Specific Document ID Query")
print(f"   Query: 'Show me invoice details for document ID {document_id}'")
print(f"   -> This will call: GET /api/invoice_management?_id={document_id}")
print()

print(f"✅ Option 2: Context-aware Query")
print(f"   Query: 'Get my invoice management information for ID {document_id}'")
print(f"   -> This will call: GET /api/invoice_management?_id={document_id}")
print()

print(f"✅ Option 3: Reference-based Query")
print(f"   Query: 'I want to see the invoice I just created: {document_id}'")
print(f"   -> This will call: GET /api/invoice_management?_id={document_id}")
print()

print(f"✅ Option 4: Field-based Query")
print(f"   Query: 'Show me invoice INV1001 details'")
print(f"   -> This will call: GET /api/invoice_management?invoice_id=INV1001")
print()

print(f"✅ Option 5: Employee-based Query")
print(f"   Query: 'Show all invoices for employee EMP001'")
print(f"   -> This will call: GET /api/invoice_management?employee_id=EMP001")
print()

print("❌ Why Your Query Didn't Work:")
print("-" * 40)
print("   Query: 'i want to get my details .please show me my information'")
print("   Problem: Too generic - system doesn't know:")
print("   • Which collection? (invoice_management, user_registration, etc.)")
print("   • Which record? (document ID, invoice ID, employee ID, etc.)")
print()

print("💡 Solution:")
print("-" * 20)
print("Be specific about:")
print("1. WHAT you want (invoice, user, supplier, etc.)")
print("2. WHICH record (document ID, invoice ID, email, etc.)")
print()

print("🌐 Expected API Behavior:")
print("-" * 30)
print("✅ Specific Query -> Triggers Query Node -> Calls GET /api/invoice_management")
print("❌ Generic Query -> Stays in general chat -> No API call")
print()

print("🎯 Try This in Your Chat:")
print("-" * 35)
print(f"Copy and paste: Show me invoice details for document ID {document_id}")