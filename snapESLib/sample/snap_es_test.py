import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import snapEsLib as esLib 

esInfo = esLib.snapESConnectUsingHost("localhost", 9200)

res = esLib.snapESDeleteIndex(esInfo, "lspstatistics")
res = esLib.snapESDeleteIndex(esInfo, "flowstatistics")

res = esLib.snapESGetAllIndices(esInfo)
print("All Indices:\n{result:s}".format(result = res["data"]))

res = esLib.snapESDeleteIndexTemplate(esInfo, "statistics")
fileLoc = "lspStats_template.json"
res = esLib.snapESAddIndexTemplate(esInfo, "statistics", fileLoc)
if "data" in res.keys():
	print(res["data"])
else:
	print(res["result"])


res = esLib.snapESCreateIndex(esInfo, "lspstatistics", True)
print(res["result"])

#res = esLib.snapESCreateIndex(esInfo, "flowstatistics", True)
#print(res["result"])

res = esLib.snapESGetAllIndices(esInfo)
print("All Indices:\n{result:s}".format(result = res["data"]))

#Generate Data

fileLoc = "test.txt"
res = esLib.snapESWriteBulkData(esInfo, "lspstatistics", "statsdata", fileLoc)
if "data" in res.keys():
	print(res["data"])
elif "errInfo" in res.keys():
	print(res["errInfo"])
else:
	print(res["result"])

#res = esLib.snapESDeleteIndex(esInfo, "statistics")
#res = esLib.snapESGetAllIndices(esInfo)
#print(res["data"])


#Below lib call works
#res = esLib.snapESGetAllIndices(es)
#print(res)

#res = esLib.snapESIsExistingIndice(es, ".kibana")
#print(res)
