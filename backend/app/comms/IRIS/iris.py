import mvp_packets
from iris_packet import IRISPacket
#import iris_event_handler

class IRIS:
    
    def __init__(self, irispacket: IRISPacket):
        self.devID: int
        #self.IrisEventHandler: IrisEventHandler
        self.requestInPropgressPacket: irispacket
