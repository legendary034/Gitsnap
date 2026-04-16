import requests
from bs4 import BeautifulSoup

def main():
    print("Fetching 8upload.com...")
    res = requests.get('https://8upload.com/')
    soup = BeautifulSoup(res.text, 'html.parser')
    for form in soup.find_all('form'):
        print("Form Action:", form.get('action'))
        print("Form Enctype:", form.get('enctype'))
        for inp in form.find_all('input'):
            print("  Input:", inp.get('type'), inp.get('name'), inp.get('value'))

if __name__ == '__main__':
    main()
