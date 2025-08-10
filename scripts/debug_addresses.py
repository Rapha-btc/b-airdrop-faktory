import pandas as pd
import re
import sys
from pathlib import Path

def is_valid_stacks_address(address):
    """Validate Stacks address format"""
    if not isinstance(address, str):
        return False
    
    address = address.strip()
    
    if len(address) != 40:
        return False
    
    if not (address.startswith('SP') or address.startswith('ST')):
        return False
    
    base58_pattern = r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{38}$'
    remaining_chars = address[2:]
    
    return bool(re.match(base58_pattern, remaining_chars))

def is_contract_address(address):
    """Check if address contains a dot (contract address)"""
    return '.' in address

def is_burn_address(address):
    """Check if address is the burn address"""
    return address == "SP000000000000000000002Q6VF78"

def debug_addresses(csv_path):
    """Debug what's happening to the addresses"""
    try:
        df = pd.read_csv(csv_path, header=None, names=['address'])
        print(f"1. Initial load: {len(df)} addresses")
        
        # Show first 10 addresses
        print("\nFirst 10 addresses:")
        for i, addr in enumerate(df['address'].head(10)):
            print(f"  {i+1}: '{addr}'")
        
        # Remove NaN and strip whitespace
        df = df.dropna()
        df['address'] = df['address'].astype(str).str.strip()
        print(f"2. After removing NaN and stripping: {len(df)} addresses")
        
        # Check for duplicates
        original_count = len(df)
        df_no_dups = df.drop_duplicates(subset=['address'])
        duplicates_removed = original_count - len(df_no_dups)
        print(f"3. Duplicates found: {duplicates_removed}")
        print(f"4. After removing duplicates: {len(df_no_dups)} addresses")
        
        # Check contract addresses
        contract_addresses = df_no_dups[df_no_dups['address'].apply(is_contract_address)]
        print(f"5. Contract addresses (with dots): {len(contract_addresses)}")
        if len(contract_addresses) > 0:
            print("   Examples:")
            for addr in contract_addresses['address'].head(5):
                print(f"     {addr}")
        
        df_no_contracts = df_no_dups[~df_no_dups['address'].apply(is_contract_address)]
        print(f"6. After removing contracts: {len(df_no_contracts)} addresses")
        
        # Check burn address
        burn_addresses = df_no_contracts[df_no_contracts['address'].apply(is_burn_address)]
        print(f"7. Burn addresses found: {len(burn_addresses)}")
        
        df_no_burn = df_no_contracts[~df_no_contracts['address'].apply(is_burn_address)]
        print(f"8. After removing burn address: {len(df_no_burn)} addresses")
        
        # Check valid format
        valid_addresses = df_no_burn[df_no_burn['address'].apply(is_valid_stacks_address)]
        invalid_addresses = df_no_burn[~df_no_burn['address'].apply(is_valid_stacks_address)]
        
        print(f"9. Valid format addresses: {len(valid_addresses)}")
        print(f"10. Invalid format addresses: {len(invalid_addresses)}")
        
        if len(invalid_addresses) > 0:
            print("\nInvalid addresses examples:")
            for addr in invalid_addresses['address'].head(10):
                print(f"  '{addr}' - length: {len(addr)}")
        
        return len(valid_addresses)
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/debug_addresses.py <csv_file_path>")
        return
    
    csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    debug_addresses(csv_path)

if __name__ == "__main__":
    main()