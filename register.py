from opmentis import register_user

# Register as a miner
wallet_address = "0xee0495497e6847e3F85343B6474A0658c32F51dd"
labid = "dbc00e29-721f-40e6-b073-ec627db90115"
role_type = "validator"
register_response = register_user(wallet_address, labid, role_type)
print("Registration Response:", register_response)
