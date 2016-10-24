import  elasticsearch as esObj
import  requests as req
import  json
import  collections

OK   = "ok"
FAIL = "fail"

################### snapESConnectUsingHost ###########################################
# API to connect to the elasticsearch instance on a host.
#    @input:  
#        hostname         = hostname of the elastic search host
#        port             = port on which elastic search instance is running
#    @output  
#        esInfo           =  This is the main obj that this library returns.
#                            Holds the esClient handle  esInfo["client"]
#################################################################################
def snapESConnectUsingHost(hostname, port):
    esInfo = dict()
    esInfo["host"]    = str(hostname) + ":" + str(port)
    try:
        es = esObj.Elasticsearch([{'host': hostname, 'port': port }])
        esInfo["client"]  = es
    except Exception as err:
        pass
    return esInfo

################### snapESGetAllIndices ###########################################
# API to get the client handle from the libEs
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successful operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESGetClientHandle(esInfo):
    """
    Comment
    """
    esClient = None
    if esInfo.has_key("client") == True:
        esClient = esInfo["client"]
    return esClient

################### snapESGetAllIndices ###########################################
# Get All the indices in elasticsearch instance
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successful operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESGetAllIndices(esInfo):
    """
    Comment
    """
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)

    if esClient == None:
        res["result"] = FAIL
        return res

    try:
        res["data"] = esClient.cat.indices()
    except esObj.ElasticsearchException  as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args
        pass
    return res


################### snapESDeleteIndex ###########################################
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successful operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESDeleteIndex(esInfo, indexName):
    """
    Comment
    """
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)

    if esClient.indices.exists(indexName) == False:
        return res
    try:
        esClient.indices.delete(index=indexName)
    except esObj.ElasticsearchException as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args
        pass
    return res


################### snapESCreateIndex ###########################################
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#        indexName        = name of the ES template to add
#        deleteIfExists   = T/F if existing index needs to be deleted
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successfull operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESCreateIndex(esInfo, indexName, deleteIfExists):
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)

    if esClient.indices.exists(indexName) == True:
        if deleteIfExists:
            res = snapESDeleteIndex(esInfo, indexName)
        else:
            res["result"] = FAIL

    if res["result"] == OK:
        try:
            esClient.indices.create(index=indexName)
        except esObj.ElasticsearchException as err:
            res["result"] = FAIL
            res["errorInfo"] = err.args
            pass
    return res


#############   snapESAddIndexTemplate ###########################################
# API to add a template in elastic search
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#        templateName     = name of the ES template to add
#        templateFile     = location of file with template definition
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successfull operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESAddIndexTemplate(esInfo, templateName, templateFile):
    """
    Comment
    """
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)

    try:
        with open(templateFile, 'rb') as templateData:    
            r = esClient.indices.put_template(templateName, body=templateData.read())
            r = snapConvertESReply(r)
            res["data"] = r
    except esObj.ElasticsearchException   as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args
        pass

    templateData.close()
    return res


#############   snapESDeleteIndexTemplate #######################################
# API to delete the template in ElasticSearch
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#        templateName     = name of the ES template to delete
#    @output  
#        res dict obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successfull operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESDeleteIndexTemplate(esInfo, templateName):
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)
    url           = "http://"+esInfo["host"]+"/_template/"+templateName
    try:    
        r= req.delete(url)
        res["data"] = r.json()
    except req.RequestException  as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args

    return res


#############   snapESWriteBulkData #############################################
# API to write bulk data to ElasticSearch from a file
#    @input:  
#        esInfo           = library obj with ElasticSearch Info
#        indexName        = name of the ES Index
#        docType          = index doc type
#        filePath         = file to read the data from
#    @output  
#        res dictionary obj
#        res["result"]    = OK/FAIL
#        res["data"]      = Data to be returned in case of successfull operation
#        res["errInfo"]   = Err info due the the operation
#################################################################################
def snapESWriteBulkData(esInfo, indexName, docType, filePath):
    res           = dict()
    res["result"] = OK
    esClient      = snapESGetClientHandle(esInfo)
    try:    
        with open(filePath, 'rb') as fd:
            r = esClient.bulk(index=indexName, doc_type=docType, body=fd.read())
            r = snapConvertESReply(r)
            if(r["errors"] == True):
                res["result"]  = FAIL
                res["errInfo"] = r
            else:
                res["data"] = "Successfully written data." \
                               "Time Taken: {time:d} ms".format(time= r["took"])
    except esObj.ElasticsearchException   as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args
        pass
    except IOError as err:
        res["result"] = FAIL
        res["errorInfo"] = err.args
        pass

    fd.close()
    return res


#############   snapConvertESReply #############################################
# API to convert Elastic search operations response in correct format
#    @input:  
#        reply - ES response for a any operation. 
#    @output  
#        reply - Properly fomatted reply (non-unicode)
################################################################################
def snapConvertESReply(reply):
    if isinstance(reply, basestring):
        return str(reply)
    elif isinstance(reply, collections.Mapping):
        return dict(map(snapConvertESReply, reply.iteritems()))
    elif isinstance(reply, collections.Iterable):
        return type(reply)(map(snapConvertESReply, reply))
    else:
        return reply
