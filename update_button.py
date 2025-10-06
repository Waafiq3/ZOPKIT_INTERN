#!/usr/bin/env python3

# Script to update the Purchase Order button
import os

def update_purchase_order_button():
    # Read the file
    with open('templates/simple_chat.html', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Replace line 753 (index 752)
    old_line = lines[752]
    new_line = '                <button id="purchaseOrderBtn" class="quick-action-btn" onclick="requestPurchaseOrderAccess()" style="display: none;">📦 Create Purchase Order</button>\n'
    lines[752] = new_line

    # Write back
    with open('templates/simple_chat.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print('✅ Button updated successfully!')
    print('Old line:', repr(old_line))
    print('New line:', repr(new_line))

if __name__ == "__main__":
    update_purchase_order_button()