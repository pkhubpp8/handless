class signBase:
    def __init__(self, site_name):
        self.access_result = False
        self.access_result_info = ""
        self.sign_result = False
        self.sign_result_info = ""
        self.need_resign = True
        self.new_message = ""
        self.result = None
        self.extra_info = {}
        self.site_name = site_name