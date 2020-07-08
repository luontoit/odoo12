from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import base64
import re
import random
import string

class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_nacha_file(self):

        # Produce NACHA file only if all files are vendor bills, not customer invoices
        for record in self:
            if record.type not in ('in_invoice', 'in_refund'):
                raise ValidationError("Invalid selection: Customer invoice selected. NACHA files can only be created for vendor bills")


        with open('file.txt', 'w') as f:
            # File Header record
            header_record_type = '1'
            priority_code = '01'
            immediate_destination = ' ' + self.env.company.bank_ids.search([('partner_id.name', '=', self.env.company.partner_id.name)]).aba_routing[:9]  # PNC bank transit/routing number preceded by a blank space
            vat = re.sub("[^0-9]", "", self.env.company.vat)
            immediate_origin = vat[:10] if len(vat) > 9 else vat.rjust(10)  # Originator's tax ID preceded by a blank space
            creation_date = datetime.now().strftime('%y%m%d')               # Date when the originator created the file  ** It was the other way around in teh sample file
            creation_time = datetime.now().strftime('%H%M')                 # Time when the originator created the file
            file_id = random.choice(string.ascii_uppercase)                 # A random uppercase letter to distinguish between files created on the same date.
            record_size = '094'                                             # Number of characters contained in each record
            blocking_factor = '10'                                          # Blocking factor defines the number of phisical records within a file
            format_code = '1'
            immediate_destination_name = 'PNC BANK'.rjust(23)
            immediate_origin_name = 'LUONTO FURNITURE'.rjust(23)            # Name of the originating company
            reference_code = ' ' * 8                                        # Blanks fill this field

            f.write(
                    header_record_type +
                    priority_code +
                    immediate_destination +
                    immediate_origin +
                    creation_date +
                    creation_time +
                    file_id +
                    record_size +
                    blocking_factor +
                    format_code +
                    immediate_destination_name +
                    immediate_origin_name +
                    reference_code +
                    '\n'
                    )

            # Company/Batch Header Record
            company_record_type = '5'
            service_class_code = '200'
            company_name = 'LUONTO FURNITURE'.rjust(16)
            company_discretionary_data = ' ' * 20
            vat = re.sub("[^0-9]", "", self.env.company.vat)
            company_identification = '1' + vat[:9]                      # TAX ID – res.company vat field. Should be 9 digits and no hiphen
            standard_entry_class_code = 'CCD'
            company_entry_description = 'VENDOR PMT'.rjust(10)
            company_descriptive_date = datetime.now().strftime('%y%m%d')
            effective_entry_date = datetime.now().strftime('%y%m%d')
            settlement_date = ' ' * 3
            originating_status_code = '1'
            originating_dfi_number = self.env.company.bank_ids.search([('partner_id.name', '=', self.env.company.partner_id.name)]).aba_routing[:8]    # 8 first digits of aba_routing on res.partner.bank of Luonto ( our company )
            batch_number = '0000001'

            f.write(
                    company_record_type +
                    service_class_code +
                    company_name +
                    company_discretionary_data +
                    company_identification +
                    standard_entry_class_code +
                    company_entry_description +
                    company_descriptive_date +
                    effective_entry_date +
                    settlement_date +
                    originating_status_code +
                    originating_dfi_number +
                    batch_number +
                    '\n'
                    )


            # Entry detail records - One record per individual vendor payment
            hash = 0
            total_amount = 0
            for count, record in enumerate(self, start=1):
                detail_record_type = '6'
                transaction_code = '22'
                receiving_dfi_id = record.partner_id.bank_ids.search([('partner_id.name', '=', record.partner_id.name)]).aba_routing[:8]           # First 8 digits of the receiver’s bank transit routing number
                hash += int(receiving_dfi_id)
                check_digit = record.partner_id.bank_ids.search([('partner_id.name', '=', record.partner_id.name)]).aba_routing[-1]   # Last digit of aba_routing of res.partner.bank of partner
                dfi_account_number = record.partner_id.bank_ids.search([('partner_id.name', '=', record.partner_id.name)]).acc_number[:17].ljust(17)    # pick only leftmost 17 characters.
                amount = "".join(filter(str.isdigit, '%.2f' % record.amount_residual)).rjust(10, '0')
                total_amount += int(amount)
                individual_number = str(record.partner_id.id).rjust(15)
                individual_name = record.partner_id.name.rjust(22)
                discretionary_data = ' '*2
                addenda = '0'
                trace_number = receiving_dfi_id +  str(count).rjust(7, '0')     # id + other 7 sequencially generated numbers

                f.write(
                        detail_record_type +
                        transaction_code +
                        receiving_dfi_id +
                        check_digit +
                        dfi_account_number +
                        amount +
                        individual_number +
                        individual_name +
                        discretionary_data +
                        addenda +
                        trace_number +
                        '\n'
                        )
            # Company/Batch Control Record
            batch_control_record_type = '8'
            service_class_code = '200'
            entry_count = str(count).rjust(6, '0')
            hash = str(hash)[-10:].rjust(10, '0')
            total_credit = '0' * 12
            total_debit = str(total_amount).rjust(12, '0')
            vat = re.sub("[^0-9]", "", self.env.company.vat)
            immediate_origin = vat[:10] if len(vat) > 9 else vat.rjust(10, '0')  # Originator's tax ID preceded by a numeric
            message_auth_code = ' ' * 19
            reserved = '6'
            originating_dfi_id = self.env.company.bank_ids.search([('partner_id.name', '=', self.env.company.partner_id.name)]).aba_routing[:8]
            batch_number = '0000001'
            print(type(batch_number))

            f.write(
                    batch_control_record_type +
                    service_class_code +
                    entry_count +
                    total_credit +
                    total_debit +
                    immediate_origin +
                    message_auth_code +
                    reserved +
                    originating_dfi_id +
                    batch_number +
                    '\n'
                    )

            # File Control record
            file_control_record_type = '9'
            batch_count = '000001'  # Number of ‘8’ batch records
            block_count = '000003'  # Number of physical blocks in the file, including file header and file control records.
            reserved = ' ' * 39
            f.write(
                    file_control_record_type +
                    batch_count +
                    block_count +
                    entry_count +
                    hash +
                    total_credit +
                    total_debit +
                    reserved +
                    '\n'
                    )
            for i in range( 10 - (count + 4) % 10):
                f.write('9' * 94 + '\n')

        with open('file.txt', 'rb') as f:
            file = f.read()
            f.close()


        new_file_vals = {
            'name': 'NACHA' + datetime.now().strftime('%H:%M:%S_%d/%m/%Y') + '.txt',
            'type': 'binary',
            'res_model': 'account.move',
            'datas': base64.b64encode(file),
            'mimetype': 'text/plain',
        }

        # Link attachment to all vendor bill records after the file is created
        for record in self:
            record.write({
                'attachment_ids': [(0, 0, new_file_vals)]
            })
