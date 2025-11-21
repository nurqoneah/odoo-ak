{
    'name': 'POS Employee Access Control',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Control employee access to various POS operations',
    'description': """
        POS Employee Access Control
        ===========================
        Control employee access to:
        * POS Closing
        * Order Deletion/Cancellation
        * Order Line Deletion
        * Order Payment
        * Discount Application
        * Price Change
        * Decreasing Quantity
        * Cash In/Out
        * Create Product
        * Fiscal Position/Tax
        * Pricelist
        * Refund
        
        The block is triggered whether a mouse, keyboard, or touch input is used.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_employee_access/static/src/js/pos_employee_access.js',
            'pos_employee_access/static/src/js/payment_override.js',
            'pos_employee_access/static/src/js/refund_override.js',
            'pos_employee_access/static/src/js/order_operations.js',
            'pos_employee_access/static/src/js/session_operations.js',
            'pos_employee_access/static/src/js/discount_operations.js',
            'pos_employee_access/static/src/js/price_operations.js',
            'pos_employee_access/static/src/js/product_operations.js',
            'pos_employee_access/static/src/js/fiscal_pricelist_operations.js',
            'pos_employee_access/static/src/xml/pos_employee_access.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}