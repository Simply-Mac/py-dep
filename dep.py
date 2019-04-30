#######################################################################################################################
#
# Device Enrollment Program (DEP) API Library Python 3.6+ Module
#
# Overview
# The purpose of this Python module is to provide a standard Python module to interact with the DEP/ACC API.
# Each method in this function interacts seamlessly with the API and either returns data from the method call or a
# status message indicating the result of the API call. For in-depth understanding of the DEP API spec, refer to
# https://applecareconnect.apple.com/api-docs/depuat/html/WSReference.html
#
# Dependencies
# - Python 3.x
# - 'requests' module
#
# Credits
# Big thanks to the folks that wrote the Meraki 'dashboard-api-python' module. This module borrowed a lot of from them.
#######################################################################################################################

import json
from os import environ

from requests import Session


class Device(object):
    def __init__(self, device_id, asset_tag=None):
        """
        Apple device to be enrolled in the customer's DEP account.
        :param device_id: The Serial Number/IMEI or MEID number of the device. The value for this field should be
                          entered in Upper case. Type: String, Max Length: 20, Required: Yes
        :param asset_tag: Additional info about the device. Type: String, Max Length: 128, Required: No
        """
        self.deviceId = device_id
        self.assetTag = asset_tag

    def json(self):
        """
        :return: Object in json format
        """
        return dict(deviceId=self.deviceId, assetTag=self.assetTag)


class Delivery(object):
    def __init__(self, delivery_number, ship_date, devices=None):
        """
        Deliveries contain shipment information and an array of devices that were on the physical delivery.
        :param delivery_number: The delivery no. corresponding to the delivery.
                                Type: String, Max Length: 32, Required: Yes
        :param ship_date: The timestamp of shipment of the delivery. This should include the date and time and
                          should be in a standard UTC format. Type: String, Max Length: 64, Required: Yes
        :param devices: List of Device objects in the Delivery to be enrolled. Please note that in the case
                        of the VD (void) order type, device information is not required.
                        Type: Array of Devices, Max Length: N/A, Required: Yes
        """
        self.deliveryNumber = delivery_number
        self.shipDate = ship_date
        self.devices = devices

    def json(self):
        """
        :return: Object in json format
        """
        return dict(
            deliveryNumber=self.deliveryNumber, shipdate=self.shipDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
            devices=self.devices
        )


class Order(object):
    def __init__(self, order_number, order_date, order_type, customer_dep_id, po_number=None, deliveries=None):
        """
        Customers will use this data for reference in their DEP account when provisioning orders and
        devices to MDM servers.
        :param order_number: Order number pertaining to the order. Type: String, Max Length: 32, Required: Yes
        :param order_date: The timestamp when the order was created. This should include the date and time and should
                            be in a standard UTC format. Type: String, Max Length: 64, Required: Yes
        :param order_type: Order type could be OR - Normal, RE - Return, VD - Void, OV - Override
                           Type: String, Max Length: 2, Required: Yes
        :param customer_dep_id: The DEP Org ID for the customer. Type: String, Max Length: 32, Required: Yes
        :param po_number: The PO Number corresponding to the order. Type: String, Max Length: 100, Required: No
        :param deliveries: The list of Delivery objects in the order. Please note that in the case of the VD void order type,
                            delivery information is not required.
        """
        self.orderNumber = order_number
        self.orderDate = order_date
        self.orderType = order_type
        self.customerId = customer_dep_id
        self.poNumber = po_number
        self.deliveries = deliveries

    def json(self):
        """
        :return: Object in json format
        """
        return dict(
            orderNumber=self.orderNumber, orderDate=self.orderDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
            orderType=self.orderType, customerId=self.customerId, poNumber=self.poNumber, deliveries=self.deliveries
        )


