#
# MIT License
#
# Copyright (c) 2018 Erriez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

##
# 8 Channel RS485 RTU relay board type R421A08.
#
# This is a Python example to control the relay board with a USB - RS485 dongle.
#
# Source: https://github.com/Erriez/R421A08-rs485-8ch-relay-board
#

import time

import relay_modbus

import struct


# Fixed board type string
BOARD_TYPE = 'AlicatMFC'

# Fixed RS485 baudrate required for the R421A08 relay board
BAUDRATE = 9600

# Fixed number of relays on the R421A08 board
NUM_RELAYS = 16

# Fixed number of addresses, configurable with 6 DIP switches on the R421A08 relay board
NUM_ADDRESSES = 64

# Commands
CMD_ON = 0x01
CMD_OFF = 0x02
CMD_TOGGLE = 0x03
CMD_LATCH = 0x04
CMD_MOMENTARY = 0x05
CMD_DELAY = 0x06

# R421A08 supports MODBUS control command and read status only
FUNCTION_CONTROL_COMMAND = 0x06
FUNCTION_READ_STATUS = 0x03
FUNCTION_WRITE_MULTIPLE_REGISTERS = 16

# Fixed receive frame length
RX_LEN_CONTROL_COMMAND = 8
RX_LEN_READ_STATUS = 25
RX_LEN_READ_MASSFLOW = 9


class ModbusException(Exception):
    pass


