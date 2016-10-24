#!/usr/bin/python

import json
import collections
import datetime
import elasticsearch
import ipaddress
import argparse
import random
import copy


def main(argparse):
    timeStampList   = []
    lspList         = []
    flowList        = []
    dataList        = []

    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(prog='dataGenerator.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-lsps", metavar=" numofLsps", help="Total number of lsps to simulate", type=int, default=5)
    parser.add_argument("-flows", metavar="numofFlows", help="Total number of flows. Split accross lsps", type=int, default=5)
    parser.add_argument("-time",  metavar=" days:hr:min", help="Duration to simulate the data", default="0:0:5")
    parser.add_argument("-intvl",  metavar="interval", help="Frequency to collect the stats in sec", type=int, default=30)
    parser.add_argument("-file",  metavar=" filepath", help="File to write flow data", default="stdout")
    args = parser.parse_args()

    intvl           = args.intvl
    numlsps         = args.lsps
    numFlows        = args.flows
    timeToSimulate  = args.time
    file            = args.file

    # Populate the Lsp in to a list
    populateLspInfo(numlsps, lspList)

    # Populate flows
    #populateFlowInfo(numFlows, flowList)

    ##Generate the required timestamps
    timeStampGenerator(timeToSimulate, intvl, timeStampList)

    # Assign flows to the lsps
    #mapFlowsToLsps(flowList, lspList)

    ##Collect stats for each timeStamp
    for ts in timeStampList:
        for lsp in lspList:
            lsp["TimeStamp"] = ts
            collectLspStats(lsp)
            dataList.append(copy.deepcopy(lsp))

    saveToFile(file, dataList)
    #writeToES(dataList)

'''
def writeToES(dataList):
    es1 = elasticsearch.Elasticsearch()
    #import pdb;pdb.set_trace()
    for item in dataList:
        item = dict(item)
        #item['Flows'] = dict(item['Flows'])
        es1.index(index="netanalysis", doc_type="net", body=item)
'''
   

def populateLspInfo(numLsps, lspList):
    senderIp = ipaddress.ip_address(u'1.1.1.1')
    srcIp    = ipaddress.ip_address(u'1.1.1.1')
    destIp   = ipaddress.ip_address(u'150.1.1.1')
    for lsp in range(numLsps):
        lspInfo  = collections.OrderedDict()
        lsp += 1; srcIp += 1; destIp += 1

        lspInfo["Sender"]    = str(srcIp)
        lspInfo["LspName"]   = "LSP_" + str(lsp)
        lspInfo["LspId"]     = lsp
        lspInfo["Src"]       = str(srcIp)
        lspInfo["Dest"]      = str(destIp)
        lspInfo["Type"]      = "rsvp"
        lspInfo["TimeStamp"] = ""
        lspList.append(lspInfo)
    return lspList


def populateFlowInfo(numFlow, flowList):
    for flows in range(numFlow):
        flowInfo = dict()
        flowInfo["Id"] = "Flow"+str(flows+1)
        ##toDo varilable const
        #flowInfo["Stats"] = 2000
        collectStats(flowInfo)
        flowList.append(flowInfo)
    return flowList


def mapFlowsToLsps(flowList, lspList):
    lenOfFlowList = len(flowList)
    lenOfLspList  = len(lspList)
    lspInfo  = collections.OrderedDict()
    flows    = []
    lspIter  = 0
    if lenOfFlowList == 0:
        return
    if lenOfLspList == 0:
        return
    for f in flowList:
        #loop over
        lspInfo  = lspList[lspIter]
        if "Flows" in lspInfo.keys():
            flows = lspInfo["Flows"]
            flows.append(f)
        else:
            flows.append(f)
            lspInfo["Flows"] = flows
        flows = []
        lspIter+=1
        if lspIter == (lenOfLspList):
            lspIter = 0
    return flowList, lspList


def timeStampGenerator(totalTime, intvl, tsList):
    duration = totalTime.split(':')
    day = int(duration[0])
    hrs = int(duration[1])
    min = int(duration[2])
    totalsec = 0
    if day:
        totalsec += day * 24 * 3600
    if hrs:
        totalsec += hrs * 3600
    if min:
        totalsec += min * 60

    t1 = datetime.datetime.now()
    t2 = t1 + datetime.timedelta(seconds=totalsec)

    while t1 < t2:
        #tsList.append(t1.strftime("%Y-%M-%D %H:%M:%S"))
        #t1 = t1 + datetime.timedelta(seconds=intvl)
        tsList.append(int(t1.strftime("%s")) * 1000)
        t1 = t1 + datetime.timedelta(seconds=intvl)
    tsList.append(int(t2.strftime("%s"))*1000)
    #tsList.append(t2.strftime("%Y-%M-%D %H:%M:%S"))

##
# for each timestamp, populate each lsp and each flow with that lsp with stats
# mode of stats : random, constant, incremental
#
def collectLspStats(lsp):
    lspStats = dict()

    loBaseM = random.randint(1, 5)
    hiBaseM = random.randint(1, 5)
    kbps_low  = 1500 * loBaseM
    kbps_hi   = kbps_low * hiBaseM
    kbps = random.randint(kbps_low, kbps_hi)
    lspStats["kbps"] = kbps

    pps_low  = 200 * loBaseM
    pps_high = pps_low * hiBaseM
    pps = random.randint(pps_low, pps_high)
    lspStats["pps"] = pps
    lsp["Stats"] = lspStats



def saveToFile(fileName, lspList):
    flow_list = []
    newLsp = collections.OrderedDict()
    index = {}
    ids   = {}
    i =0
    if fileName == "stdout":
        #print(json.dumps(lspList))
        print(json.dumps(lspList, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
    else:
        with open(fileName, "w") as f:
            #f.write(json.dumps(lspList, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
            for lsp in lspList:
                i+=1
                ids["_id"] = i
                index["index"] = {}
                f.write(json.dumps(index))
                f.write("\n")
                f.write(json.dumps(lsp))
                f.write("\n")
        f.close()


if __name__ == "__main__":
   main(argparse)
