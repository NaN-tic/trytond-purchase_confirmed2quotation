# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.purchase_confirmed2quotation.tests.test_purchase_confirmed2quotation import suite
except ImportError:
    from .test_purchase_confirmed2quotation import suite

__all__ = ['suite']
