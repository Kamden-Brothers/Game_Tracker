import json

class CredentialsException(Exception):
    pass

class LoadCredentials:
    def get_credential(search_key):
        with open('credentials.json') as f:
            cred_dict = json.load(f)
        if search_key not in cred_dict.keys():
            raise Exception(f'Could find key {search_key} in credentials.json')
        return cred_dict[search_key]

    def get_connection_credentials():
        with open('credentials.json') as f:
            cred_dict = json.load(f)
        if 'master_db' not in cred_dict.keys():
            raise CredentialsException('Could not find master_db in credentions.json')

        for key in ['username', 'password']:
            if key not in cred_dict['master_db']:
                raise CredentialsException('Could not find [master_db, {key}] in credentials.json')

        return cred_dict['master_db']
