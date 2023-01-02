import json
import requests
import time


class MenuItemExtractor:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def OrderLineMaker(self, line_items: dict) -> dict:

        client_order_line_id = line_items["item_id"]
        quantity = line_items["quantity"]
        menu_dict = {"client_order_line_id": client_order_line_id, "client_menu_item_id": client_order_line_id,
                     "quantity": quantity, "subtract": False}
        if("child_item" in line_items.keys()):
            child_item_list = line_items["child_item"]
            order_item_list = []
            temp = {"order_lines": order_item_list}
            for item in child_item_list:
                order_item_list.append(self.OrderLineMaker(item))
            menu_dict.update(temp)
        return menu_dict


class QuBeyondOrderExtractor(MenuItemExtractor):
    def __init__(self, config: dict, **entries):
        super().__init__(**entries)
        self.__dict__.update(config)

    def Qu_Beyond_Auth_Config(self):
        url = self.__dict__["Auth_URL"]
        userName = self.__dict__["userName"]
        password = self.__dict__["password"]
        companyId = self.__dict__["companyId"]

        payload = json.dumps({
            "userName": f"{userName}",
            "password": f"{password}",
            "companyId": f"{companyId}"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            access_token = json.loads(response.text)["token"]
            return access_token
        except Exception as e:
             print("QuBeyond authentication failed with status code: " + str(response.status_code))  #reason of failer

    def get_transformed_orders(self, order_list: list) -> list:
        checks_to_be_sent = []
        for order in order_list:
            order_number = order["check_id"]
            posted_date_time = time.mktime(time.strptime(order["opened_at"], '%Y-%m-%dT%H:%M:%S'))
            last_modified_date_time = time.mktime(time.strptime(order["last_modified_at"], '%Y-%m-%dT%H:%M:%S'))
            data_to_send = {"order_number": order_number, "posted_date_time": posted_date_time,
                            "last_modified_date_time": last_modified_date_time}
            try:
                item_lists = order["item"]
            except KeyError:
                item_lists = []
            line_items = []
            temp = {"order_lines": line_items}
            for line_item in item_lists:
                line_items.append(self.OrderLineMaker(line_item))
            data_to_send.update(temp)
            print(data_to_send)
            checks_to_be_sent.append(data_to_send)
        return checks_to_be_sent

    def get_latest_orders(self, delta_from_date, delta_from_time, end_date="09092021") -> list:
        BaseUrl = self.__dict__["BaseUrl"]
        companyId = self.__dict__["companyId"]
        locationId = self.__dict__["locationId"]
        url = f"{BaseUrl}/{companyId}/{locationId}?data_type=checks&delta_from_date={delta_from_date}&delta_from_time={delta_from_time}&include_abandoned=true"
        access_token = self.Qu_Beyond_Auth_Config() if self.Qu_Beyond_Auth_Config() is not None else exit()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers)
        orders: list = json.loads(response.text)["data"]["check"]
        if len(orders) == 0:
            return orders

        orders = self.get_transformed_orders(orders)
        return orders

    def get_default_orders(self, start_date="09052021", end_date="09102021") -> list:
        BaseUrl = self.__dict__["BaseUrl"]
        companyId = self.__dict__["companyId"]
        locationId = self.__dict__["locationId"]
        url = f"{BaseUrl}/{companyId}/{locationId}?data_type=checks&start_date={start_date}&end_date={end_date}&include_abandoned=true"
        access_token = self.Qu_Beyond_Auth_Config() if self.Qu_Beyond_Auth_Config() is not None else exit()
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers)
        orders = json.loads(response.text)["data"]["check"]
        if len(orders) == 0:
            return orders

        orders = self.get_transformed_orders(orders)
        return orders
