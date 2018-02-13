import numpy



class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.signalHeader = None
        self.signalBuffer = list()
        self.bol=False
        self.bolPrinted=False



    def process(self):
        for chunkIndex in range(len(self.input[0])):
            if type(self.input[0][chunkIndex]) == OVSignalHeader:
                self.signalHeader = self.input[0].pop()

                # Generate a Stimulation Header for the Output
                outputHeader=OVStimulationHeader(self.signalHeader.startTime, self.signalHeader.endTime)


                # Push the stimulation header out to exit
                self.output[0].append(outputHeader)
            elif type(self.input[0][chunkIndex]) == OVSignalBuffer:
                chunk = self.input[0].pop()

                # original signal shape
                shape = numpy.array(chunk).shape

                # get the information about number of channels and signal length
                new_shape = tuple(self.signalHeader.dimensionSizes)

                # number of channels and signal length
                (chNo, signalLen) = new_shape

                # reshape the buffer to be more intuitive
                numpy_buffer = numpy.array(chunk).reshape(new_shape)

                y = numpy_buffer[0, :]

                stimulationOutput=OVStimulationSet(chunk.startTime,chunk.endTime)


                for ch in range(0, chNo):
                    y = numpy_buffer[ch, :]
                    for value in y:
                        if value==1:
                            self.bol=True
                        else:
                            self.bol=False


                        if self.bol!=self.bolPrinted:
                            if self.bol:
                                #Create Stimulation for Begin
                                stimulusON=OVStimulation(0x300,self.getCurrentTime(),0)
                                stimulationOutput.append(stimulusON)

                            else:
                                #Create Stimulation for END
                                stimulusOFF=OVStimulation(0x320,self.getCurrentTime(),0)
                                stimulationOutput.append(stimulusOFF)
                            self.bolPrinted=self.bol


                self.output[0].append(stimulationOutput)
                stimulationOutput=None

            elif (type(self.input[0][chunkIndex]) == OVSignalEnd):

                self.input[0].pop()
                self.output[0].append(OVStimulationEnd(None))


box = MyOVBox()
