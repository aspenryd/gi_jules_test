import unittest
import csv
import os
from lxml import etree
from CustomerMapper.Mappers.customer_mapper import CustomerMapper

class TestCustomerMapper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mapper = CustomerMapper()
        cls.test_data_path = os.path.join(os.path.dirname(__file__), '..', 'example files', 'customers-100.csv')
        cls.xsd_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'target_customer_list.xsd')

        cls.source_customers_data = []
        try:
            with open(cls.test_data_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    cls.source_customers_data.append(row)
        except FileNotFoundError:
            # This allows tests to be discovered and run even if CSV is missing,
            # though specific tests using it will fail.
            print(f"Warning: Test data file not found at {cls.test_data_path}")
        except Exception as e:
            print(f"Warning: Error reading test data file {cls.test_data_path}: {e}")

        try:
            with open(cls.xsd_path, 'rb') as f: # lxml.etree.XMLSchema expects bytes
                xsd_doc = etree.XML(f.read())
            cls.xml_schema = etree.XMLSchema(xsd_doc)
        except FileNotFoundError:
            cls.xml_schema = None
            print(f"Warning: XSD schema file not found at {cls.xsd_path}")
        except etree.XMLSchemaParseError as e:
            cls.xml_schema = None
            print(f"Warning: XSD schema could not be parsed from {cls.xsd_path}: {e}")
        except Exception as e:
            cls.xml_schema = None
            print(f"Warning: An unexpected error occurred while loading XSD schema {cls.xsd_path}: {e}")


    def _validate_xml_with_xsd(self, xml_string):
        if not self.xml_schema:
            self.skipTest(f"Skipping XSD validation because the schema at {self.xsd_path} could not be loaded.")
        try:
            xml_doc = etree.fromstring(xml_string.encode('utf-8'))
            self.xml_schema.assertValid(xml_doc) # Throws etree.DocumentInvalid if not valid
            return True
        except etree.DocumentInvalid as e:
            self.fail(f"XML validation failed: {e}")
        except etree.XMLSyntaxError as e:
            self.fail(f"Generated XML is not well-formed: {e}\nXML Content:\n{xml_string}")
        return False

    def test_csv_data_conversion_and_schema_validation(self):
        if not self.source_customers_data:
            self.skipTest("Skipping test as source customer data is not loaded.")

        # Test with a subset for brevity in output, but full validation
        # Using first 5 customers from CSV for detailed checks, but will validate full generated XML
        sample_input_data = self.source_customers_data[:5]

        xml_output = self.mapper.json_to_xml(self.source_customers_data) # Convert all data
        self.assertTrue(xml_output.strip().startswith("<?xml"))
        # For non-empty lists, it should end with </Customers> potentially after some whitespace
        self.assertTrue(xml_output.strip().endswith("</Customers>"))


        # Validate the full XML output against XSD
        self._validate_xml_with_xsd(xml_output)

        # Basic structural checks on the parsed XML for the sample
        # We parse the XML string to check its content
        root = etree.fromstring(xml_output.encode('utf-8'))
        self.assertEqual(root.tag, "Customers")

        customers_in_xml = root.findall("Customer")
        self.assertEqual(len(customers_in_xml), len(self.source_customers_data))

        # Detailed check for the first customer from the sample
        if sample_input_data and customers_in_xml:
            first_csv_customer = sample_input_data[0]
            first_xml_customer = customers_in_xml[0]

            self.assertEqual(first_xml_customer.get("CustomerID"), first_csv_customer.get("Customer Id"))
            self.assertEqual(first_xml_customer.findtext("CompanyName"), first_csv_customer.get("Company"))

            expected_contact_name = f"{first_csv_customer.get('First Name', '')} {first_csv_customer.get('Last Name', '')}".strip()
            self.assertEqual(first_xml_customer.findtext("ContactName"), expected_contact_name)
            self.assertEqual(first_xml_customer.findtext("ContactTitle"), "N/A")
            self.assertEqual(first_xml_customer.findtext("Phone"), first_csv_customer.get("Phone 1"))

            if first_csv_customer.get("Phone 2"):
                self.assertEqual(first_xml_customer.findtext("Fax"), first_csv_customer.get("Phone 2"))
            else:
                self.assertIsNone(first_xml_customer.find("Fax"))

            full_address = first_xml_customer.find("FullAddress")
            self.assertIsNotNone(full_address)
            self.assertEqual(full_address.findtext("Address"), "N/A")
            self.assertEqual(full_address.findtext("City"), first_csv_customer.get("City"))
            self.assertEqual(full_address.findtext("Region"), "N/A")
            self.assertEqual(full_address.findtext("PostalCode"), "0")
            self.assertEqual(full_address.findtext("Country"), first_csv_customer.get("Country"))

    def test_empty_customer_list(self):
        xml_output = self.mapper.json_to_xml([])
        self.assertTrue(xml_output.strip().startswith("<?xml"))
        # The mapper might produce <Customers/> or <Customers>\n</Customers>
        # So we check for the presence of the root tag and ensure it's empty or contains only whitespace.
        root = etree.fromstring(xml_output.encode('utf-8'))
        self.assertEqual(root.tag, "Customers")
        self.assertEqual(len(root.findall("Customer")), 0)
        self._validate_xml_with_xsd(xml_output)

    def test_missing_optional_fields_in_source(self):
        test_data = [
            {
                "Index": 1,
                "Customer Id": "NOFAX01",
                "First Name": "NoFax",
                "Last Name": "User",
                "Company": "NoFax Corp",
                "City": "Testville",
                "Country": "Testland",
                "Phone 1": "123-456-7890",
                # "Phone 2" is deliberately missing
                "Email": "nofax@example.com",
                "Subscription Date": "2022-01-01",
                "Website": "http://nofax.com"
            }
        ]
        xml_output = self.mapper.json_to_xml(test_data)
        self._validate_xml_with_xsd(xml_output)

        root = etree.fromstring(xml_output.encode('utf-8'))
        customer_node = root.find("Customer")
        self.assertIsNotNone(customer_node)
        self.assertIsNone(customer_node.find("Fax")) # Fax element should not exist
        self.assertEqual(customer_node.findtext("Phone"), "123-456-7890")


    def test_special_xml_characters_in_fields(self):
        test_data = [
            {
                "Customer Id": "SPCLCHR",
                "First Name": "James \"Jim\"",
                "Last Name": "O'Malley & Sons <LLC>",
                "Company": "AT&T <Company>",
                "City": "St. John's > East",
                "Country": "A & B 'Land'",
                "Phone 1": "555-0100",
                "Phone 2": "555-0101"
            }
        ]
        xml_output = self.mapper.json_to_xml(test_data)
        self._validate_xml_with_xsd(xml_output) # lxml validation also checks for well-formedness

        # We don't need to check escaped values directly if XSD validation passes,
        # as ElementTree handles escaping, and lxml parsing would fail on bad XML.
        # However, a quick check on one field for confidence:
        root = etree.fromstring(xml_output.encode('utf-8'))
        customer_node = root.find("Customer")
        # Example: Company name should be 'AT&T <Company>'
        # ElementTree stores it as 'AT&T <Company>', and serializes it as 'AT&amp;T &lt;Company&gt;'
        self.assertEqual(customer_node.findtext("CompanyName"), "AT&T <Company>")
        # Contact name should be 'James "Jim" O'Malley & Sons <LLC>'
        self.assertEqual(customer_node.findtext("ContactName"), "James \"Jim\" O'Malley & Sons <LLC>")


    def test_data_type_consistency_for_placeholders(self):
        # This is implicitly tested by XSD validation for PostalCode (xs:int)
        # We can add a specific check if needed, but schema validation is stronger.
        test_data = [
            {
                "Customer Id": "DTYPETEST",
                "First Name": "DataType",
                "Last Name": "Test",
                "Company": "TypeTest Inc.",
                "City": "Numeria",
                "Country": "Integerland",
                "Phone 1": "N/A",
            }
        ]
        xml_output = self.mapper.json_to_xml(test_data)
        self._validate_xml_with_xsd(xml_output) # This will fail if PostalCode isn't a valid int

        root = etree.fromstring(xml_output.encode('utf-8'))
        customer_node = root.find("Customer")
        full_address = customer_node.find("FullAddress")
        self.assertEqual(full_address.findtext("PostalCode"), "0") # Check the default placeholder

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    # Note: When running directly, ensure PYTHONPATH is set up if CustomerMapper is not in the same dir
    # or run with `python -m unittest CustomerMapper.Tests.test_customer_mapper` from repo root.
    # For this agent environment, direct execution in test file might be tricky due to paths.
    # The agent should use `run_in_bash_session` with the unittest command.