def dep_credentials():
    """
    :usage: Defines the Session and the Device Enrollment Program Settings for the API calls
    :return: Requests Session w/ headers and DEP cert, DEP SoldTo, DEP ResellerID, and endpoint base URL
    """
    # Begin a Requests Session for all API Calls
    session = Session()
    session.headers.update({
        'Content-Type': "application/json;charset=utf-8",  # Required
        'Accept-Encoding': "application/json"  # Optional
    })

    # Get ACC Connection Details from Environment Variables
    dep_env = environ['DEP_ENV']  # DEP Environment: UAT or PROD
    dep_ship_to = environ['DEP_SHIPTO']  # 10 digit Ship-To Account Number
    dep_reseller_id = environ['DEP_RESELLER_ID']  # DEP Reseller ID

    # Set the base_url of the AppleCare Connect endpoint and SSL cert
    # Default to Dev/Test environment
    base_url = "https://acc-ipt.apple.com/enroll-service/1.0"
    session.cert = (environ['DEP_UAT_CERT'],  # Path to DEP UAT Cert .PEM File
                    environ['DEP_UAT_PRIVATE_KEY'])  # Path to DEP UAT Private Key .PEM File

    if dep_env == 'UAT':
        # Joint UAT environment
        session.cert = (environ['DEP_UAT_CERT'],  # Path to DEP UAT Cert .PEM File
                        environ['DEP_UAT_PRIVATE_KEY'])  # Path to DEP UAT Private Key .PEM File
        if (int(dep_ship_to) % 2) == 0:
            base_url = "https://api-applecareconnect-ept.apple.com/enroll-service/1.0"
        else:
            base_url = "https://api-applecareconnect-ept2.apple.com/enroll-service/1.0"

    elif dep_env == 'PROD':
        # Production environment
        session.cert = (environ['DEP_PROD_CERT'],  # Path to DEP PROD Cert .PEM File
                        environ['DEP_PROD_PRIVATE_KEY'])  # Path to DEP PROD Private Key .PEM File
        if (int(dep_ship_to) % 2) == 0:
            base_url = "https://api-applecareconnect.apple.com/enroll-service/1.0"
        else:
            base_url = "https://api-applecareconnect2.apple.com/enroll-service/1.0"

    # Context Information for the request. Contains the Ship-To, language code and timezone.
    request_context = dict(
        shipTo=dep_ship_to,  # Ship-To Account Number
        timeZone="420",  # Default value is Pacific Time. Users can provide a timezone, offset or canonical ID values.
        langCode="en"  # Default value is "en". Users can provide any of the Valid Language Codes.
    )

    return session, dep_ship_to, dep_reseller_id, base_url, request_context


def is_json(json_array):
    """
    :param json_array: String variable to be validated if it is JSON
    :return: True if json_array is valid, False if not
    """
    try:
        json_object = json.loads(json_array)
    except ValueError:
        return False
    return True


def response_handler(response_data, suppress_print):
    """
    :param response_data: JSON response from the DEP API
    :param suppress_print: Prints output when function is called
    :return: Full API response and any API errors and their messages
    """
    valid_return = is_json(response_data)

    if valid_return:
        json_response = json.loads(response_data)
        error_code = []
        error_message = []

        # Bulk Enroll Devices Error(s)
        if "enrollDeviceErrorResponse" in json_response:
            api_errors = json_response["enrollDeviceErrorResponse"]
            for error in api_errors:
                error_code.append(error['errorCode'])
                error_message.append(error['errorMessage'])
                if suppress_print is False:
                    print(f"{error['errorCode']} - {error['errorMessage']}")
        # Check Transaction Error(s)
        elif "checkTransactionErrorResponse" in json_response:
            api_errors = json_response["checkTransactionErrorResponse"]
            # for error in api_errors:
            error_code.append(api_errors['errorCode'])
            error_message.append(api_errors['errorMessage'])
            if suppress_print is False:
                print(f"{api_errors['errorCode']} - {api_errors['errorMessage']}")
        # Check Transaction - Order Error(s)
        elif "devicePostStatusMessage" in json_response:
            api_errors = json_response["orders"][0]["deliveries"][0]["devices"]
            for error in api_errors:
                error_code.append(error[0]['devicePostStatus'])
                error_message.append(error[0]['devicePostStatusMessage'])
                if suppress_print is False:
                    print(f"{error['errorCode']} - {error['errorMessage']}")
        # Show Order Error(s)
        elif "showOrderErrorResponse" in json_response:
            api_errors = json_response["showOrderErrorResponse"]
            for error in api_errors:
                error_code.append(error[0]['errorCode'])
                error_message.append(error[0]['errorMessage'])
                if suppress_print is False:
                    print(f"{error['errorCode']} - {error['errorMessage']}")
        # Show Order - Order Error(s)
        elif "showOrderStatusCode" in json_response:
            api_errors = json_response["orders"]
            for error in api_errors:
                error_code.append(error[0]['showOrderStatusCode'])
                error_message.append(f"{error[0]['orderNumber']}, {error[0]['showOrderStatusMessage']}")
                if suppress_print is False:
                    print(f"{error['errorCode']} - {error[0]['orderNumber']}, {error[0]['showOrderStatusMessage']}")
        # ShipTo Error
        elif "errorCode" in json_response:
            error_code.append(json_response['errorCode'])
            error_message.append(json_response['errorMessage'])
            if suppress_print is False:
                print(f'{error_code} - {error_message}')
        # No Errors
        else:
            if suppress_print is False:
                print('REST Operation Successful - See full response for details')
    else:
        error_code = "DEP_ERR_0001"
        error_message = "JSON is invalid - Inspect full response for errors"
        if suppress_print is False:
            print('JSON is invalid - Inspect full response for errors')

    return json.loads(response_data), error_code, error_message


