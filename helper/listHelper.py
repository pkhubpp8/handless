def printList(tmpList, logger):
    if not tmpList:
        logger.info("空")
    else:
        for url in tmpList:
            logger.info(url)