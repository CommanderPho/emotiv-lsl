from enum import Enum, auto

class HardwareConnectionBackend(Enum):
    """Description of the enum class and its purpose."""
    USB = auto()
    BLUETOOTH = auto()
    # THIRD = auto()

    def __str__(self):
        return self.name

    @classmethod
    def list_values(cls):
        """Returns a list of all enum values"""
        return list(cls)

    @classmethod
    def list_names(cls):
        """Returns a list of all enum names"""
        return [e.name for e in cls]


class CyKitCompatibilityHelpers:
    """ 
     from emotiv_lsl.helpers import HardwareConnectionBackend, CyKitCompatibilityHelpers
    """
    @classmethod
    def get_sn(cls, model, serial_number, a_backend: HardwareConnectionBackend):
        """ 
        k, samplingRate, channels = CyKitCompatibilityHelpers.get_sn(model=self.KeyModel, serial_number=serial_number, a_backend=a_backend)
        
        """
        sn = bytearray()

        for i in range(0,len(serial_number)):
            if a_backend.value == HardwareConnectionBackend.BLUETOOTH.value:
                sn += bytearray([serial_number[i]])
            else:
                sn += bytearray([ord(serial_number[i])])

        # if len(sn) != 16:
        #     return           
        assert len(sn) == 16, f"{len(sn)} != 16, '{sn}"
        
        k = ['\0'] * 16        

        # --- Model 1 > [Epoc::Premium]
        if model == 1:
            k = [sn[-1],00,sn[-2],72,sn[-1],00,sn[-2],84,sn[-3],16,sn[-4],66,sn[-3],00,sn[-4],80]
            samplingRate = 128
            channels = 40

        # --- Model 2 > [Epoc::Consumer]
        if model == 2:   
            k = [sn[-1],00,sn[-2],84,sn[-3],16,sn[-4],66,sn[-1],00,sn[-2],72,sn[-3],00,sn[-4],80]
            samplingRate = 128
            channels = 40

        # --- Model 3 >  [Insight::Premium]
        if model == 3:
            k = [sn[-2],00,sn[-1],68,sn[-2],00,sn[-1],12,sn[-4],00,sn[-3],21,sn[-4],00,sn[-3],88]
            samplingRate = 128
            channels = 20

        # --- Model 4 > [Insight::Consumer]
        if model == 4: 
            k = [sn[-1],00,sn[-2],21,sn[-3],00,sn[-4],12,sn[-3],00,sn[-2],68,sn[-1],00,sn[-2],88]
            samplingRate = 128
            channels = 20

        # --- Model 5 > [Epoc+::Premium]
        if model == 5:
            k = [sn[-2],sn[-1],sn[-2],sn[-1],sn[-3],sn[-4],sn[-3],sn[-4],sn[-4],sn[-3],sn[-4],sn[-3],sn[-1],sn[-2],sn[-1],sn[-2]]
            samplingRate = 256
            channels = 40

        # --- Model 6 >  [Epoc+::Consumer]
        if model == 6:
            k = [sn[-1],sn[-2],sn[-2],sn[-3],sn[-3],sn[-3],sn[-2],sn[-4],sn[-1],sn[-4],sn[-2],sn[-2],sn[-4],sn[-4],sn[-2],sn[-1]]
            samplingRate = 256
            channels = 40

        # --- Model 7 > [EPOC+::Standard]-(14-bit mode)
        if model == 7: 
            k = [sn[-1],00,sn[-2],21,sn[-3],00,sn[-4],12,sn[-3],00,sn[-2],68,sn[-1],00,sn[-2],88]
            samplingRate = 128
            channels = 40

            # 1223332414224421
        if a_backend.value == HardwareConnectionBackend.BLUETOOTH.value:
            return bytes(bytearray(k)), samplingRate, channels
        else:
            return k, samplingRate, channels
