import pandas as pd
import re
import sys
from pathlib import Path

def is_valid_stacks_address(address):
    """
    Validate Stacks address format:
    - Starts with SP or ST
    - Followed by exactly 38 characters
    - Characters are base58 (no 0, O, I, l)
    """
    if not isinstance(address, str):
        return False
    
    # Remove any whitespace
    address = address.strip()
    
    # Check length (should be 40 total: SP/ST + 38 chars)
    if len(address) != 40:
        return False
    
    # Check prefix
    if not (address.startswith('SP') or address.startswith('ST')):
        return False
    
    # Check if remaining 38 characters are valid base58
    # Base58 alphabet excludes 0, O, I, l to avoid confusion
    base58_pattern = r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{38}$'
    remaining_chars = address[2:]
    
    return bool(re.match(base58_pattern, remaining_chars))

def generate_clarity_test(addresses, output_path):
    """
    Generate Clarity contract with all addresses for validation
    """
    clarity_code = [
        ";; Address validation test contract",
        ";; Generated from CSV - malformed addresses will show red underlines",
        "",
        "(define-public (validate-all-addresses)",
        "  (begin"
    ]
    
    # Add each address as a print statement
    for i, address in enumerate(addresses):
        clarity_code.append(f"    (print '{address}) ;; Address {i+1}")
    
    clarity_code.extend([
        "    (ok true)",
        "  )",
        ")",
        "",
        "(define-public (test-transfers)",
        "  (begin"
    ])
    
    # Add transfer calls (commented out)
    for i, address in enumerate(addresses):
        clarity_code.append(f"    ;; (try! (contract-call? 'SPV9K21TBFAK4KNRJXF5DFP8N7W46G4V9RCJDC22.b-faktory transfer u1000000 tx-sender '{address} none)) ;; Address {i+1}")
    
    clarity_code.extend([
        "    (ok true)",
        "  )",
        ")",
        "",
        f";; Total addresses: {len(addresses)}"
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(clarity_code))
    
    print(f"Clarity contract generated: {output_path}")

def validate_csv_addresses(csv_path):
    """
    Validate addresses from CSV file
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_path, header=None, names=['address'])
        print(f"Loaded {len(df)} addresses from CSV")
        
        # Remove any NaN values and strip whitespace
        df = df.dropna()
        df['address'] = df['address'].astype(str).str.strip()
        
        # Remove duplicates
        original_count = len(df)
        df = df.drop_duplicates(subset=['address'])
        duplicates_removed = original_count - len(df)
        print(f"Removed {duplicates_removed} duplicate addresses")
        print(f"Unique addresses: {len(df)}")
        
        # Generate Clarity contract with all addresses
        generate_clarity_test(df['address'].tolist(), 'contracts/address-validator.clar')
        
        return df['address'].tolist()
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/validate_addresses.py <csv_file_path>")
        return
    
    csv_path = sys.argv[1]
    
    if not Path(csv_path).exists():
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    print(f"Processing: {csv_path}")
    print("-" * 50)
    
    addresses = validate_csv_addresses(csv_path)
    
    print(f"\n{'='*50}")
    print(f"Generated Clarity contract with {len(addresses)} addresses")
    print(f"Run 'clarinet check' to validate all addresses")

if __name__ == "__main__":
    main()