# -*- coding: utf-8 -*-
 
import json
import signalfx
 
 
SFX_TOKEN = '<censored>'
 
def pretty_json(data):
    """Generate pretty-printed JSON string from object.
 
   :param data: Object to convert to a JSON string
   :return: Pretty-printed JSON.
   :rtype: str
   """
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
 
 
def get_cassandra_goodness(product='cassandra_cluster', additional_filter=None):
    """Query for dimensions matching a query while defaulting to looking for Cassandra cluster names.
 
   :param product: (optional) Make sure this field exists in the results and generate a list of values for this field.
                   (default: 'cassandra_cluster')
   :type product: str`
   :param additional_filter: (optional) Additional query string to append to the original query. (default: None)
   :return: List of values.
   :rtype: list
   """
    query = '_exists_:ecosystem AND _exists_:{}'.format(product)
    if additional_filter:
        query += ' AND {}'.format(additional_filter)
 
    product_results = []
 
    with signalfx.SignalFx().rest(token=SFX_TOKEN) as sfx:
        sfx_results = sfx.search_dimensions(query=query)
        if not sfx_results:
            return None
 
        results = sfx_results.get('results')
        if not results:
            return None

        for result in results:
            key = result.get('key')
            val = result.get('value')
            if key == product and val:
                if val in product_results:
                    continue
                product_results.append(val)
                continue
 
            custom_properties = result.get('customProperties')
            if custom_properties:
                cp_product = custom_properties.get(product)
                if cp_product:
                    if cp_product in product_results:
                        continue
 
                    product_results.append(cp_product)
                    continue
 
            print('Found nothing interesting for: {}'.format(result))
    return sorted(product_results)
 
 
def main():
    main_results = get_cassandra_goodness(
        product='cassandra_cluster',
        additional_filter='ecosystem:prod'
    )
 
    print(pretty_json(main_results))
 
 
if __name__ == '__main__':
    main()
