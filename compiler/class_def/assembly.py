from collections import OrderedDict
from conversions.helpers import *

class Assembly:
    def __init__(self, lang):
        self.dataMem = OrderedDict(); 
        self.progMem = [];
        #count of the last temp variable used
        #if is count=3 then t3 was used last
        self.stackCount = 0;
        #list of number of times a reserved word was used
        self.reservedCount = {};

        if lang == 'cl':
            self.allocateGlobalIdMem();

    #call this to get a keyword with a count appended to it to
    #avoid multiple label pointing to different locations
    def getNextReserved(self,keyword):
        if keyword in self.reservedCount:
            self.reservedCount[keyword] += 1;

        else:
            self.reservedCount[keyword] = 0;

        return str(keyword) + str(self.reservedCount[keyword]);

    def getNextTemp(self):
        temp = "t" + str(self.stackCount);
        self.stackCount +=1;
        return temp;

    def subleq(self,a,b,c):
        self.progMem.append(subleq(a,b,c));

    def allocateGlobalIdMem(self):

        #allocate memory for global ids
        self.dataMem["work_dims"] = "%_work_dimensions"; #11 is the maximum number of dimensions allowed
        for i in range(0,11):
            self.dataMem["glob_ids" + str(i)] = "%_initIndex" + str(i);

        self.dataMem["glob_ids"] = "&glob_ids0";

        #allocate memory for the maximum id, if the id equals this value, the core knows to stop
        for i in range(0,11):
            self.dataMem["glob_idsMax" + str(i)] = "%_maxIndex" + str(i); 

        self.dataMem["glob_idsMax"] = "&glob_idsMax0";

    def generateKernelLoop(self):
        t2 = self.getNextTemp();
        t0 = self.getNextTemp();
        checkReady = self.getNextReserved("checkReady");
        

        for i in range(10,-1,-1):
            t0 = self.getNextTemp();
            t1 = self.getNextTemp();
            t2 = self.getNextTemp();
            dim = "dim" + str(i);
            globalMax = "glob_idsMax" + str(i);
            globalIds = "glob_ids" + str(i);
            finish = self.getNextReserved("finish");
            startLoop = self.getNextReserved("startLoop");

            #put the beginning of the loop before everything

            self.progMem.insert(0,subleq(dim + ":" + t0,t0,"NEXT"));
            self.progMem.insert(1,subleq(globalMax,t0,"NEXT"));
            self.progMem.insert(2,subleq(t1,t1,"NEXT"));
            self.progMem.insert(3,subleq(t0,t1,"NEXT"));
            self.progMem.insert(4,subleq(globalIds,t1,finish));

            #put the increment stage at the end of everything
            self.progMem.append("\n");
            self.subleq(-1,globalIds,"NEXT");
            self.subleq(t0,t0,dim);

            #noop for the finish
            self.progMem.append(next_subleq(finish + ":" + t0, t0));

        self.subleq("doneFlag","doneFlag","NEXT"); #after the core is done execution, set its done flag and clear the ready flag
        self.subleq(-1,"doneFlag","NEXT");
        self.subleq("#8200","#8200","#0");

        self.dataMem["0"] = 0;
        self.dataMem["1"] = 1;
        self.dataMem["-1"] = -1;
        self.dataMem["-2"] = -2;
        self.dataMem["doneFlag"] = "%_doneflag"
