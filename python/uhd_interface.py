import numpy as np
from numpy.random import randint
from time import sleep
import os, sys, traceback, uhd

USER = os.environ['USER']
LIB_PATH = f'/home/{USER}/uhd/install/local/lib/python3.10/dist-packages'

class SDR:
    """ Sets up the USRP to be used. Also provided methods to TX and RX. """
    _tx_streamer = None
    _rx_streamer = None

    def __init__(self, sample_rate:float, center_freq:float, tx_gain:int, rx_gain:int, usrp_device_name:str):
        self._sample_rate:float = sample_rate
        self._center_freq:float = center_freq
        self._tx_gain:int = tx_gain
        self._rx_gain:int = rx_gain
        self._usrp_device_name:str = usrp_device_name
        # RX
        self._rx_stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
        self._rx_stream_cmd.stream_now = True
        self._rx_meta_data = uhd.types.RXMetadata()
        # TX
        self._tx_meta_data = uhd.types.TXMetadata()
        self._tx_meta_data.has_time_spec = False
        self._tx_meta_data.start_of_burst = True
        self._tx_meta_data.end_of_burst = False
        self._tx2_meta_data = uhd.types.TXMetadata()
        self._tx2_meta_data.has_time_spec = False
        self._tx2_meta_data.start_of_burst = False
        self._tx2_meta_data.end_of_burst = True
        # USRP
        if usrp_device_name is not None:
            self._usrp_device = uhd.usrp.MultiUSRP(
                "send_frame_size=10000, recv_frame_size=10000, num_recv_frames=1000, serial=" + usrp_device_name
            )
        else:
            self._usrp_device = uhd.usrp.MultiUSRP(
                "send_frame_size=10000, recv_frame_size=10000, num_recv_frames=1000"
            )
        # Setup RX and TX
        self.set_rx()
        self.set_tx()

    def set_tx(self) -> None:
        """ Sets up the USRP TX """
        try:
            # Set TX center frequency
            self._usrp_device.set_tx_rate(self._sample_rate, 0)
            self._usrp_device.set_tx_freq(
                uhd.libpyuhd.types.tune_request(self._center_freq), 0
            )
            # Set TX gain
            self._usrp_device.set_tx_gain(self._tx_gain, 0)
            # wait until the lo's are locked
            while not self._usrp_device.get_tx_sensor("lo_locked", 0).to_bool():
                print('waiting for usrp lo lock')
                sleep(0.01)
            # setup stream and receive buffer
            st_args = uhd.usrp.StreamArgs("fc32", "sc16")
            st_args.channels = [0]
            self._tx_streamer = self._usrp_device.get_tx_stream(st_args)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def set_rx(self) -> None:
        """ Sets up the USRP RX """
        try:
            # Set RX center frequency
            self._usrp_device.set_rx_rate(self._sample_rate, 0)
            self._usrp_device.set_rx_freq(
                uhd.libpyuhd.types.tune_request(self._center_freq), 0
            )
            # Set RX gain
            self._usrp_device.set_rx_gain(self._rx_gain, 0)
            self._usrp_device.set_rx_antenna("TX/RX", 0)
            # Setup the stream buffer and recieve buffer
            st_args = uhd.usrp.StreamArgs("fc32", "sc16")
            st_args.channels = [0]
            # Setup _rx_streamer
            self._rx_streamer = self._usrp_device.get_rx_stream(st_args)
            self._rx_streamer.issue_stream_cmd(self._rx_stream_cmd)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def tx_data(self, data:np.ndarray) -> None:
        """ Sends data out over the USRP 
        
        Arguments:
            data (np.ndarray): The packet to be transmitted.
        """
        self._tx_streamer.send(data, self._tx_meta_data)
        self._tx_streamer.send(np.zeros(10, dtype=np.complex64), self._tx2_meta_data)

    def rx_data(self) -> np.ndarray:
        """ Recieve data from the USRP """
        self._recv_buffer = np.zeros(
            (1, self._rx_streamer.get_max_num_samps() * 10), dtype=np.complex64
        )
        self._rx_streamer.recv(self._recv_buffer, self._rx_meta_data, 0.2)
        if self._rx_meta_data.error_code != uhd.types.RXMetadataErrorCode.none:
            print(f'error: {self._rx_meta_data.strerror()}')
        return self._recv_buffer

if __name__ == "__main__":
    sdr = SDR(15000000.0, 2400000000.0, 70, 74, None)
    sleep(1)
    print("attempting to RX")
    data = sdr.rx_data()
    print(data)