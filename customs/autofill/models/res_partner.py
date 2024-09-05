from odoo import api, models

import json
import requests
import xml.etree.ElementTree as ET


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = 'res.partner'

    @api.onchange("vat")
    def _onchange_vat(self):
        if len(self.vat or '') == 13:
            try:
                url = "https://rdws.rd.go.th/jsonRD/vatserviceRD3.asmx"
                soap_action = "https://rdws.rd.go.th/JserviceRD3/vatserviceRD3/Service"

                TIN = self.vat or '' # '0107542000011' '0107544000108'

                # Define the SOAP envelope
                soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <Service xmlns="https://rdws.rd.go.th/JserviceRD3/vatserviceRD3">
                      <username>anonymous</username>
                      <password>anonymous</password>
                      <TIN>{TIN}</TIN>
                      <Name></Name>
                      <ProvinceCode>0</ProvinceCode>
                      <BranchNumber>0</BranchNumber>
                      <AmphurCode>0</AmphurCode>
                    </Service>
                  </soap:Body>
                </soap:Envelope>"""

                # Set the headers
                headers = {
                    "Content-Type": "text/xml; charset=utf-8",
                    "SOAPAction": soap_action,
                }

                # Send the POST request
                response = requests.post(url, data=soap_envelope, headers=headers)

                # print(response.status_code)
                # print(response.text)

                # Optionally parse the response
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    namespace = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                                 'ns': 'https://rdws.rd.go.th/JserviceRD3/vatserviceRD3'}
                    service_result_element = root.find('.//ns:ServiceResult', namespaces=namespace)
                    if service_result_element is not None:
                        # Get the text content of the ServiceResult
                        service_result_text = service_result_element.text

                        # Parse the JSON content
                        try:
                            data = json.loads(service_result_text)
                            print(data.get('TitleName')[0])
                            # Print or process the data
                            print("Parsed Data:")
                            print(json.dumps(data, indent=4, ensure_ascii=False))

                            self.name = f'{data["TitleName"][0].strip()} {data["Name"][0].strip()}'
                            self.street = f'อาคาร {data["BuildingName"][0].strip()}'
                            self.street += f' ชั้น {data["FloorNumber"][0].strip()}'
                            self.street += f' หมู่บ้าน  {data["VillageName"][0].strip()}'
                            self.street += f' ห้องเลขที่  {data["RoomNumber"][0].strip()}'
                            self.street += f' บ้านเลขที่  {data["HouseNumber"][0].strip()}'
                            self.street += f' หมู่  {data["MooNumber"][0].strip()}'
                            self.street2 = f'ซอย {data["SoiName"][0].strip()} '
                            self.street2 += f' ถนน {data["StreetName"][0].strip()} '
                            self.street2 += f' ตำบล {data["Thambol"][0].strip()} '
                            self.street2 += f' อำเภอ {data["Amphur"][0].strip()}'
                            self.city = f'{data["Province"][0].strip()}'
                            self.zip = f'{data["PostCode"][0].strip()}'
                            self.country_id = 217

                        except json.JSONDecodeError as e:
                            print("Error decoding JSON:", e)
                    else:
                        print("ServiceResult element not found")
                    # for elem in root.iter():
                    #     print(elem.tag, elem.text)
                else:
                    print("Error:", response.status_code)
                    print(response.text)
            except e:
                print("Error:", e)