def bulk_enroll_devices(transaction_id, orders, suppress_print=False):
    """
    :usage: Allows resellers to post the device details to ACC for getting the devices enrolled in the
            Device Enrollment Program (DEP). Upon successful receipt of the transaction, the request is validated
            (for JSON validity and mandatory fields check). Once validation is successful,
            a unique deviceEnrollmentTransactionId is generated and returned to the reseller. Validation failure or
            any other issues are reported through an appropriate error message.
    :param transaction_id: Unique transaction ID provided by the reseller. For instance, "TXN_000001"
    :param orders: List of Order objects with at least one Delivery that also has at least one Device.
                   (limit 1000 per transaction)
    :param suppress_print: Suppress any print output from function (Default: False)
    :return: JSON formatted strings of the complete API request, response, and any error codes
    """
    # Establish request variables
    session, dep_ship_to, dep_reseller_id, base_url, context = dep_credentials()

    post_url = f'{base_url}/bulk-enroll-devices'
    call_type = 'bulk-enroll-devices'

    # Prepare data in array
    post_data = dict(
        requestContext=context, transactionId=transaction_id, depResellerID=dep_reseller_id, orders=orders
    )

    # Send data to API
    response = session.post(post_url, data=json.dumps(post_data))

    # Call return handler function to parse request response
    response_data, error_code, error_message = response_handler(response.text, suppress_print)

    return post_data, response_data, error_code, error_message, call_type


def check_transaction_status(transaction_id, suppress_print=False):
    """
    :usage: Allows resellers to check the status of an enrollment transaction posted to DEP/ACC. Because this API
            transaction is asynchronous, the Check Transaction Status API should be used after posting a
            Bulk Enroll Devices API call.
    :param transaction_id: Unique Transaction ID provided by DEP API during Bulk Enroll
    :param suppress_print: Suppress any print output from function (Default: False)
    :return: JSON formatted strings of the complete API request, response, and any error codes
    """
    # Establish request variables
    session, dep_ship_to, dep_reseller_id, base_url, context = dep_credentials()

    post_url = f'{base_url}/check-transaction-status'
    call_type = 'check-transaction-status'

    # Prepare data in array
    post_data = dict(
        requestContext=context,
        depResellerId=dep_reseller_id,
        deviceEnrollmentTransactionId=transaction_id
    )

    # Send data to API
    response = session.post(post_url, data=json.dumps(post_data))

    # Call return handler function to parse request response
    response_data, error_code, error_message = response_handler(response.text, suppress_print)

    return post_data, response_data, error_code, error_message, call_type


def show_order_details(order_numbers, suppress_print=False):
    """
    :usage: Allows resellers to check the enrollment status of existing orders. The reseller should query ACC with
            valid order numbers corresponding to orders they have previously submitted. ACC will then return the latest
            state of enrollment details of the order. If the order number is invalid, or if the order is
            pending enrollment, a suitable error code and message will be sent to the reseller.
    :param order_numbers: List of order numbers whose details are requested. Must be of type: <class 'list'>.
    :param suppress_print: Suppress any print output from function (Default: False)
    :return: JSON formatted strings of the complete API request, response, and any error codes
    """
    # Establish request variables
    session, dep_ship_to, dep_reseller_id, base_url, context = dep_credentials()

    post_url = f'{base_url}/show-order-details'
    call_type = 'show-order-details'

    # Prepare data in array
    post_data = dict(
        requestContext=context,
        depResellerId=dep_reseller_id,
        orderNumbers=order_numbers
    )

    # Send data to API
    response = session.post(post_url, data=json.dumps(post_data))

    # Call return handler function to parse request response
    response_data, error_code, error_message = response_handler(response.text, suppress_print)

    return post_data, response_data, error_code, error_message, call_type
