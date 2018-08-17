# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import Workflow, ModelView
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['Purchase']


class Purchase(metaclass=PoolMeta):
    __name__ = 'purchase.purchase'

    @classmethod
    def __setup__(cls):
        super(Purchase, cls).__setup__()
        cls._transitions.add(
            ('confirmed', 'quotation'),
            )
        cls._buttons.update({
                'to_quote': {
                    'invisible': Eval('state') != 'confirmed',
                    },
                })

    @classmethod
    @ModelView.button
    @Workflow.transition('quotation')
    def to_quote(cls, purchases):
        pass
