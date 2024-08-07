import unittest
from decimal import Decimal

from proteus import Model
from trytond.ir import queue_
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install purchase
        activate_modules('purchase_confirmed2quotation')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']
        Account = Model.get('account.account')
        cash, = Account.find([
            ('name', '=', 'Main Cash'),
            ('company', '=', company.id),
        ])

        # Create parties
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()
        customer = Party(name='Customer')
        customer.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        product = Product()
        template = ProductTemplate()
        template.name = 'product'
        template.account_category = account_category
        template.default_uom = unit
        template.type = 'goods'
        template.purchasable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.save()
        product.template = template
        product.save()
        service = Product()
        template = ProductTemplate()
        template.name = 'service'
        template.account_category = account_category
        template.default_uom = unit
        template.type = 'service'
        template.purchasable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.save()
        service.template = template
        service.save()

        # Create payment term
        PaymentTerm = Model.get('account.invoice.payment_term')
        PaymentTermLine = Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name='Direct')
        payment_term_line = PaymentTermLine(type='remainder')
        payment_term.lines.append(payment_term_line)
        payment_term.save()

        # Purchase 5 products
        Purchase = Model.get('purchase.purchase')
        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = 'order'
        purchase_line = purchase.lines.new()
        purchase_line.product = product
        purchase_line.quantity = 2.0
        purchase_line.unit_price = product.cost_price
        purchase.click('quote')

        # Set has_worker = True to ensure purchase is not processed automatically on confirm
        queue_.has_worker = True

        # Confirm and try to go back to quote
        purchase.click('confirm')
        self.assertEqual(purchase.state, 'confirmed')
        purchase.click('to_quote')
        self.assertEqual(purchase.state, 'quotation')
