from odoo import http
from odoo.http import request


class PaymentDecidir(http.Controller):

    @http.route('/sps/endop/<string:op_id>', type='http', methods=['POST', 'GET'], auth="public", website=True)
    def decidir_endop(self, op_id='', **post):

        tx = request.env['payment.transaction'].sudo().search(
            [('acquirer_reference', '=', op_id), ('state', '!=', 'done')], limit=1)
        resultado = post.get('resultado', '')

        if tx:
            state_message = ''
            for k, v in post.iteritems():
                state_message += '%s: %s \n' % (k, v)
            if resultado == 'APROBADA':
                tx.sudo().write({
                    'state': 'done',
                    'state_message': state_message,
                    'acquirer_reference': post.get('noperacion', ''),
                    # 'partner_email':post.get('emailcomprador',''),
                    # 'partner_name':post.get('titular',''),
                    # 'partner_reference':"%s %s" % (post.get('tipodocdescri',''),post.get('nrodoc','')),
                })

                return resultado

            elif resultado == 'RECHAZADA':
                tx.sudo().message_post("Error en la operacion %s" %
                                       state_message, 'Rechazo de tarjeta %s ' % post.get('motivo', ''))

                tx.sudo().write({'state': 'cancel', 'state_message': state_message})
            else:
                tx.sudo().write(
                    {'state': 'cancel', 'state_message': state_message})
                resultado = 'no computado'
        else:
            return 'No encontrada'
        return str(resultado)
