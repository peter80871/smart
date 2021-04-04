import requests

def finder(t1, t2):
    t1_matches = requests.get(f'https://m.melbet.ru/LineFeed/Web_SearchZip?text={t1}&limit=150&lng=ru&partner=195&mode=6')
    t2_matches = requests.get(f'https://m.melbet.ru/LineFeed/Web_SearchZip?text={t2}&limit=150&lng=ru&partner=195&mode=6')

    matches1 = t1_matches.json()
    matches2 = t2_matches.json()
   
    matches1 = matches1['Value']
    matches2 = matches2['Value']
    total_t1_b, total_t1_m, total_t2_b, total_t2_m = '~','~','~','~'
    try:
        for match in matches1:
            for match2 in matches2:
                if match2['CI'] == match['CI']:
                    LI = match['LI']    # leageu code (first arg)
                    CI = match['CI']    # match code
                    LE = match['LE']    # league name
                    O1 = match['O1E']   # first team
                    O2 = match['O2E']   #second team
                   
                    id_t = requests.get(f'https://m.melbet.ru/LineFeed/GetGameZip?id={CI}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=50&partner=195&grMode=2').json()

                    I = id_t['Value']['SG'][0]['I']

                    l = O1.split()
                    O1 = '-'.join(l)
                    l = O2.split()
                    O2 = '-'.join(l)  
                    
                    LE = LE.split('.')
                    LE = ''.join(LE)
                    l = LE.strip('.').split()
                    LE = '-'.join(l)  

                    #href = f'https://m.melbet.ru/line/Football/{LI}-{LE}/{CI}-{O1}-{O2}'    #https://m.melbet.ru/LineFeed/GetGameZip?id=96230530&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=50&partner=195&grMode=2
                    
                    rrrr = requests.get(f'https://m.melbet.ru/LineFeed/GetGameZip?id={I}&lng=ru&cfview=0&isSubGames=true&GroupEvents=true&countevents=200&partner=195&grMode=2').json()

                    all_params = rrrr['Value']
                    all_totals = all_params['GE']
                    
                    total_t1_b = all_totals[7]['E'][0][0]['C'] 
                    total_t1_m = all_totals[7]['E'][1][0]['C']

                    total_t2_b = all_totals[9]['E'][0][0]['C']
                    total_t2_m = all_totals[9]['E'][1][0]['C']

    except:
        print('no kf')

    return total_t1_b, total_t1_m, total_t2_b, total_t2_m

#print(finder())