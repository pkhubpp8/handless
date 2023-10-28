import requests

def get_ipv4_icanhazip():
    try:
        response = requests.get('http://ipv4.icanhazip.com')
        if response.status_code == 200:
            ipv4 = response.text.strip()
            return ipv4
        else:
            print('Error: Unable to retrieve IPv4 address.')
    except Exception as e:
        print('Error:', e)


def get_ipv4_ipify():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            ipv4 = response.text.strip()
            return ipv4
        else:
            print('Error: Unable to retrieve IPv4 address.')
    except Exception as e:
        print('Error:', e)

def get_ipv4_wtfismyip():
    try:
        response = requests.get('https://ipv4.wtfismyip.com/text')
        if response.status_code == 200:
            ipv4 = response.text.strip()
            return ipv4
        else:
            print('Error: Unable to retrieve IPv4 address.')
    except Exception as e:
        print('Error:', e)

def get_ipv4_ipv4icanhazip():
    try:
        response = requests.get('http://ipv4.icanhazip.com')
        if response.status_code == 200:
            ipv4 = response.text.strip()
            return ipv4
        else:
            print('Error: Unable to retrieve IPv4 address.')
    except Exception as e:
        print('Error:', e)
        
def get_ipv4_ip4onlyme():
    try:
        response = requests.get('http://ip4only.me/api/')
        if response.status_code == 200:
            response_parts = response.text.strip().split(',')
            ipv4 = response_parts[1]
            return ipv4
        else:
            print('Error: Unable to retrieve IPv4 address.')
    except Exception as e:
        print('Error:', e)

