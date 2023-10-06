def printList(tmpList):
    if not tmpList:
        logger.info("空")
    else:
        for url in tmpList:
            logger.info(url)