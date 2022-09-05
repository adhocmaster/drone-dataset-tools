import pandas as pd
from sortedcontainers import SortedList
import logging

class LocationData:

  def __init__(self, locationId, recordingIds, recordingDataList):
    self.locationId = locationId
    self.recordingIds = recordingIds
    self.recordingDataList = recordingDataList

    self.recordingMetaList = [recordingData.recordingMeta for recordingData in recordingDataList]
    self.validateRecordingMeta()

    self.frameRate = self.recordingMetaList[0]["frameRate"]
    self.orthoPxToMeter = self.recordingMetaList[0]["orthoPxToMeter"]
  
    # cache
    self.__crossingDf = None
    self.__crossingIds = None

  

  def validateRecordingMeta(self):
    sameValueFields = [
      "locationId",
      "frameRate",
      # "latLocation",
      # "lonLocation",
      # "xUtmOrigin",
      # "yUtmOrigin",
      "orthoPxToMeter"
      ]
    
    firstMeta = self.recordingMetaList[0]
    for otherMeta in self.recordingMetaList:
      for field in sameValueFields:
        if firstMeta[field] != otherMeta[field]:
          raise Exception(f"{field} value mismatch for {firstMeta['recordingId']} and {otherMeta['recordingId']}")

  def getUniqueCrossingIds(self):
    """
    returns unique pedestrian ids
    """

    if self.__crossingIds is None:
      self.__crossingIds = SortedList()
      for recordingData in self.recordingDataList:
        # crossingIds = recordingData.getCrossingIds()
        try:
          crossingDf = recordingData.getCrossingDf()
          if "uniqueTrackId" in crossingDf:
            uniqueIds = crossingDf.uniqueTrackId.unique()
            logging.info(f"crossing ids for {recordingData.recordingId}: {recordingData.getCrossingPedIds()}")
            logging.info(f"uniqueIds for {recordingData.recordingId}: {uniqueIds}")
            self.__crossingIds.update(uniqueIds)
          else:
            logging.warn(f"{recordingData.recordingId} does not have uniqueTrackId")
        except Exception as e:
          logging.warn(f"{recordingData.recordingId} has exception: {e}")

    
    return self.__crossingIds

  def getCrossingDfByUniqueTrackId(self, uniqueTrackId):
    return self.getCrossingDfByUniqueTrackIds([uniqueTrackId])

  def getCrossingDfByUniqueTrackIds(self, uniqueTrackIds):
      crossingDf = self.getCrossingDf()
      criterion = crossingDf['uniqueTrackId'].map(lambda uniqueTrackId: uniqueTrackId in uniqueTrackIds)
      return crossingDf[criterion]

  def getCrossingDf(self):
    if self.__crossingDf is None:
      dfs = []
      for recordingData in self.recordingDataList:
        try:
          dfs.append(recordingData.getCrossingDf())
        except Exception as e:
          logging.warn(f"{recordingData.recordingId} has exception: {e}")

      self.__crossingDf = pd.concat(dfs, ignore_index=True)
    
    return self.__crossingDf





