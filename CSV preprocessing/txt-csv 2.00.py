import csv
import re

class test1_:
    #adds file and init. variables
    def input(self, fileInput='104_TT_150C.txt'):
        self.fileName=fileInput
        self.fileLinesNo = sum(1 for line in open(fileInput))
        self.lineLeakageStart = -1
        self.lineLeakageEnd = -1

    #sanitizes input
    def sanitize(self, lineTemp, lineNo):
        lineTemp = re.sub("TestValue", "TestValue,P/F", lineTemp)

        #removes - < : from file
        lineTemp = re.sub("[-]+", "", lineTemp)
        lineTemp = re.sub("<", "", lineTemp)
        lineTemp = re.sub(":", "", lineTemp)

        #appends units on numbers and removes whitespace between
        lineTemp = re.sub("[\s]+(mV)[\s]", "_mV ", lineTemp)
        lineTemp = re.sub("[\s]+(mA)[\s]", "_mA ", lineTemp)
        lineTemp = re.sub("[\s]+(mS)[\s]", "_mS ", lineTemp)
        lineTemp = re.sub("[\s]+(V)[\s]", "_V ", lineTemp)
        lineTemp = re.sub("[\s]+(uA)[\s]", "_uA ", lineTemp)

        #edge cases
        lineTemp = re.sub("[\s](Cont)[\s](N)[\s]", " Cont_N ", lineTemp)
        lineTemp = re.sub("[\s](TOTAL)[\s](TEST)[\s](TIME)[\s]", " TOTAL_TEST_TIME ", lineTemp)

        #same as above but checks in case it doesnt end in whitespace
        lineTemp = re.sub("[\s]+(mV)(\Z)", "_mV", lineTemp)
        lineTemp = re.sub("[\s]+(mS)(\Z)", "_mS", lineTemp)
        lineTemp = re.sub("[\s]+(mA)(\Z)", "_mA", lineTemp)
        lineTemp = re.sub("[\s]+(V)(\Z)", "_V", lineTemp)
        lineTemp = re.sub("[\s]+(uA)(\Z)", "_uA", lineTemp)
        lineTemp = re.sub("[\s]+(N)(\Z)", "_N", lineTemp)

        #removes all space
        lineTemp = re.sub("\A\s+\Z", "", lineTemp)
        lineTemp = re.sub("\s+", ",", lineTemp)
        return lineTemp

    def genLines(self):
        #open file
        with open(self.fileName, 'r') as in_file:
            #output list
            self.allLines = []
            self.meta = []
            self.throwawayData = []
            self.pinsData = []
            self.leakageData = []
            self.vminStdData = []
            self.vminAutoData = []
            self.memYdData = []

            pinsOn = 0
            firstLeakageFlag=0
            firstStdVminFlag=0
            firstAutoVminFlag=0
            vminAutoShmooFlag=0
            firstMemYdFlag=0
            counter=0
            for line_number, line in enumerate(in_file, 1):

                #removes inital and final whitespace
                lineTemp = line.strip()
                #santizes the lines
                lineTemp = self.sanitize(lineTemp, line_number)
                #splits on commas
                lineFinal = lineTemp.split(",")
                if(re.match("SITE",lineTemp)):
                    counter+=1
                    self.allLines.append(lineFinal)
                if(not re.search("^$",lineTemp)):
                    #appends to an array and returns it class wide
                    self.allLines.append(lineFinal)

                    #checks if running times
                    if(counter > 1):
                        self.meta.append(lineFinal)
                    else:
                        #checks if it is a pin data line
                        if(re.search("\ATSTNum,Pin,Chn",lineTemp) or (len(lineFinal) is 10) or (len(lineFinal) is 11)):
                            if(not (lineFinal[0]=="TstNum")):
                                if(lineFinal[9] != "(F)"):
                                    lineFinal.insert(9,"(P)")
                            self.pinsData.append(lineFinal)
                        if(re.search("\Atb_leakage_",lineTemp)):
                            if(firstLeakageFlag is 0):
                                firstLeakageFlag = 1
                                tempList = ["Test","Testing_Item","Test_(Repeat)","Range","Value"]
                                self.leakageData.append(tempList)

                            lineFinal.insert(1,re.match("[a-zA-Z0-9_]+(?=_leakage)",lineFinal[1]).group(0))
                            lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+(?=leakage)","",lineFinal[2])

                            lineFinal.insert(2,re.match("[a-zA-Z0-9_]+(?=_2uA)",lineFinal[2]).group(0))
                            lineFinal[3]=re.sub("\A[a-zA-Z0-9_]+(?=2uA)","",lineFinal[3])

                            self.leakageData.append(lineFinal)
                        if(re.search("\A[0-9]+,tb_sc_yd_vmin_shm",lineTemp) or re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                            if(firstStdVminFlag is 0):
                                firstStdVminFlag = 1
                                tempList = ["Test_Number","Test_Type","Testing_Item","Test_Type","Library","Range","Result","Test_Type_(Shmoo)","Testing_Item_(Shmoo)","Library_(Shmoo)","Result_(Shmoo)"]
                                self.vminStdData.append(tempList)

                            if(re.search("\Ashmoo_bsmin_vec_stdcell_",lineTemp)):
                                lineFinal.insert(0,re.match("[a-zA-Z0-9_]+(?=_sc)",lineFinal[0]).group(0))
                                lineFinal[1]=re.sub("\A[a-zA-Z0-9_]+(?=sc)","",lineFinal[1])

                                lineFinal.insert(1,re.match("[a-zA-Z0-9_]+(?=_sfk)",lineFinal[1]).group(0))
                                lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+(?=sfk)","",lineFinal[2])

                                self.vminStdData[len(self.vminStdData)-1].extend(lineFinal)
                            else:
                                lineFinal.insert(2,re.match("[a-zA-Z0-9_]+(?=_sc)",lineFinal[2]).group(0))
                                lineFinal[3]=re.sub("\A[a-zA-Z0-9_]+(?=sc)","",lineFinal[3])

                                lineFinal.insert(3,re.match("[a-zA-Z0-9_]+(?=_sfk)",lineFinal[3]).group(0))
                                lineFinal[4]=re.sub("\A[a-zA-Z0-9_]+(?=sfk)","",lineFinal[4])

                                lineFinal.insert(4,re.match("[a-zA-Z0-9_]+(?=_pattern)",lineFinal[4]).group(0))
                                lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+(?=pattern)","",lineFinal[5])

                                self.vminStdData.append(lineFinal)
                        if(re.match("[0-9]+?,tb_mem_yd_ckb",lineTemp)):
                            if(firstMemYdFlag is 0):
                                firstMemYdFlag = 1
                                tempList = ["Test_Number","Testing_Type","A/S","Test(META???)","Location_Type","Test_Location","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","RANGE","Value"]
                                self.memYdData.append(tempList)

                            lineFinal.insert(1,re.match("tb_mem_yd_ckb",lineFinal[1]).group(0))
                            lineFinal[2]=re.sub("\Atb_mem_yd_ckb_","",lineFinal[2])

                            lineFinal.insert(3,re.match("func_vec",lineFinal[3]).group(0))
                            lineFinal[4]=re.sub("\Afunc_vec_","",lineFinal[4])

                            if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[4]).group(0) == "cln16ffcll"):
                                lineFinal.insert(4,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[4]).group(0))
                                lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[5])
                            else:
                                lineFinal.insert(4,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[4]).group(0))
                                lineFinal[5]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[5])

                            lineFinal.insert(5,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0))
                            lineFinal[6]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[6])

                            lineFinal.insert(6,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[6]).group(0))
                            lineFinal[7]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[7])

                            lineFinal.insert(7,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[7]).group(0))
                            lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[8])

                            lineFinal.insert(8,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[8]).group(0))
                            lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[9])

                            lineFinal.insert(9,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[9]).group(0))
                            lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[10])

                            lineFinal.insert(10,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[10]).group(0))
                            lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[11])

                            lineFinal.insert(11,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[11]).group(0))
                            lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[12])

                            lineFinal.insert(12,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[12]).group(0))
                            lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[13])

                            lineFinal.insert(13,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[13]).group(0))
                            lineFinal[14]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[14])

                            lineFinal.insert(14,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[14]).group(0))
                            lineFinal[15]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[15])

                            lineFinal.insert(15,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[15]).group(0))
                            lineFinal[16]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[16])

                            lineFinal.insert(16,re.search("(?<=ken)[a-zA-Z0-9_]+?(?=_vddpe)",lineFinal[16]).group(0))
                            lineFinal[17]=re.sub("\A[a-zA-Z0-9_]+?(?=vddpe)","",lineFinal[17])

                            self.memYdData.append(lineFinal)
                        if(re.search("\A[0-9]+,tb_vmin_ckb",lineTemp) or (vminAutoShmooFlag is 1)):
                            if(firstAutoVminFlag is 0):
                                firstAutoVminFlag = 1
                                tempList = ["Test_Number","Test","A/S","Location_Type(Catagory)","Test(META???)","Location_Type","Test_Location","??","EMA#1","EMA#2","EMAW","EMAS","EMAP","WABL","WABLM","RAWL","RAWLM","KEN","RANGE","Value","Test_Type(Shmoo)","Location_Type(Shmoo)","Test_Location(Shmoo)","??(Shmoo)","EMA#1(Shmoo)","EMA#2(Shmoo)","EMAW(Shmoo)","EMAS(Shmoo)","EMAP(Shmoo)","WABL(Shmoo)","WABLM(Shmoo)","RAWL(Shmoo)","RAWLM(Shmoo)","KEN(Shmoo)","Value(Shmoo)"]
                                self.vminAutoData.append(tempList)

                            if(re.search("\A[0-9]+,tb_vmin_ckb",lineTemp)):
                                vminAutoShmooFlag=1

                                lineFinal.insert(1,re.match("tb_vmin_ckb",lineFinal[1]).group(0))
                                lineFinal[2]=re.sub("\Atb_vmin_ckb_","",lineFinal[2])

                                lineFinal.insert(2,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[2]).group(0))
                                lineFinal[3]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[3])

                                lineFinal.insert(4,re.match("Vmax_vec",lineFinal[4]).group(0))
                                lineFinal[5]=re.sub("\AVmax_vec_","",lineFinal[5])

                                if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0) == "cln16ffcll"):
                                    lineFinal.insert(5,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[5]).group(0))
                                    lineFinal[6]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[6])
                                else:
                                    lineFinal.insert(5,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[5]).group(0))
                                    lineFinal[6]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[6])

                                lineFinal.insert(6,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[6]).group(0))
                                lineFinal[7]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[7])

                                lineFinal.insert(7,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[7]).group(0))
                                lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[8])

                                lineFinal.insert(8,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[8]).group(0))
                                lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[9])

                                lineFinal.insert(9,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[9]).group(0))
                                lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[10])

                                lineFinal.insert(10,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[10]).group(0))
                                lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[11])

                                lineFinal.insert(11,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[11]).group(0))
                                lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[12])

                                lineFinal.insert(12,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[12]).group(0))
                                lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[13])

                                lineFinal.insert(13,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[13]).group(0))
                                lineFinal[14]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[14])

                                lineFinal.insert(14,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[14]).group(0))
                                lineFinal[15]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[15])

                                lineFinal.insert(15,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[15]).group(0))
                                lineFinal[16]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[16])

                                lineFinal.insert(16,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[16]).group(0))
                                lineFinal[17]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[17])

                                lineFinal.insert(17,re.search("(?<=ken)[a-zA-Z0-9_]+?(?=_vddpe)",lineFinal[17]).group(0))
                                lineFinal[18]=re.sub("\A[a-zA-Z0-9_]+?(?=vddpe)","",lineFinal[18])

                                self.vminAutoData.append(lineFinal)
                            else:
                                vminAutoShmooFlag=0

                                lineFinal.insert(0,re.match("shmoo_bsmin_vec",lineFinal[0]).group(0))
                                lineFinal[1]=re.sub("\Ashmoo_bsmin_vec_","",lineFinal[1])

                                if(re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[1]).group(0) == "cln16ffcll"):
                                    lineFinal.insert(1,re.match("[a-zA-Z0-9_]+?(?=_w)",lineFinal[1]).group(0))
                                    lineFinal[2]=re.sub("\A[a-zA-Z0-9_]+?(?=w)","",lineFinal[2])
                                else:
                                    lineFinal.insert(1,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[1]).group(0))
                                    lineFinal[2]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[2])

                                lineFinal.insert(2,re.match("[a-zA-Z0-9]+?(?=_)",lineFinal[2]).group(0))
                                lineFinal[3]=re.sub("\A[a-zA-Z0-9]+?_","",lineFinal[3])

                                lineFinal.insert(3,re.match("[a-zA-Z0-9_]+?(?=_ema)",lineFinal[3]).group(0))
                                lineFinal[4]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[4])

                                lineFinal.insert(4,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_ema)",lineFinal[4]).group(0))
                                lineFinal[5]=re.sub("\A[a-zA-Z0-9_]+?(?=ema)","",lineFinal[5])

                                lineFinal.insert(5,re.search("(?<=ema)[a-zA-Z0-9_]+?(?=_emaw)",lineFinal[5]).group(0))
                                lineFinal[6]=re.sub("\A[a-zA-Z0-9_]+?(?=emaw)","",lineFinal[6])

                                lineFinal.insert(6,re.search("(?<=emaw)[a-zA-Z0-9_]+?(?=_emas)",lineFinal[6]).group(0))
                                lineFinal[7]=re.sub("\A[a-zA-Z0-9_]+?(?=emas)","",lineFinal[7])

                                lineFinal.insert(7,re.search("(?<=emas)[a-zA-Z0-9_]+?(?=_emap)",lineFinal[7]).group(0))
                                lineFinal[8]=re.sub("\A[a-zA-Z0-9_]+?(?=emap)","",lineFinal[8])

                                lineFinal.insert(8,re.search("(?<=emap)[a-zA-Z0-9_]+?(?=_wabl)",lineFinal[8]).group(0))
                                lineFinal[9]=re.sub("\A[a-zA-Z0-9_]+?(?=wabl)","",lineFinal[9])

                                lineFinal.insert(9,re.search("(?<=wabl)[a-zA-Z0-9_]+?(?=_wablm)",lineFinal[9]).group(0))
                                lineFinal[10]=re.sub("\A[a-zA-Z0-9_]+?(?=wablm)","",lineFinal[10])

                                lineFinal.insert(10,re.search("(?<=wablm)[a-zA-Z0-9_]+?(?=_rawl)",lineFinal[10]).group(0))
                                lineFinal[11]=re.sub("\A[a-zA-Z0-9_]+?(?=rawl)","",lineFinal[11])

                                lineFinal.insert(11,re.search("(?<=rawl)[a-zA-Z0-9_]+?(?=_rawlm)",lineFinal[11]).group(0))
                                lineFinal[12]=re.sub("\A[a-zA-Z0-9_]+?(?=rawlm)","",lineFinal[12])

                                lineFinal.insert(12,re.search("(?<=rawlm)[a-zA-Z0-9_]+?(?=_ken)",lineFinal[12]).group(0))
                                lineFinal[13]=re.sub("\A[a-zA-Z0-9_]+?(?=ken)","",lineFinal[13])

                                self.vminAutoData[len(self.vminAutoData)-1].extend(lineFinal)
                else:
                    self.throwawayData.append(lineFinal)




    def genFullCSV(self, fileOutput="fullOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.allLines)

    def genMetaCSV(self, fileOutput="metaOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.meta)

    def genThrowawayCSV(self, fileOutput="ThrowawayOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.throwawayData)

    def genPinsCSV(self, fileOutput="pinsOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.pinsData)

    def genLeakageCSV(self, fileOutput="leakageOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.leakageData)

    def genStdVminCSV(self, fileOutput="vminStdOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.vminStdData)

    def genMemCSV(self, fileOutput="memYdOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.memYdData)

    def genAutoVminCSV(self, fileOutput="vminAutoOutput.csv"):
        #opens output file
        with open(fileOutput, "w") as out_file:
            #writes csv file from list
            writer = csv.writer(out_file)
            writer.writerows(self.vminAutoData)

test1 = test1_()
test1.input()
test1.genLines()
test1.genFullCSV()
test1.genMetaCSV()
test1.genThrowawayCSV()
test1.genPinsCSV()
test1.genLeakageCSV()
test1.genStdVminCSV()
test1.genMemCSV()
test1.genAutoVminCSV()
