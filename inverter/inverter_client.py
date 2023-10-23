import sys
import socket
import binascii
import re
import libscrc
import json
import datetime
import logging

from inverter.config import Config

class InverterClient:
    def __init__(self, config: Config):
        self.config = config

    def read_realtime_data(self):
        '''Queries the self.configured inverter for its realtime data and returns it as JSON'''
        logging.info("Building request")
        response_json, totalpower = self._realtime_data_request()

        if totalpower < self.config.inverter_installed_power * 1000:
            return response_json
        else:
            # open text file
            text_file = open("picos_potencia.txt", "a")

            # write string to file
            text_file.write(datetime.datetime.now().strftime(
                '%d/%m/%y %I:%M %S %p') * '\n')
            text_file.write(response_json + '\n')

            # close file
            text_file.close()
            raise Exception("Total power is higher than installed power")

    # private

    _PV_POWER_REGISTERS = ['0x00BA', '0x00BB']

    def _realtime_data_request(self):
        pini = 59
        pfin = 112
        chunks = 0
        while chunks < 2:
            logging.debug(f"Chunks: {chunks}")
            if chunks == -1:
                pini = 235
                pfin = 235
                print("Initialise Connection")
            start = binascii.unhexlify('A5')  # start
            length = binascii.unhexlify('1700')  # datalength
            controlcode = binascii.unhexlify('1045')  # controlCode
            serial = binascii.unhexlify('0000')  # serial
            # com.igen.localmode.dy.instruction.send.SendDataField
            datafield = binascii.unhexlify('020000000000000000000000000000')
            pos_ini = str(hex(pini)[2:4].zfill(4))
            pos_fin = str(hex(pfin-pini + 1)[2:4].zfill(4))
            businessfield = binascii.unhexlify(
                '0103' + pos_ini + pos_fin)  # sin CRC16MODBUS
            crc = binascii.unhexlify(str(hex(libscrc.modbus(businessfield))[
                                    4:6]) + str(hex(libscrc.modbus(businessfield))[2:4]))  # CRC16modbus
            checksum = binascii.unhexlify('00')  # checksum F2
            endCode = binascii.unhexlify('15')

            inverter_sn2 = bytearray.fromhex(
                hex(self.config.inverter_sn)[8:10] + 
                hex(self.config.inverter_sn)[6:8] + 
                hex(self.config.inverter_sn)[4:6] + 
                hex(self.config.inverter_sn)[2:4]
            )
            frame = bytearray(start + length + controlcode + serial +
                            inverter_sn2 + datafield + businessfield + crc + checksum + endCode)

            checksum = 0
            frame_bytes = bytearray(frame)
            for i in range(1, len(frame_bytes) - 2, 1):
                checksum += frame_bytes[i] & 255
            frame_bytes[len(frame_bytes) - 2] = int((checksum & 255))

            response_bytes = self._send_request_to_inverter(frame_bytes)

            # Parse the response bytes (start position 56, end position 60)
            totalpower = 0
            i = pfin-pini
            a = 0

            output = "{"  # initialise json output
            while a <= i:
                p1 = 56 + (a * 4)
                p2 = 60 + (a * 4)
                response = InverterClient._twosComplement_hex(
                    str(
                        ''.join(hex(x)[2:].zfill(2) for x in bytearray(response_bytes)) + 
                        '  ' + 
                        re.sub('[^\x20-\x7f]', '', '')
                        )[p1:p2]
                    )
                
                hexpos = str("0x") + str(hex(a + pini)[2:].zfill(4)).upper()
                with open("./DYRealTime.json") as txtfile:
                    parameters = json.loads(txtfile.read())

                for parameter in parameters:
                    for item in parameter["items"]:
                        title = item["titleEN"]
                        ratio = item["ratio"]
                        unit = item["unit"]

                        for register in item["registers"]:
                            if register == hexpos and chunks != -1:
                                if title.find("Temperature") != -1:
                                    response = round(response * ratio-100, 2)
                                else:
                                    response = round(response * ratio, 2)
                                output = output + "\"" + title + "(" + unit + ")" + "\":" + str(response) + ","
                                
                                if hexpos in InverterClient._PV_POWER_REGISTERS:
                                    totalpower += response * ratio
                a += 1
            pini = 150
            pfin = 195
            chunks += 1
        output = output[:-1] + "}"

        return output, totalpower

    def _send_request_to_inverter(self, frame_bytes):
        # Open socket
        for res in socket.getaddrinfo(self.config.inverter_ip, self.config.inverter_port, socket.AF_INET, socket.SOCK_STREAM):
            family, socktype, proto, canonname, sockadress = res
            try:
                clientSocket = socket.socket(family, socktype, proto)
                clientSocket.settimeout(10)
                clientSocket.connect(sockadress)
            except socket.error as msg:
                print("Could not open socket")
                break

        # Send data
        clientSocket.sendall(frame_bytes)

        # Receive data
        ok = False
        while (not ok):
            try:
                data = clientSocket.recv(1024)
                ok = True
                try:
                    data
                except:
                    print("No data - Die")
                    sys.exit(1)  # die, no data
            except socket.timeout as msg:
                print("Connection timeout")
                sys.exit(1)  # die

        return data

    def _twosComplement_hex(hexval):
        bits = 16
        val = int(hexval, bits)
        if val & (1 << (bits-1)):
            val -= 1 << bits
        return val