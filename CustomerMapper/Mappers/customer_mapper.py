import xml.etree.ElementTree as ET
from xml.dom import minidom

class CustomerMapper:
    def json_to_xml(self, customers_data):
        """
        Converts a list of customer data (Python dictionaries) to an XML string.
        """
        root_element = ET.Element("Customers")

        for customer_dict in customers_data:
            customer_element = ET.SubElement(root_element, "Customer")

            # Set CustomerID attribute
            if customer_dict.get("Customer Id"):
                customer_element.set("CustomerID", str(customer_dict.get("Customer Id")))

            # CompanyName
            company_name = ET.SubElement(customer_element, "CompanyName")
            company_name.text = customer_dict.get("Company", "N/A")

            # ContactName
            contact_name_parts = [customer_dict.get("First Name", ""), customer_dict.get("Last Name", "")]
            contact_name_str = " ".join(filter(None, contact_name_parts)).strip()
            contact_name = ET.SubElement(customer_element, "ContactName")
            contact_name.text = contact_name_str if contact_name_str else "N/A"

            # ContactTitle
            contact_title = ET.SubElement(customer_element, "ContactTitle")
            contact_title.text = "N/A"  # Placeholder

            # Phone
            phone = ET.SubElement(customer_element, "Phone")
            phone.text = customer_dict.get("Phone 1", "N/A")

            # Fax (optional)
            if customer_dict.get("Phone 2"):
                fax = ET.SubElement(customer_element, "Fax")
                fax.text = customer_dict.get("Phone 2")

            # FullAddress
            full_address_element = ET.SubElement(customer_element, "FullAddress")

            address = ET.SubElement(full_address_element, "Address")
            address.text = "N/A"  # Placeholder

            city = ET.SubElement(full_address_element, "City")
            city.text = customer_dict.get("City", "N/A")

            region = ET.SubElement(full_address_element, "Region")
            region.text = "N/A"  # Placeholder

            postal_code_val = 0 # Placeholder as per plan
            postal_code = ET.SubElement(full_address_element, "PostalCode")
            postal_code.text = str(postal_code_val)

            country = ET.SubElement(full_address_element, "Country")
            country.text = customer_dict.get("Country", "N/A")

        # Pretty print XML
        xml_str = ET.tostring(root_element, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")

if __name__ == '__main__':
    # Example Usage (for basic testing)
    mapper = CustomerMapper()
    sample_data = [
        {
            "Index": 1,
            "Customer Id": "ALFKI",
            "First Name": "Maria",
            "Last Name": "Anders",
            "Company": "Alfreds Futterkiste",
            "City": "Berlin",
            "Country": "Germany",
            "Phone 1": "030-0074321",
            "Phone 2": "030-0076545",
            "Email": "maria.anders@example.com",
            "Subscription Date": "2020-01-01",
            "Website": "http://example.com"
        },
        {
            "Index": 2,
            "Customer Id": "ANATR",
            "First Name": "Ana",
            "Last Name": "Trujillo",
            "Company": "Ana Trujillo Emparedados y helados",
            "City": "México D.F.",
            "Country": "Mexico",
            "Phone 1": "(5) 555-4729",
            "Phone 2": None, # Missing Phone 2 for Fax test
            "Email": "ana.trujillo@example.com",
            "Subscription Date": "2021-03-15",
            "Website": "http://example.mx"
        }
    ]
    xml_output = mapper.json_to_xml(sample_data)
    print(xml_output)

    empty_xml_output = mapper.json_to_xml([])
    print(empty_xml_output)

    # Example with special characters
    special_char_data = [
        {
            "Customer Id": "SPCL1",
            "First Name": "O'Malley",
            "Last Name": "\"The Great\"",
            "Company": "Widgets & Gadgets <Inc.>",
            "City": "Angle brackets city < >",
            "Country": "Ampersand & Country",
            "Phone 1": "123-456-7890",
        }
    ]
    xml_special_output = mapper.json_to_xml(special_char_data)
    print(xml_special_output)
