import aigolearning

if __name__ == '__main__':
    dateList = aigolearning.expandClassDates("09/15/2022-01/05/2023", "Thu 19:00-20:00")
    print(len(dateList))
    for date in dateList:
        print(str(date[0]) + "\t" + str(date[1]))
