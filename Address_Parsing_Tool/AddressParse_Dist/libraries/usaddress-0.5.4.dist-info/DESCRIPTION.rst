usaddress is a python library for parsing unstructured address strings into address components, using advanced NLP methods.

>From the python interpreter:

>>> import usaddress
>>> usaddress.parse('123 Main St. Suite 100 Chicago, IL')
[('123', 'AddressNumber'), 
 ('Main', 'StreetName'), 
 ('St.', 'StreetNamePostType'), 
 ('Suite', 'OccupancyType'), 
 ('100', 'OccupancyIdentifier'), 
 ('Chicago,', 'PlaceName'), 
 ('IL', 'StateName')]


