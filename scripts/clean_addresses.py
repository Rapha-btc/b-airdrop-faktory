import pandas as pd
import sys
from pathlib import Path

def is_contract_address(address):
    """Check if address contains a dot (contract address)"""
    return '.' in address

def is_burn_address(address):
    """Check if address is the burn address"""
    return address == "SP000000000000000000002Q6VF78"

def generate_airdrop_contract(addresses, output_path):
    """Generate Clarity contract with airdrop function"""
    clarity_code = [
        "(define-public (test-transfers)",
        "  (begin"
    ]
    
    for address in addresses:
        clarity_code.append(f"    (try! (contract-call? 'SPV9K21TBFAK4KNRJXF5DFP8N7W46G4V9RCJDC22.b-faktory transfer u1000000 tx-sender '{address} none))")
    
    clarity_code.extend([
        "    (ok true)",
        "  )",
        ")"
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(clarity_code))

def clean_addresses(csv_path):
    """Clean addresses from CSV"""
    try:
        df = pd.read_csv(csv_path, header=None, names=['address'])
        
        # Remove NaN and strip whitespace
        df = df.dropna()
        df['address'] = df['address'].astype(str).str.strip()
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['address'])
        
        # Filter out contract addresses (contain dots)
        df = df[~df['address'].apply(is_contract_address)]
        
        # Filter out burn address
        df = df[~df['address'].apply(is_burn_address)]
        
        addresses = df['address'].tolist()
        
        # Generate Clarity contract
        generate_airdrop_contract(addresses, 'contracts/address-validator.clar')
        
        return addresses
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        return
    
    csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        return
    
    addresses = clean_addresses(csv_path)
    print(f"Generated contract with {len(addresses)} clean addresses")

if __name__ == "__main__":
    main()