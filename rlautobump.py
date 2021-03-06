import requests, json, time, urllib, sys
from datetime import datetime, timedelta
from random import randint
from bs4 import BeautifulSoup 

class Storage:
    data = {}

    def __init__(self):
        with open('data.json', 'r') as f:
            print('Loading user data from .json file..')
            self.data = json.load(f)
            print('Loaded successfully!')

    def uploadData(self):
        '''Uploading storage TO .json file'''
        with open('data.json', 'w') as f:
            print('Uploading data. Replacing .json file..')
            json.dump(self.data, f, indent=4)
            print('Uploaded successfully!')
    
    def updateStorage(self):
        '''Updating storage FROM .json file'''
        with open('data.json', 'r') as f:
            print('Loading data from .json file..')
            self.data = json.load(f)
            print('Loaded successfully!')

class Bumper:
    storage = Storage()
    session = requests.Session()
    allowed_modes = ['all-once-mode', 'inverse-mode']

    def randsleep(self, start, end, message='then retrying'):
        r = randint(start, end)
        print('Sleeping for %s sec %s..' %(r,message))
        time.sleep(r)

    def requestExceptionInfo(self, where):
        print('\nRequest error in (%s). Please, check your internet connection.' % where)
        self.randsleep(10, 21)

    def attributeExceptionInfo(self, where):
        print('\nAttribute error in (%s).' % where)
        self.randsleep(10,21)

    def find_csrf(self):
        url = 'https://rocket-league.com/contact'
        
        while(True):
            print('\nFinding token..')
            try:
                result = self.session.get(url)
            except requests.exceptions.RequestException:
                self.requestExceptionInfo('find_csrf')
                continue

            soup = BeautifulSoup(result.content, 'html.parser')
            try:
                contact = soup.find('form', attrs={'action': '/functions/contactForm.php'})
                token = contact.input['value']
            except AttributeError:
                self.attributeExceptionInfo('find_csrf')
                continue

            if token == None:
                print('Token was not found. Sleeping for 60sec then retrying..')
                time.sleep(60)
                continue
            else:
                print('Found token: csrf_token = [%s]' %token)
                return token

    def login(self):
        '''RL Garage login function'''
        user = self.storage.data['user']
        url = 'https://rocket-league.com/functions/login.php'
        cookie = {'acceptedPrivacyPolicy': '2.0'}

        while(True):
            user['csrf_token'] = self.find_csrf()
            print('\nLogging in..')
            try:
                result = self.session.post(
                    url,
                    data=user,
                    headers=dict(referer='https://rocket-league.com'),
                    cookies=cookie
                )
            except requests.exceptions.RequestException:
                self.requestExceptionInfo('login')
                continue
        
            status = result.status_code
            if 200 <= status < 300:
                try:
                    soup = BeautifulSoup(result.content, 'html.parser')
                    error = soup.find('p', attrs={'class': 'rlg-site-popup__text'}).string
                except AttributeError:
                    self.attributeExceptionInfo('login')
                    continue
                else:
                    if error is None:
                        print('No errors found. Status: %d. Logged in!' %status)
                        break
                    else:
                        print('\nError:\n\tYour email and password is not correct.')
                        input('\tCheck it on data.json file and press ENTER to retry:')
                        self.storage.updateStorage()
                        continue
            else:
                print('Something went wrong. Status code: %d. Retrying after 60 sec..' %status)
                time.sleep(60)
                continue

    def sniffProfile(self):
        user = self.storage.data['user']
        root_url = 'https://rocket-league.com'

        print("\n" + "-"*30 + "\nLet's sniff some profile data!\n" + "-"*30)

        while(True):
            print('Opening home page and reading some data..')
            cookie = {'acceptedPrivacyPolicy': '2.0'}
            try:
                result = self.session.get(root_url, cookies=cookie)
            except requests.exceptions.RequestException:
                self.requestExceptionInfo('sniffProfile')
                continue
            soup = BeautifulSoup(result.content, 'html.parser')
            
            #sniffing user data
            try:
                user_menu = soup.find('div', attrs={'class':'rlg-header-main-welcome-user'})
                username = user_menu.find('span').string
                trades_url = root_url + '/trades/' + username
            except AttributeError:
                self.attributeExceptionInfo('sniffProfile')
                print('Trying to log in again..')
                self.login()
                continue


            print('\nCurrent user: ' + username.upper() + '\nUser trades url: ' + trades_url)
            return {"username": username, "trades_url": trades_url}

    def sniffTrades(self):
        while(True):
            trades_dict = {}
            profile = self.storage.data['profile']
            existed_trades = self.storage.data['trades']

            print("\n" + "-"*30 + "\nUpdating trades data!\n" + "-"*30)
            cookie = {'acceptedPrivacyPolicy': '2.0'}
            try:
                result = self.session.get(profile['trades_url'], cookies=cookie)
            except requests.exceptions.RequestException:
                self.requestExceptionInfo('sniffTrades')
                continue
            
            soup = BeautifulSoup(result.content, 'html.parser')
            #counting trades
            try:
                n = soup.find('div', attrs={'class':'col-3-5'}).find('span').string
            except AttributeError:
                self.attributeExceptionInfo('sniffTrades')
                continue
            n = int(n[1:-1])
            if not n:
                print(
                    "There is no trades in %s's profile." %profile['username'],
                    "\nYou need to add one before bumping."
                    )
                input("Press ENTER when you are ready to check again..")
                continue
            
            print("%s's active trades: %s" %(profile['username'].upper(),n))
            print('\nReading trades info..')

            trades = soup.find_all('div', attrs={'class': 'rlg-trade-display-container'})
            if not trades:
                print('Somethig went wrong.. Retrying reading..')
                continue

            root_url = 'https://rocket-league.com'
            for trade in trades:
                try:
                    trade_id = trade.find('a').get('href')[7:]
                    posted = trade.find('span', attrs={'class': 'rlg-trade-display-added'})
                except AttributeError:
                    self.attributeExceptionInfo('sniffTrades')
                    continue
                posted = posted.string.split()[1:-3]
                posted[0] = int(posted[0])
                #removing 's' ending
                if posted[1][-1] == 's':
                    posted[1] = posted[1][:-1]
                
                bump = True
                if trade_id in existed_trades:
                    bump = existed_trades[trade_id]['bump']

                
                trades_dict[trade_id] = {
                    'posted' : posted,
                    'bump': bump
                }

            return trades_dict

    def iseditable(self, trade):
        n = trade['posted'][0]
        label = trade['posted'][1]
        
        if label == 'second' or (label == 'minute' and n < 16):
            return False
        else:
            return True

    def sniffTrade(self, trade_id):
        form_data = dict(
            csrf_token=self.find_csrf(),
            paint=0, certification=0, amount=1,
            amount_key=1, search='', note='', platform=1,
            alias=trade_id, btnSubmit='Save changes',
            ownerItems=[],
            tradeItems=[]
        )

        url = 'https://rocket-league.com/trade/edit?trade=' + trade_id
        while(True):
            try:
                print('\nTrying to get [%s] edit trade page..' %trade_id)
                result = self.session.get(url)
                
                if result.status_code >= 300:
                    print('\nError:\n\tStatus code: %d.' %result.status_code)
                    self.randsleep(10,21)
                    continue

                soup = BeautifulSoup(result.content, 'html.parser')
                
                error = soup.find('p', attrs={'class': 'rlg-site-popup__text'}).string
                if error is None:
                    print('No errors found. Status: %d.' %result.status_code)
                elif 'This trade is on a 15 minute edit cooldown' in error:
                    print('\nError:\n\tThis trade is already edited.')
                    return
            
                print('All good! Currently on trade [%s].' %trade_id)

                note = soup.find('textarea', attrs={'class':'rlg-input'}).string
                if note is not None:
                    form_data['note'] = note

                your_items = soup.find(id='rlg-youritems') \
                    .find_all('div', attrs={'class': 'rlg-trade-display-item'})
                their_items = soup.find(id='rlg-theiritems') \
                    .find_all('div', attrs={'class': 'rlg-trade-display-item'})
            except requests.exceptions.RequestException:
                self.requestExceptionInfo('sniffTrade')
                continue
            except:
                print('Error while reading trade data.')
                self.randsleep(10,21)
                continue
            
            for item in your_items:
                d = dict(
                        itemId='',
                        paint='',
                        cert='',
                        quantity=''
                )

                item_id = item.get('data-item')
                if not item_id:
                    break
                d['itemId'] = item_id

                quantity = item.get('data-quantity')
                if quantity == '1':
                    d.pop('quantity', None)
                else:
                    d['quantity'] = quantity

                paint = item.get('data-paint')
                if not paint:
                    paint = 0
                d['paint'] = paint

                cert = item.get('data-cert')
                if not cert:
                    cert = 0
                d['cert'] = cert

                form_data['ownerItems'].append(d)

            for item in their_items:
                d = dict(
                        itemId='',
                        paint='',
                        cert='',
                        quantity=''
                )

                item_id = item.get('data-item')
                if not item_id:
                    break
                d['itemId'] = item_id

                quantity = item.get('data-quantity')
                if quantity == '1':
                    d.pop('quantity', None)
                else:
                    d['quantity'] = quantity

                paint = item.get('data-paint')
                if not paint:
                    paint = 0
                d['paint'] = paint

                cert = item.get('data-cert')
                if not cert:
                    cert = 0
                d['cert'] = cert

                form_data['tradeItems'].append(d)

            return form_data

    def bumpAll(self):
        trades = self.storage.data['trades']
        for key in reversed(list(trades.keys())):
            trade = trades[key]

            all_once_mode = self.allowed_modes[0] in sys.argv
            inverse_mode = self.allowed_modes[1] in sys.argv

            if not self.iseditable(trade):
                if all_once_mode:
                    print('\nAll in once mode finished bumping.')
                    return 0
                else:
                    print('\nFinished bumping whole list. Refreshing time values..')
                    #refreshing trades data
                    self.storage.data["trades"] = self.sniffTrades()
                    self.storage.uploadData()
                    trade = self.storage.data['trades'][key]

                posted = trade['posted']
                sleep_time = 16 * 60 + randint(10,21) #16 min+
                
                if self.iseditable(trade):
                    print('\nThere is still editable trade(s).')
                    return 1
                elif posted[1] == 'minute':
                    sleep_time -= int(posted[0]) * 60
                else:
                    sleep_time = 60
                
                exp_time = datetime.now() + timedelta(seconds=sleep_time)
                print(
                    'No trades to edit. Refreshing after {:.1f} min sleep.'.format(sleep_time/60),
                    '\nExpected refresh time: {}'.format(exp_time.time().strftime('%H:%M:%S'))
                    )
                time.sleep(sleep_time)
                return 0
            
            bumpable = trade['bump']
            if inverse_mode:
                bumpable = not trade['bump']
            if not bumpable and not all_once_mode:
                print('\nTrade [%s] bump param is set to False. Skipping..' %key)
                continue
            
            url = "https://rocket-league.com/functions/editTrade.php"
            ref_url = 'https://rocket-league.com/trade/edit?trade='
            cookie = {'acceptedPrivacyPolicy': '2.0'}

            try:
                form_data = self.sniffTrade(key)
                if not form_data:
                    print('\nLooks like trades list changed. Refreshing trades and retrying.')
                    return -1
                urle = urllib.parse.urlencode(form_data)
                index = urle.find('ownerItems')
                urle = urle[:index] + urle[index:].replace('+','').replace('%27','%22')

                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9,uk;q=0.8,ru;q=0.7',
                    'content-length': str(len(urle)),
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://rocket-league.com',
                    'referer': ref_url+key + '&source=mytrades',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                }

                result = self.session.post(
                    url,
                    data=urle,
                    headers = headers,
                    cookies=cookie
                )

            except requests.exceptions.RequestException as e:
                print(e)
                self.requestExceptionInfo('bumpAll')
                self.randsleep(10,21,'then refreshing trades and retrying')
                return -1
            else:
                if result.status_code == 200:
                    print(
                        '\nSuccesfully bumped trade [%s].' %key,
                        'Status: %d' %result.status_code
                    )
                    if all_once_mode:
                        self.randsleep(10,21,'')
                    else:
                        self.randsleep(50, 71,'')
                else:
                    print('\nSomething went wrong while bumping trade [%s].' %key)
                    self.randsleep(10,21,'then refreshing trades and retrying')
                    return -1
        else:
            print('\nFinished bumping whole list. Refreshing..')


    def start(self):
        if len(sys.argv) > 1 and sys.argv[1] not in self.allowed_modes:
            print('\nError:\n\tUnknown mode in argv.')
            return
        elif len(sys.argv) > 2:
            print('\nError:\n\tOnly one mode allowed at the same time.')
            return

        first_start = True
    
        try:
            self.login()
            self.storage.data["profile"] = self.sniffProfile()
            status = None
            while(True):
                if status != 1:
                    self.storage.data["trades"] = self.sniffTrades()
                    self.storage.uploadData()
                if first_start and not self.allowed_modes[0] in sys.argv:
                    input("\nTrades updated. Press ENTER to start bumping..")
                    self.storage.updateStorage()
                    first_start = False
                status = self.bumpAll()
                if self.allowed_modes[0] in sys.argv and status == 0:
                    return
        
        except KeyboardInterrupt:
            print('\nKeyboardInterrupt raised - forcing exit..')
            self.session.close()
            print('\nClosing after:')
            for n in reversed(range(1,4)):
                print('\t%d' %n)
                time.sleep(1)



def main():
    bumper = Bumper()
    bumper.start()

if __name__ == '__main__':
    main()