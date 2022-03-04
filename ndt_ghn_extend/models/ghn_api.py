# -*- coding: utf-8 -*-
import requests
from odoo.exceptions import UserError
shop_id_87 = 1295159
token_87 = '81f253e7-e8da-11ea-84a7-3e05d9a3136e'
token_090 = '7e079abb-fe1d-11ea-aeaa-9a0707cfe569'
shop_id_090 = 1318075 
token = token_090#token_87
shop_id = shop_id_090#shop_id_87

token = token_87
shop_id = shop_id_87
otp = '783122'
ghn_config = {'token': token, 'shop_id':shop_id_87}

# def fetch_2_ghn(url, token, shop_id=None, data=None):
#     if not token:
#         raise UserError('Bạn phải nhập token ở setting')
#     headers = {'token': token }
#     if shop_id:
#         headers.update({'shop_id':str(shop_id)})
#     response = requests.post(url, 
#                              headers=headers, json = data)
#     json_response = response.json()
#     return json_response

def request_ghn(url, token, shop_id, data):
    if not token:
        raise UserError('Bạn phải nhập token ở setting')
    headers = {'token': token }
    if shop_id:
        headers.update({'shop_id':str(shop_id)})
    response = requests.post(url, 
                             headers=headers, json = data)
    json_response = response.json()
    code  = json_response['code']
    if code == 200:
        return json_response['data']
    else:
        raise UserError(json_response['message'])

def fetch_ghn_fee(token, shop_id, to_district_id, to_ward_code,service_type_id,service_id, from_district_id , 
    height=0, length=0, width=0, weight=0):
        url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee'
        if shop_id == False:
            raise UserError('Phải cấu hình GHN shop id trong kho hàng')
        if not weight:
            weight = 1
        data = {    
                    "service_type_id":service_type_id,
                    "to_district_id":to_district_id,
                    "to_ward_code":to_ward_code,# char
                    "height":height,
                    "length":length,
                    "width":width,
                    "weight":weight,
                    "coupon": None}
        rs = request_ghn(url, token, shop_id, data)
        return rs

def fetch_ghn_order(token, shop_id, to_district_id, to_ward_code, to_address,service_id,service_type_id,
    delivery_payment_type_id, delivery_cod_amount,note,to_name,to_phone,
    items,height=0, length=0, width=0, weight=0):
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create'
    data ={
    "payment_type_id": delivery_payment_type_id,#selection, nếu thu hộ tiền thì onchage cái này lên 2 ( buyer)
    "note": note,
    "required_note": "KHONGCHOXEMHANG",
    "return_phone": "",
    "return_address": "",
    "return_district_id": None,
    "return_ward_code": "",
    "client_order_code": "",# SO name
    "to_name": to_name,#need change
    "to_phone": to_phone,#need change
    "to_address": to_address,
    "to_ward_code": to_ward_code,
    "to_district_id": to_district_id,
    "cod_amount": delivery_cod_amount,#phải thu hộ tiền, hay đã chuyển khoản
    "content": note,# Nội dung đơn hàng
    "weight": weight,
    "length": length,
    "width": width,
    "height": height,
    "pick_station_id": 0,
    "deliver_station_id": 0,
    "service_id": service_id,# có thể chỉ cần service_type_id là đủ
    "service_type_id":service_type_id,
    "items":items
}
    rt = request_ghn(url, token, shop_id, data)
    return rt

def get_ghn_order_info(token, ghn_order):
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/detail'
    data = {"order_code": ghn_order}
    rt = request_ghn(url,token,None, data)
    return rt

def cancel_ghn_shipment(token, ghn_order):
    # trả về: rt: data trả về
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/switch-status/cancel'
    data = {"order_codes": ghn_order }
    rt = request_ghn(url,token,None,data)
    return rt

def ghn_update_order(token, ghn_order, data):
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/update'
    data.update({"order_code": ghn_order})
    rt = request_ghn(url,token,None,data)
    return rt
   
def get_fee_of_order(token, ghn_order):
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/soc'
    data = {"order_code": ghn_order}
    rt = request_ghn(url,token,None,data)
    return rt

def get_service(token, shop_id, from_district, to_district):
    url = 'https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/available-services'
    shop_id = int(ghn_config['shop_id'])
    if not shop_id:
        raise UserError('Phải cấu hình GHN shop id trong kho hàng')
    if not to_district:
        raise UserError('Bạn chưa set địa điểm đích để lấy dịch vụ ghn')
    if not from_district:
        raise UserError('Bạn chưa set địa nguồn để lấy dịch vụ ghn')
    data = {
    "shop_id": shop_id,#bắt buộc
	"from_district": from_district,#bắt buộc
	"to_district": to_district##bắt buộc
    }
    rt = request_ghn(url, token, None, data)
    return rt


if __name__ == "__main__":
    # {'service_type_id': 2, 'to_district_id': 1484, 'to_ward_code': '1A0110', 'height': 10, 'length': 10, 'width': 10, 'weight': 1, 'coupon': None}
    from_district =  3135
    to_ward_code = '1A0110' 
    to_district_id = 1484
    service_type_id = 2
    service_id = False
    from_district_id  = 0
    rs = fetch_ghn_fee(token, shop_id, to_district_id, to_ward_code, service_type_id, service_id, from_district_id , 
    height=10, length=10, width=10, weight=1)
    print (rs)


   