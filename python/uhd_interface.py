import numpy as np
from numpy.random import randint
from time import sleep
import os, sys, traceback, uhd

USER = os.environ['USER']
LIB_PATH = f'/home/{USER}/uhd/install/local/lib/python3.10/dist-packages'

class SDR:
    """ Sets up the USRP to be used. Also provided methods to TX and RX. """
    tx_streamer = None
    rx_streamer = None

    def __init__(self, sample_rate:float, center_freq:float, tx_gain:int, rx_gain:int, usrp_device_name:str):
        self.sample_rate:float = sample_rate
        self.center_freq:float = center_freq
        self.tx_gain:int = tx_gain
        self.rx_gain:int = rx_gain
        self.usrp_device_name:str = usrp_device_name
        # RX
        self.rx_stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
        self.rx_stream_cmd.stream_now = True
        self.rx_meta_data = uhd.types.RXMetadata()
        # TX
        self.tx_meta_data = uhd.types.TXMetadata()
        self.tx_meta_data.has_time_spec = False
        self.tx_meta_data.start_of_burst = True
        self.tx_meta_data.end_of_burst = False
        self.tx2_meta_data = uhd.types.TXMetadata()
        self.tx2_meta_data.has_time_spec = False
        self.tx2_meta_data.start_of_burst = False
        self.tx2_meta_data.end_of_burst = True
        # USRP
        if usrp_device_name is not None:
            self.usrp_device = uhd.usrp.MultiUSRP(
                "send_frame_size=10000, recv_frame_size=10000, num_recv_frames=1000, serial=" + usrp_device_name
            )
        else:
            self.usrp_device = uhd.usrp.MultiUSRP(
                "send_frame_size=10000, recv_frame_size=10000, num_recv_frames=1000"
            )
        # Setup RX and TX
        self.set_rx()
        self.set_tx()

    def set_tx(self) -> None:
        """ Sets up the USRP TX """
        try:
            # Set TX center frequency
            self.usrp_device.set_tx_rate(self.sample_rate, 0)
            self.usrp_device.set_tx_freq(
                uhd.libpyuhd.types.tune_request(self.center_freq), 0
            )
            # Set TX gain
            self.usrp_device.set_tx_gain(self.tx_gain, 0)
            # wait until the lo's are locked
            while not self.usrp_device.get_tx_sensor("lo_locked", 0).to_bool():
                print('waiting for usrp lo lock')
                sleep(0.01)
            # setup stream and receive buffer
            st_args = uhd.usrp.StreamArgs("fc32", "sc16")
            st_args.channels = [0]
            self.tx_streamer = self.usrp_device.get_tx_stream(st_args)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def set_rx(self) -> None:
        """ Sets up the USRP RX """
        try:
            # Set RX center frequency
            self.usrp_device.set_rx_rate(self.sample_rate, 0)
            self.usrp_device.set_rx_freq(
                uhd.libpyuhd.types.tune_request(self.center_freq), 0
            )
            # Set RX gain
            self.usrp_device.set_rx_gain(self.rx_gain, 0)
            self.usrp_device.set_rx_antenna("TX/RX", 0)
            # Setup the stream buffer and recieve buffer
            st_args = uhd.usrp.StreamArgs("fc32", "sc16")
            st_args.channels = [0]
            # Setup rx_streamer
            self.rx_streamer = self.usrp_device.get_rx_stream(st_args)
            self.rx_streamer.issue_stream_cmd(self.rx_stream_cmd)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise

    def tx_data(self, data:np.ndarray) -> None:
        """ Sends data out over the USRP 
        
        Arguments:
            data (np.ndarray): The packet to be transmitted.
        """
        self.tx_streamer.send(data, self.tx_meta_data)
        self.tx_streamer.send(np.zeros(10, dtype=np.complex64), self.tx2_meta_data)

    def rx_data(self) -> np.ndarray:
        """ Recieve data from the USRP """
        self.recv_buffer = np.zeros(
            (1, self.rx_streamer.get_max_num_samps() * 10), dtype=np.complex64
        )
        self.rx_streamer.recv(self.recv_buffer, self.rx_meta_data, 0.1)
        if self.rx_meta_data.error_code != uhd.types.RXMetadataErrorCode.none:
            print(f'error: {self.rx_meta_data.strerror()}')
        return self.recv_buffer

if __name__ == "__main__":
    sdr = SDR(15000000.0, 915000000.0, 70, 74, None)
    sleep(1)
    print("attempting to TX")
    dummy_data = randint(0, 1, 20)
    sdr.tx_data(dummy_data)