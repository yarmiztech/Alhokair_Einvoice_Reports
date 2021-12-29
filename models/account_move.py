from odoo import models,fields,api
# from deep_translator import GoogleTranslator
import convert_numbers

from uuid import uuid4
import qrcode
import base64
import logging

from lxml import etree



class AccountMove(models.Model):
    _inherit = 'account.move'

    datetime_field = fields.Datetime(string="Create Date", default=lambda self: fields.Datetime.now())
    decoded_data = fields.Char('Decoded Data')



    def total_vat(self):
        total_vat = self.amount_untaxed * 0.15
        return total_vat








    # def print_einvoice(self):
    #     return self.env.ref('alhokair_einvoice_reports.alhokair_einvoice_report').report_action(self)

    def print_einvoice(self):
        if self.partner_id.type_of_customer == 'b_b':
            # print(self.partner_id.type_of_customer)
            return self.env.ref('alhokair_einvoice_reports.alhokair_einvoice_report').report_action(self)
        # function for b2b invoice
        if self.partner_id.type_of_customer == 'b_c':
            # print(self.partner_id.type_of_customer)
            return self.env.ref('account_invoice_ubl.account_invoices_b2c').report_action(self)
    # function for b2c

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.partner_id.type_of_customer == 'b_b':
            # print(self.partner_id.type_of_customer)
            return self.env.ref('alhokair_einvoice_reports.alhokair_einvoice_report').report_action(self)
        # function for b2b invoice
        if self.partner_id.type_of_customer == 'b_c':
            # print(self.partner_id.type_of_customer)
            return self.env.ref('account_invoice_ubl.account_invoices_b2c').report_action(self)
        return res

    def amount_amount(self):
        # amount = self.price_subtotal * (tax.amount / 100)
        total_amount = 0
        if self.tax_ids:
            for i in self:
                amount = self.price_subtotal * 0.15
                total_amount = self.price_subtotal + amount
                return  total_amount
        else:
            return total_amount

    def ar_total_tax(self):
        value = self.amount_tax
        before, after = str(value).split('.')
        before_int = int(before)
        after_int = int(after)
        before_ar = convert_numbers.english_to_arabic(before_int)
        after_ar = convert_numbers.english_to_arabic(after_int)
        ar_total_tax_amount = before_ar + '.' + after_ar
        return before_ar + '.' + after_ar

    def amount_total_arabic(self):
        value = self.amount_total
        before, after = str(value).split('.')
        before_int = int(before)
        after_int = int(after)
        before_ar = convert_numbers.english_to_arabic(before_int)
        after_ar = convert_numbers.english_to_arabic(after_int)
        ar_total_tax_amount = before_ar + '.' + after_ar
        return before_ar + '.' + after_ar

    def amount_untaxed_convert(self):
        value = self.amount_untaxed
        before, after = str(value).split('.')
        before_int = int(before)
        after_int = int(after)
        before_ar = convert_numbers.english_to_arabic(before_int)
        after_ar = convert_numbers.english_to_arabic(after_int)
        # ar_total_tax_amount = before_ar + '.' + after_ar
        return before_ar + '.' + after_ar

    def ar_advances(self):
        value = 0.00
        before, after = str(value).split('.')
        before_int = int(before)
        after_int = int(after)
        before_ar = convert_numbers.english_to_arabic(before_int)
        after_ar = convert_numbers.english_to_arabic(after_int)
        ar_total_tax_amount = before_ar + '.' + after_ar
        return before_ar + '.' + after_ar

        # def ar_invoice_name(self,name):
        #     translated = GoogleTranslator(source='auto', target='ar').translate(name)
        #     print(translated,'name')
        #     return translated

    def ar_invoice_name(self, name):

        interger_part = name[3:]
        interger_part_arabic = convert_numbers.english_to_arabic(interger_part)
        # inv_name_arabic = GoogleTranslator(source='auto', target='ar').translate(name[:3])
        # inv_name_arabic = ""
        # return  inv_name_arabic+interger_part_arabic
        return interger_part_arabic

    def ar_invoice_date(self):
        m = str(self.invoice_date)
        if m.split('-'):
            interger_part_arabic = ''
            for each in m.split('-'):
                if interger_part_arabic:
                    interger_part_arabic = interger_part_arabic + '-'
                interger_part_arabic += convert_numbers.english_to_arabic(int(each))

        return interger_part_arabic


    def _ubl_add_attachments(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        self.billing_refence(parent_node, ns, version="2.1")
        # if self.decoded_data:
        self.testing()
        self.qr_code(parent_node, ns, version="2.1")
        self.qr_1code(parent_node, ns, version="2.1")
        self.pih_code(parent_node, ns, version="2.1")

        # self.signature_refence(parent_node, ns, version="2.1")
        # if self.company_id.embed_pdf_in_ubl_xml_invoice and not self.env.context.get(
        #     "no_embedded_pdf"
        # ):
        # self.signature_refence(parent_node, ns, version="2.1")
        filename = "Invoice-" + self.name + ".pdf"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach_node = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
        binary_node = etree.SubElement(
            attach_node,
            ns["cbc"] + "EmbeddedDocumentBinaryObject",
            mimeCode="application/pdf",
            filename=filename,
        )
        ctx = dict()
        ctx["no_embedded_ubl_xml"] = True
        ctx["force_report_rendering"] = True
        # pdf_inv = (
        #     self.with_context(ctx)
        #     .env.ref("account.account_invoices")
        #     ._render_qweb_pdf(self.ids)[0]
        # )
        ########changed########################
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_1')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2b')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2b_credit')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #     'account_invoice_ubl.account_invoices_b2b_debit')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2c')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
                    'account_invoice_ubl.account_invoices_b2c_credit')._render_qweb_pdf(self.ids)[0]
        # +++++++++++++++++++++++++++++++OUR CUSTOMES ADD HERE+++++++++++++++++++++++++++++++++++++
        pdf_inv = self.with_context(ctx).env.ref(
            'alhokair_einvoice_reports.alhokair_einvoice_report')._render_qweb_pdf(self.ids)[0]
       # -----------------------------aboveeeeeeee---------------------------------

        binary_node.text = base64.b64encode(pdf_inv)

    @api.model
    def _get_invoice_report_names(self):
        return [
            "account.report_invoice",
            "account.report_invoice_with_payments",
            "account_invoice_ubl.report_invoice_1",
            "account_invoice_ubl.report_invoice_b2b",
            "account_invoice_ubl.report_invoice_b2b_credit",
            # "account_invoice_ubl.report_invoice_b2b_debit",
            "account_invoice_ubl.report_invoice_b2c",
            "account_invoice_ubl.report_invoice_b2c_credit",
            # "account_invoice_ubl.report_invoice_b2c_debit",
            "alhokair_einvoice_reports.alhokair_einvoice_report_view",

        ]

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"


    @classmethod
    def _get_invoice_reports_ubl(cls):
        return [
            "account.report_invoice",
            'account_invoice_ubl.report_invoice_1',
            'account_invoice_ubl.report_invoice_b2b',
            'account_invoice_ubl.report_invoice_b2b_credit',
            'account_invoice_ubl.report_invoice_b2b_debit',
            'account_invoice_ubl.report_invoice_b2c',
            'account_invoice_ubl.report_invoice_b2c_credit',
            'account_invoice_ubl.report_invoice_b2c_debit',
            "account.report_invoice_with_payments",
            "account.account_invoice_report_duplicate_main",
            "alhokair_einvoice_reports.alhokair_einvoice_report_view",

        ]



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def product_tax_value(self):
        amount = 0
        if self.tax_ids:
            tax_amount = self.env['account.tax'].search([('name','=',self.tax_ids.name)])
            for tax in tax_amount:
                amount = self.price_subtotal*(tax.amount/100)

        return amount

    def amount_amount(self):
        # amount = self.price_subtotal * (tax.amount / 100)
        total_amount = 0
        if self.tax_ids:
            for i in self:
                amount = self.price_subtotal * 0.15
                total_amount = self.price_subtotal + amount
                return  total_amount
        else:
            return total_amount

