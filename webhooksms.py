#!/usr/bin/python

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

# if you want to know what's happening
logging.basicConfig(level='INFO')

# Two parts, GSM default / UCS2, SMS with UDH
parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(u'Hello World €$£')

client = smpplib.client.Client('smscsim.smpp.org', 2775)

# Print when obtain message_id
client.set_message_sent_handler(
    lambda pdu: logging.info('submit_sm_resp seqno: {} msgid: {}'.format(pdu.sequence, pdu.message_id)))

# Handle delivery receipts (and any MO SMS)
def handle_deliver_sm(pdu):
        logging.info('delivered msgid:{}'.format(pdu.receipted_message_id))
        return 0 # cmd status for deliver_sm_resp

client.set_message_received_handler(lambda pdu: handle_deliver_sm(pdu))

client.connect()
client.bind_transceiver(system_id='SYSTEMID', password='PASSWORD')

for part in parts:
    pdu = client.send_message(
        source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
        source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
        # Make sure it is a byte string, not unicode:
        source_addr='MelroseLabs',

        dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
        dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
        # Make sure these two params are byte strings, not unicode:
        destination_addr='447712345678',
        short_message=part,

        data_coding=encoding_flag,
        esm_class=msg_type_flag,
        registered_delivery=True,
    )
    logging.info('submit_sm {}->{} seqno: {}'.format(pdu.source_addr,pdu.destination_addr,pdu.sequence))

# Enters a loop, waiting for incoming PDUs
client.listen()