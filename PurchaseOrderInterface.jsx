import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, FileText, Check, X, Calendar, Package, DollarSign, Building } from 'lucide-react';

// Purchase Order Interface Component
const PurchaseOrderInterface = () => {
  const [mode, setMode] = useState('chat'); // 'chat' or 'form'
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [formData, setFormData] = useState({
    supplier_id: '',
    order_date: '',
    total_amount: '',
    items: '',
    status: 'pending',
    po_id: '',
    quantity: '',
    description: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [chatStep, setChatStep] = useState(0);
  const messagesEndRef = useRef(null);

  // Required fields based on API schema
  const requiredFields = ['supplier_id', 'order_date', 'total_amount', 'items'];
  
  // Chat flow questions
  const chatQuestions = [
    "👋 Welcome! I'll help you create a purchase order. What's your supplier ID? (e.g., SUP001, SUP002)",
    "📅 Great! What's the order date? (YYYY-MM-DD format)",
    "📦 What items would you like to order? (e.g., 'Laptops x10, Mice x20')",
    "💰 What's the total amount for this order? (e.g., $15000 or 15000)",
    "📝 Any additional description for this order? (optional)",
    "✅ Perfect! Let me show you a summary of your purchase order."
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (mode === 'chat' && chatMessages.length === 0) {
      // Initialize chat with welcome message
      setChatMessages([{
        type: 'bot',
        content: chatQuestions[0],
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  }, [mode]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Handle chat message submission
  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    // Add user message
    const userMessage = {
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setChatMessages(prev => [...prev, userMessage]);

    // Process user input based on current step
    processUserInput(currentMessage, chatStep);
    setCurrentMessage('');
  };

  // Process user input in chat mode
  const processUserInput = (input, step) => {
    let botResponse = '';
    let nextStep = step + 1;

    switch (step) {
      case 0: // Supplier ID
        if (input.match(/SUP\\d+/i)) {
          setFormData(prev => ({ ...prev, supplier_id: input.toUpperCase() }));
          botResponse = chatQuestions[1];
        } else {
          botResponse = "Please provide a valid supplier ID (format: SUP001, SUP002, etc.)";
          nextStep = step; // Stay on same step
        }
        break;

      case 1: // Order Date
        if (input.match(/^\\d{4}-\\d{2}-\\d{2}$/)) {
          setFormData(prev => ({ ...prev, order_date: input }));
          botResponse = chatQuestions[2];
        } else {
          botResponse = "Please provide date in YYYY-MM-DD format (e.g., 2025-10-15)";
          nextStep = step;
        }
        break;

      case 2: // Items
        setFormData(prev => ({ ...prev, items: input }));
        // Extract quantity if mentioned
        const qtyMatch = input.match(/x(\\d+)/i);
        if (qtyMatch) {
          setFormData(prev => ({ ...prev, quantity: parseInt(qtyMatch[1]) }));
        }
        botResponse = chatQuestions[3];
        break;

      case 3: // Total Amount
        const amountMatch = input.match(/\\$?([\\d,]+(?:\\.\\d{2})?)/);
        if (amountMatch) {
          const amount = parseFloat(amountMatch[1].replace(',', ''));
          setFormData(prev => ({ ...prev, total_amount: amount }));
          botResponse = chatQuestions[4];
        } else {
          botResponse = "Please provide a valid amount (e.g., $15000 or 15000)";
          nextStep = step;
        }
        break;

      case 4: // Description (optional)
        setFormData(prev => ({ ...prev, description: input }));
        botResponse = chatQuestions[5];
        setTimeout(() => setShowSummary(true), 1000);
        break;

      default:
        botResponse = "Thank you! Your purchase order is ready for review.";
    }

    // Add bot response
    setTimeout(() => {
      setChatMessages(prev => [...prev, {
        type: 'bot',
        content: botResponse,
        timestamp: new Date().toLocaleTimeString()
      }]);
      setChatStep(nextStep);
    }, 500);
  };

  // Handle form input changes
  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Validate form data
  const validateForm = () => {
    const newErrors = {};
    
    requiredFields.forEach(field => {
      if (!formData[field] || formData[field].toString().trim() === '') {
        newErrors[field] = `${field.replace('_', ' ').toUpperCase()} is required`;
      }
    });

    // Specific validations
    if (formData.supplier_id && !formData.supplier_id.match(/SUP\\d+/i)) {
      newErrors.supplier_id = 'Supplier ID must be in format SUP001, SUP002, etc.';
    }

    if (formData.order_date && !formData.order_date.match(/^\\d{4}-\\d{2}-\\d{2}$/)) {
      newErrors.order_date = 'Order date must be in YYYY-MM-DD format';
    }

    if (formData.total_amount && (isNaN(formData.total_amount) || formData.total_amount <= 0)) {
      newErrors.total_amount = 'Total amount must be a positive number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit purchase order
  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Generate PO ID if not exists
      const poId = formData.po_id || `PO${Date.now()}`;
      
      const orderData = {
        ...formData,
        po_id: poId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // API call to submit purchase order
      const response = await fetch('http://localhost:5000/api/purchase_order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();

      if (result.status === 'success') {
        alert(`✅ Purchase Order Created Successfully!\\nPO ID: ${poId}\\nDocument ID: ${result.id}`);
        
        // Reset form
        setFormData({
          supplier_id: '',
          order_date: '',
          total_amount: '',
          items: '',
          status: 'pending',
          po_id: '',
          quantity: '',
          description: ''
        });
        setShowSummary(false);
        setChatMessages([]);
        setChatStep(0);
      } else {
        throw new Error(result.message || 'Failed to create purchase order');
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Switch between modes
  const switchMode = (newMode) => {
    setMode(newMode);
    if (newMode === 'chat' && chatMessages.length === 0) {
      setChatMessages([{
        type: 'bot',
        content: chatQuestions[0],
        timestamp: new Date().toLocaleTimeString()
      }]);
      setChatStep(0);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-4 flex items-center gap-3">
            <Package className="text-blue-600" />
            Purchase Order System
          </h1>
          
          {/* Mode Switcher */}
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => switchMode('chat')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                mode === 'chat' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <MessageCircle size={20} />
              Chat Mode
            </button>
            <button
              onClick={() => switchMode('form')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                mode === 'form' 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <FileText size={20} />
              Form Mode
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {mode === 'chat' ? (
              /* Chat Mode */
              <div className="bg-white rounded-xl shadow-lg h-96 flex flex-col">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-xl font-semibold text-gray-800">Chat Assistant</h2>
                  <p className="text-sm text-gray-600">Let me guide you through creating your purchase order</p>
                </div>
                
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {chatMessages.map((message, index) => (
                    <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {message.timestamp}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
                
                {/* Input */}
                <form onSubmit={handleChatSubmit} className="p-4 border-t border-gray-200">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      placeholder="Type your response..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={showSummary}
                    />
                    <button
                      type="submit"
                      disabled={showSummary}
                      className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send size={20} />
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              /* Form Mode */
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-6">Purchase Order Form</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Supplier ID */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Building className="inline w-4 h-4 mr-1" />
                      Supplier ID *
                    </label>
                    <input
                      type="text"
                      value={formData.supplier_id}
                      onChange={(e) => handleFormChange('supplier_id', e.target.value)}
                      placeholder="SUP001, SUP002, etc."
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.supplier_id ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.supplier_id && <p className="text-red-500 text-xs mt-1">{errors.supplier_id}</p>}
                  </div>

                  {/* Order Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Calendar className="inline w-4 h-4 mr-1" />
                      Order Date *
                    </label>
                    <input
                      type="date"
                      value={formData.order_date}
                      onChange={(e) => handleFormChange('order_date', e.target.value)}
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.order_date ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.order_date && <p className="text-red-500 text-xs mt-1">{errors.order_date}</p>}
                  </div>

                  {/* Items */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Package className="inline w-4 h-4 mr-1" />
                      Items *
                    </label>
                    <textarea
                      value={formData.items}
                      onChange={(e) => handleFormChange('items', e.target.value)}
                      placeholder="e.g., Laptops x10, Wireless Mice x20, USB Cables x50"
                      rows={3}
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.items ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.items && <p className="text-red-500 text-xs mt-1">{errors.items}</p>}
                  </div>

                  {/* Total Amount */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <DollarSign className="inline w-4 h-4 mr-1" />
                      Total Amount *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.total_amount}
                      onChange={(e) => handleFormChange('total_amount', e.target.value)}
                      placeholder="15000.00"
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.total_amount ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.total_amount && <p className="text-red-500 text-xs mt-1">{errors.total_amount}</p>}
                  </div>

                  {/* Status */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select
                      value={formData.status}
                      onChange={(e) => handleFormChange('status', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="pending">Pending</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>

                  {/* Description */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description (Optional)</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleFormChange('description', e.target.value)}
                      placeholder="Additional notes or specifications..."
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="mt-6 flex gap-4">
                  <button
                    onClick={() => setShowSummary(true)}
                    disabled={!requiredFields.every(field => formData[field])}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Review Order
                  </button>
                  <button
                    onClick={() => {
                      setFormData({
                        supplier_id: '',
                        order_date: '',
                        total_amount: '',
                        items: '',
                        status: 'pending',
                        po_id: '',
                        quantity: '',
                        description: ''
                      });
                      setErrors({});
                    }}
                    className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Clear Form
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Summary Panel */}
          <div className="lg:col-span-1">
            {(showSummary || Object.values(formData).some(val => val !== '' && val !== 'pending')) && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Check className="text-green-600" />
                  Order Summary
                </h3>
                
                <div className="space-y-3">
                  {formData.supplier_id && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Supplier:</span>
                      <span className="font-medium">{formData.supplier_id}</span>
                    </div>
                  )}
                  
                  {formData.order_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Date:</span>
                      <span className="font-medium">{formData.order_date}</span>
                    </div>
                  )}
                  
                  {formData.items && (
                    <div>
                      <span className="text-gray-600">Items:</span>
                      <p className="font-medium mt-1 bg-gray-50 p-2 rounded text-sm">{formData.items}</p>
                    </div>
                  )}
                  
                  {formData.total_amount && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total:</span>
                      <span className="font-bold text-lg text-green-600">${formData.total_amount}</span>
                    </div>
                  )}
                  
                  {formData.status && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className={`font-medium capitalize px-2 py-1 rounded-full text-xs ${
                        formData.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        formData.status === 'approved' ? 'bg-green-100 text-green-800' :
                        formData.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {formData.status}
                      </span>
                    </div>
                  )}
                </div>

                {showSummary && requiredFields.every(field => formData[field]) && (
                  <div className="mt-6 space-y-3">
                    <button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                      className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Submitting...
                        </>
                      ) : (
                        <>
                          <Check size={16} />
                          Confirm & Submit Order
                        </>
                      )}
                    </button>
                    
                    <button
                      onClick={() => setShowSummary(false)}
                      className="w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 flex items-center justify-center gap-2"
                    >
                      <X size={16} />
                      Back to Edit
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PurchaseOrderInterface;