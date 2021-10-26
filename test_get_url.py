with open("race_URL"+ "/" + str(2021) + "-" + str(1020) + ".txt", mode='r') as f:
    pre_url_num = len(f.readlines())
    print(pre_url_num)