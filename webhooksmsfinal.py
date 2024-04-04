from flask import Flask, request
import logging
import smpplib.gsm
import smpplib.client
import smpplib.consts

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/webhook-endpoint', methods=['POST'])
def webhook():
    data = request.json
    alert_message = data.get('message', 'No message provided')
    send_sms(alert_message)
    return 'Webhook received successfully!', 200

def send_sms(message):
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    client = smpplib.client.Client('10.51.37.196', 6200)
    client.connect()
    client.bind_transceiver(system_id='smscloud', password='smscloud')
    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
            source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
            source_addr='TEST',
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            destination_addr='84766642199',
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )
        logging.info('submit_sm {}->{} seqno: {}'.format(pdu.source_addr, pdu.destination_addr, pdu.sequence))
    client.listen()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