class AlicatMFC(object):
    """ Alicat Mass Flow Controller class """
    def __init__(self,
                 modbus_obj,
                 address=3,
                 board_name='Alicat MFC {}'.format(BOARD_TYPE),
                 num_address=NUM_ADDRESSES,
                 verbose=False):
        """
            Alicat MFC relay board constructor
        :param modbus_obj:
        :param address:
        :param board_name:
        :param num_address:
        :param num_relays:
        :param verbose:
            False: Normal prints (Default)
            True: Print verbose messages
        """
        # Print additional prints
        self._verbose = verbose

        assert type(modbus_obj) == relay_modbus.Modbus
        self._modbus = modbus_obj

        # Store required board address (Configurable with DIP 6 switches)
        assert 0 <= int(address) < NUM_ADDRESSES
        self._address = int(address)

        # Store optional board name
        self._board_name = str(board_name)

        # Store default R421A08 board settings which may be overruled (Not recommended)
        self._num_addresses = int(num_address)

    # ----------------------------------------------------------------------------------------------
    # Relay board properties
    # ----------------------------------------------------------------------------------------------
    @property
    def board_type(self):
        return BOARD_TYPE

    @property
    def board_name(self):
        return self._board_name

    @board_name.setter
    def board_name(self, board_name):
        self._board_name = board_name

    @property
    def serial_port(self):
        return self._modbus.serial_port

    @property
    def baudrate(self):
        return self._modbus.baudrate

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        address = int(address)

        if address >= 0 and address < self._num_addresses:
            self._address = address

    @property
    def num_addresses(self):
        return self._num_addresses

    @property
    def num_relays(self):
        return self._num_relays

    # ----------------------------------------------------------------------------------------------
    # MFC private functions
    # ----------------------------------------------------------------------------------------------
    def _set_MFC_setpoint(self, setpt):
        """
            Send relay control
        :param relay: Relay number
        :param cmd: Command
        :param delay: Optional delay
        :return: List response (int)
        """

        assert type(setpt) == float

        if not self._modbus.is_open():
            raise ModbusException('Error: Serial port not open')

        setpt_bin = struct.pack('>f', setpt)

        # Create binary read status
        tx_data = [
            self.address,  # Slave address of the MFC
            FUNCTION_WRITE_MULTIPLE_REGISTERS,  # this is function 16
            0x03, 0xF1,  # write starting register 1010
            0X00, 0x02, 0X04,  # WRITE 2 REGISTERS, 4 bytes
            setpt_bin[0], setpt_bin[1],  # higher order setpoint register
            setpt_bin[2], setpt_bin[3],  # lower order setpoint register
        ]

        # Send command
        self._modbus.send(tx_data)

        # Wait for response with timeout
        rx_frame = self._modbus.receive(RX_LEN_CONTROL_COMMAND)

        # Check response from relay
        if not rx_frame or len(rx_frame) != RX_LEN_CONTROL_COMMAND:
            return False

        return True

    def _reset_MFC_total(self):
        """
            Send relay control
        :param relay: Relay number
        :param cmd: Command
        :param delay: Optional delay
        :return: List response (int)
        """

        if not self._modbus.is_open():
            raise ModbusException('Error: Serial port not open')

        # Create binary read status
        tx_data = [
            self.address,  # Slave address of the MFC
            FUNCTION_WRITE_MULTIPLE_REGISTERS,  # this is function 16
            0x03, 0xe7,  # write starting register 1000 (command registers)
            0X00, 0x02, 0x04,  # WRITE 2 REGISTERS, 4 bytes
            0x00, 0x05,  # higher order setpoint register
            0x00, 0x00,  # lower order setpoint register
        ]

        # Send command
        self._modbus.send(tx_data)

        # Wait for response with timeout
        rx_frame = self._modbus.receive(RX_LEN_CONTROL_COMMAND)
        
        # Check response from relay
        if not rx_frame or len(rx_frame) != RX_LEN_CONTROL_COMMAND:
            return False

        return True

    def _read_MFC_status(self):
        """
            Read statistics registers from MFC
            Registers are:
                Register Number Statistic
                1203-04 Pressure
                1205-06 Flow Temperature
                1207-08 Volumetric Flow
                1209-10 Mass Flow
                1211-12 Mass Flow Setpoint
        """


        if not self._modbus.is_open():
            raise ModbusException('Error: Serial port not open')

        reg_num_h = 0x04
        reg_num_l = 0xb2
        # Create binary read status
        tx_data = [
            self._address,          # Slave address of the relay board 0..63
            FUNCTION_READ_STATUS,   # Read status is always 0x03
            reg_num_h, reg_num_l,            # Relay 0x0001..0x0008
            0x00, 0x0a              # Number of registers is 10 for the five double-wide registers
        ]

        # Send command and wait for response with timeout
        self._modbus.send(tx_data)

        # Wait for response with timeout
        rx_data = self._modbus.receive(RX_LEN_READ_STATUS)

        if rx_data and len(rx_data) > 2:
            # Check CRC
            data_no_crc = rx_data[:-2]
            crc = rx_data[-2:]
            if self._modbus.crc(data_no_crc) != crc:
                raise ModbusException('RX error: Incorrect CRC received')
            elif rx_data[0] != tx_data[0]:
                raise ModbusException('RX error: Incorrect address received')
            elif rx_data[1] != tx_data[1]:
                raise ModbusException('RX error: Incorrect function received')
            elif rx_data[2] != 20:
                raise ModbusException('RX error: Incorrect data length received')
            else:
                return rx_data

        return -1

    def _read_MFC_massflow(self):
        """
            Read statistics registers from MFC
            Registers are:
                Register Number Statistic
                1203-04 Pressure
                1205-06 Flow Temperature
                1207-08 Volumetric Flow
                1209-10 Mass Flow
                1211-12 Mass Flow Setpoint
        """


        if not self._modbus.is_open():
            raise ModbusException('Error: Serial port not open')

        reg_num_h = 0x04
        reg_num_l = 0xb8
        # Create binary read status
        tx_data = [
            self._address,          # Slave address of the relay board 0..63
            FUNCTION_READ_STATUS,   # Read status is always 0x03
            reg_num_h, reg_num_l,            # Relay 0x0001..0x0008
            0x00, 0x02              # Number of registers is 10 for the five double-wide registers
        ]

        # Send command and wait for response with timeout
        self._modbus.send(tx_data)

        # Wait for response with timeout
        rx_data = self._modbus.receive(RX_LEN_READ_MASSFLOW)

        if rx_data and len(rx_data) > 2:
            # Check CRC
            data_no_crc = rx_data[:-2]
            crc = rx_data[-2:]
            if self._modbus.crc(data_no_crc) != crc:
                raise ModbusException('RX error: Incorrect CRC received')
            elif rx_data[0] != tx_data[0]:
                raise ModbusException('RX error: Incorrect address received')
            elif rx_data[1] != tx_data[1]:
                raise ModbusException('RX error: Incorrect function received')
            elif rx_data[2] != 4:
                raise ModbusException('RX error: Incorrect data length received')
            else:
                return rx_data

        return -1

    def _read_MFC_masstotal(self):
        """
            Read statistics registers from MFC
            Registers are:
                Register Number Statistic
                1203-04 Pressure
                1205-06 Flow Temperature
                1207-08 Volumetric Flow
                1209-10 Mass Flow
                1211-12 Mass Flow Setpoint
                1213-14 Mass Total
        """


        if not self._modbus.is_open():
            raise ModbusException('Error: Serial port not open')

        reg_num_h = 0x04
        reg_num_l = 0xbc
        # Create binary read status
        tx_data = [
            self._address,          # Slave address of the relay board 0..63
            FUNCTION_READ_STATUS,   # Read status is always 0x03
            reg_num_h, reg_num_l,            # Relay 0x0001..0x0008
            0x00, 0x02              # Number of registers is 10 for the five double-wide registers
        ]

        # Send command and wait for response with timeout
        self._modbus.send(tx_data)

        # Wait for response with timeout
        rx_data = self._modbus.receive(RX_LEN_READ_MASSFLOW)

        if rx_data and len(rx_data) > 2:
            # Check CRC
            data_no_crc = rx_data[:-2]
            crc = rx_data[-2:]
            if self._modbus.crc(data_no_crc) != crc:
                raise ModbusException('RX error: Incorrect CRC received')
            elif rx_data[0] != tx_data[0]:
                raise ModbusException('RX error: Incorrect address received')
            elif rx_data[1] != tx_data[1]:
                raise ModbusException('RX error: Incorrect function received')
            elif rx_data[2] != 4:
                raise ModbusException('RX error: Incorrect data length received')
            else:
                return rx_data

        return -1

    # ----------------------------------------------------------------------------------------------
    # Public functions to control MFC
    # ----------------------------------------------------------------------------------------------
    def setpoint(self,setpt):
        return self._set_MFC_setpoint(setpt)

    def readback(self):
        datalist = self._read_MFC_status()
        data = bytearray(datalist)
        pressure = struct.unpack('>f',data[3:7])[0]
        flowtemp = struct.unpack('>f',data[7:11])[0]
        volflow = struct.unpack('>f',data[11:15])[0]
        massflow = struct.unpack('>f',data[15:19])[0]
        setpoint = struct.unpack('>f',data[19:23])[0]
        ret = {'press':pressure,'flowTemp':flowtemp,'volFlow':volflow,'massFlow':massflow,'setpoint':setpoint}
        return ret

    def readMassFlow(self):
        datalist = self._read_MFC_massflow()
        data = bytearray(datalist)
        massflow = struct.unpack('>f',data[3:7])[0]
        return massflow

    def readMassTotal(self):
        datalist = self._read_MFC_masstotal()
        data = bytearray(datalist)
        massflow = struct.unpack('>f',data[3:7])[0]
        return massflow
    
    def resetTotal(self):
        return self._reset_MFC_total()
    
