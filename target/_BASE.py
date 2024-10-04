class signBase:
    def __init__(self, site_name):
        self.access_result = False
        self.access_result_info = ""
        self.sign_result = False
        self.sign_result_info = ""
        self.new_message = ""
        self.result = None
        self.extra_info = {}
        self.site_name = site_name
        self.driver = None
    def set_driver(self, driver):
        self.driver = driver
    def get_driver(self):
        return self.driver
    def exit(self):
        if self.driver:
            # 因为没有切换到新标签页，所以不需要close，直接打开下一个页面即可
            # self.driver.close()
            self.driver = None
