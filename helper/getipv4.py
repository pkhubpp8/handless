import requests


class getIpv4():
    def __init__(self, logger):
        self.logger = logger
    def get_ipv4_icanhazip(self):
        try:
            response = requests.get('http://ipv4.icanhazip.com')
            if response.status_code == 200:
                ipv4 = response.text.strip()
                return ipv4
            else:
                self.logger.warning(f'get_ipv4_icanhazip: Unable to retrieve IPv4 address. status_code = {response.status_code}')
        except Exception as e:
            self.logger.debug('Error:', e)

    def get_ipv4_ipify(self):
        try:
            response = requests.get('https://api.ipify.org')
            if response.status_code == 200:
                ipv4 = response.text.strip()
                return ipv4
            else:
                self.logger.warning(f'get_ipv4_ipify: Unable to retrieve IPv4 address. status_code = {response.status_code}')
        except Exception as e:
            self.logger.debug('Error:', e)

    def get_ipv4_wtfismyip(self):
        try:
            response = requests.get('https://ipv4.wtfismyip.com/text')
            if response.status_code == 200:
                ipv4 = response.text.strip()
                return ipv4
            else:
                self.logger.warning(f'get_ipv4_wtfismyip: Unable to retrieve IPv4 address. status_code = {response.status_code}')
        except Exception as e:
            self.logger.debug('Error:', e)

    def get_ipv4_ipv4icanhazip(self):
        try:
            response = requests.get('http://ipv4.icanhazip.com')
            if response.status_code == 200:
                ipv4 = response.text.strip()
                return ipv4
            else:
                self.logger.warning(f'get_ipv4_ipv4icanhazip: Unable to retrieve IPv4 address. status_code = {response.status_code}')
        except Exception as e:
            self.logger.debug('Error:', e)

    def get_ipv4_ip4onlyme(self):
        try:
            response = requests.get('http://ip4only.me/api/')
            if response.status_code == 200:
                response_parts = response.text.strip().split(',')
                ipv4 = response_parts[1]
                return ipv4
            else:
                self.logger.warning(f'get_ipv4_ip4onlyme: Unable to retrieve IPv4 address. status_code = {response.status_code}')
        except Exception as e:
            self.logger.debug('Error:', e)
